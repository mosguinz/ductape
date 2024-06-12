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
    folders: bool = None
    report_name: bool = None
    zipfile_name: bool = None

    def __bool__(self):
        return all((self.folders, self.report_name, self.zipfile_name))


@dataclass
class Student:
    name: str
    canvas_id: str
    sis_id: str
    filename: str
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

            if re.match(r"\w+-Assignment-\w+(-\d)?\.zip", original_filename):
                compliance.zipfile_name = True
            else:
                compliance.zipfile_name = False

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zf.open(submission)) as student_zip:
                    student_zip.extractall(temp_dir)
                    cleanup_files(temp_dir)

                    if parts:
                        compliance.folders = check_folders(parts, temp_dir)
                    if report:
                        compliance.report_name = check_report(temp_dir)

            student = Student(
                name=res[1], canvas_id=res[2], sis_id=res[3], filename=original_filename, compliance=compliance
            )
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

    if student.compliance.zipfile_name is False:
        messages.append(
            "  - Your submission ZIP file is not named correctly. It should be in the format: "
            f"FirstLast-Assignment-{assignment_name}.zip"
        )
    if student.compliance.folders is False:
        if len(parts) > 2:
            s = ", ".join(parts[:-1])
            s += ", and " + parts[-1]
        else:
            s = " and ".join(parts)
        messages.append(
            f"  - Your submission do not appear to contain folders for one or more of the following parts: {s}."
        )
    if student.compliance.report_name is False:
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


def main():
    parts = ["C", "D"]
    students = check_zipfile("submissions.zip", parts)
    for student in students:
        if not student.compliance:
            pprint(student)
            # send_message("01", parts, student)
