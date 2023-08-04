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


def check_folders(parts: list[str], temp_dir: str) -> bool:
    """
    Check if the provided directory contains the required folders for the given parts.

    Per policy, students are required to have folders in the form "Part_X" for their solutions.
    Attempts to find the given folders in such a format, ignoring case and punctuations.
    """
    macos_folders = glob.glob(f"{temp_dir}/**/__MACOSX", recursive=True)
    for f in macos_folders:
        shutil.rmtree(f)

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


def check_zipfile(canvas_zip, parts: list[str] = None):
    students = {}
    with zipfile.ZipFile(canvas_zip, "r") as zf:
        for submission in zf.infolist():
            res = re.match(r"([^\W_]+)(?:_\w+)*_(\d+)_(\d+)_(.+)", submission.filename)
            student = Student(*res.groups())

            students[student] = Compliance()
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zf.open(submission)) as student_zip:
                    student_zip.extractall(temp_dir)
                    students[student].folders = check_folders(parts, temp_dir)

    pprint({k: v for k, v in students.items() if not v.folders})


def send_message():
    pass
