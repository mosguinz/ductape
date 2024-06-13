import argparse
import glob
import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pprint import pprint

import requests

# For messaging feature, set Canvas token here or in your environment variable.
CANVAS_TOKEN = "1234"


@dataclass
class Compliance:
    zip_name_compliant: bool = None
    report_name_compliant: bool = None
    folders_compliant: bool = None

    zip_name: str = None
    report_name: str = None
    folder_structure: str = None

    def __bool__(self):
        return all((self.folders_compliant, self.report_name_compliant, self.zip_name_compliant))


@dataclass
class Student:
    name: str
    canvas_id: str
    sis_id: str
    compliance: Compliance

    def __hash__(self):
        return hash(self.sis_id)


def cleanup_files(path):
    """Currently just removes __MACOSX folders."""
    macos_folders = glob.glob(f"{path}/**/__MACOSX", recursive=True)
    for f in macos_folders:
        shutil.rmtree(f)


def check_folders(parts: list[str], temp_dir: str) -> bool:
    """
    Check if the provided directory contains the required folders for the given parts.

    Per policy, students are required to have folders in the form "Part_X" for their solutions.
    Attempts to find the given folders in such a format, ignoring case and punctuations.
    """
    folders = glob.glob(f"{temp_dir}/**/*/", recursive=True)
    for part in sorted(parts):
        found = False
        for folder in folders:
            if re.search(rf"part.*{part}/", folder, re.IGNORECASE):
                found = True
                break
        if not found:
            return False
    return True


def check_report(temp_dir: str) -> bool:
    """Checks if the submissions contains a report, and whether it loosely conforms to the naming format."""
    pdfs = glob.glob(f"{temp_dir}/**/*.pdf", recursive=True)
    for pdf in pdfs:
        if re.search(r"assignment.+report", pdf, re.IGNORECASE):
            return True
    return False


def check_zipfile(canvas_zip, parts: list[str] = None, report=True, debug=True):
    students = []

    with zipfile.ZipFile(canvas_zip, "r") as zf:
        for submission in zf.infolist():
            res = re.match(r"([^\W_]+)(?:_\w+)*_(\d+)_(\d+)_(.+)", submission.filename)
            original_filename = res[4]
            compliance = Compliance()
            compliance.zip_name = original_filename

            if re.match(r"\w+-Assignment-\w+(-\d)?\.zip", original_filename):
                compliance.zip_name_compliant = True
            else:
                compliance.zip_name_compliant = False

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zf.open(submission)) as student_zip:
                    student_zip.extractall(temp_dir)
                    cleanup_files(temp_dir)

                    if parts:
                        compliance.folders_compliant = check_folders(parts, temp_dir)
                    if report:
                        compliance.report_name_compliant = check_report(temp_dir)

            student = Student(name=res[1], canvas_id=res[2], sis_id=res[3], compliance=compliance)
            students.append(student)

    return students
    # pprint({k: v for k, v in compliance.items() if not v.report})


def send_message(assignment_name: str, parts: list[str], student: Student, canvas_token=None, debug=True):
    canvas_token = canvas_token or os.getenv("CANVAS_TOKEN") or CANVAS_TOKEN
    if not canvas_token:
        raise ValueError("No Canvas token found")
    messages = [
        "You are receiving this message because an automated check has found that your submission may not be "
        "compliant with the grading policy.",
        f"Your submission for Assignment {assignment_name} may receive a zero for one or more of the following "
        "reasons:\n",
    ]

    if student.compliance.zip_name_compliant is False:
        messages.append(
            "  - Your submission ZIP file is not named correctly. It should be in the format: "
            f"FirstLast-Assignment-{assignment_name}.zip"
        )
    if student.compliance.folders_compliant is False:
        if len(parts) > 2:
            s = ", ".join(parts[:-1])
            s += ", and " + parts[-1]
        else:
            s = " and ".join(parts)
        messages.append(
            f"  - Your submission do not appear to contain folders for one or more of the following parts: {s}."
        )
    if student.compliance.report_name_compliant is False:
        messages.append(
            f"  - Your assignment report is not named correctly. Your report should be in the format: "
            f"FirstLast-Assignment-{assignment_name}-Report.pdf"
        )

    messages.append(
        "\nBe sure to update your submission before the deadline to avoid penalties. Failure to do so may "
        "result in a zero for some or all parts of the assignment."
    )
    messages.append("This is an automated check. If you believe this message was sent in error, please let us know.")
    body = "\n".join(messages)
    print(body)

    data = {
        "recipients": student.canvas_id,
        "body": body,
        "subject": f"Courtesy Notice: Assignment {assignment_name} format",
        "force_new": True,
        "group_conversation": False,
    }

    if debug:
        data["recipients"] = [os.getenv("MY_CANVAS_ID")]

    with requests.post(
            url="https://sfsu.instructure.com/api/v1/conversations",
            headers={"Authorization": f"Bearer {canvas_token}"},
            data=data,
    ) as req:
        pprint(req.headers)
        pprint(req.json())


def parse_args():
    parser = argparse.ArgumentParser(description="Utility for checking student's submission format.")

    parser.add_argument("zip_file", help="The submission ZIP file from Canvas.")
    parser.add_argument("-a", "--asmt", help="The assignment name.", required=True)
    parser.add_argument("-r", "--report", help="Whether a report is required.", action="store_true", default=True)
    parser.add_argument("-p", "--parts", help="Required folders to be present.", nargs="+")
    parser.add_argument(
        "-m",
        "--send_message",
        help="If set, a message will be sent to students with non-compliant submissions.",
        action="store_true",
        default=False,
    )

    return parser.parse_args()


def display_students(students):
    good, bad = [], []
    for student in students:
        good.append(student) if student.compliance else bad.append(student)

    tick = "\033[42m ✔ \033[0m"  # Green background check mark
    cross = "\033[41m ✘ \033[0m"  # Red background cross mark

    # Table headers
    headers = ["Name", "Canvas ID", "Filename", "Z", "R", "F"]
    rows = []

    # Prepare rows for printing
    for student in *bad, *good:
        row = [
            student.name,
            student.canvas_id,
            student.compliance.zip_name,
            tick if student.compliance.zip_name_compliant else cross,
            tick if student.compliance.report_name_compliant else cross,
            tick if student.compliance.folders_compliant else cross,
        ]
        rows.append(row)

    # Find maximum column widths for pretty printing
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*[headers] + rows)]
    col_widths[-3:] = 3, 3, 3  # fixed size for last three columns to ignore ANSI codes

    # Print summary
    print(f"{len(students)} submissions: {len(good)} compliant, {len(bad)} non-compliant.")
    print("Displaying non-compliant submissions first.")
    print("Z = ZIP file name compliance")
    print("R = Report name compliance")
    print("F = Required folder(s) compliance")
    print()

    # Print headers
    header_str = " | ".join(
        f"{headers[i]:<{col_widths[i]}}" if i < 3 else f"{headers[i]:^{col_widths[i]}}" for i in range(len(headers))
    )
    print(header_str)
    print("-" * len(header_str))

    # Print each row
    for row in rows:
        row_str = " | ".join(
            f"{row[i]:<{col_widths[i]}}" if i < 3 else f"{row[i]:^{col_widths[i]}}" for i in range(len(row))
        )
        print(row_str)


def main():
    opt = parse_args()
    pprint(opt)

    students = check_zipfile(canvas_zip=opt.zip_file, parts=opt.parts, report=opt.report)

    display_students(students)
