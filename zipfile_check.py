import shutil
import zipfile
import re
import glob
import tempfile

from dataclasses import dataclass
from pprint import pprint


@dataclass
class Student:
    name: str
    canvas_id: str
    sis_id: str
    filename: str

    def __hash__(self):
        return hash(self.sis_id)


@dataclass
class Compliance:
    folders: bool = None
    report: bool = None


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


def check_zipfile(canvas_zip, parts: list[str] = None, report=True):
    compliance = {}
    with zipfile.ZipFile(canvas_zip, "r") as zf:
        for submission in zf.infolist():
            res = re.match(r"([^\W_]+)(?:_\w+)*_(\d+)_(\d+)_(.+)", submission.filename)
            student = Student(*res.groups())
            compliance[student] = Compliance()

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zf.open(submission)) as student_zip:
                    student_zip.extractall(temp_dir)
                    cleanup_files(temp_dir)

                    if parts:
                        compliance[student].folders = check_folders(parts, temp_dir)
                    if report:
                        compliance[student].report = check_report(temp_dir)

    pprint({k: v for k, v in compliance.items() if not v.report})


def send_message():
    pass
