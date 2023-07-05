import zipfile
import os
import re
import glob
import logging
import argparse
import pathlib
import random
from pprint import pprint

import mosspy

logging.basicConfig(level=logging.DEBUG)

LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "java": ["java"],
    "cpp": [".cpp", ".h", ".hpp"],
}

DEFAULT_CANVAS_ZIP = "submissions.zip"
DEFAULT_ZIP_OUTPUT = "./zip_output"

user_id = os.getenv("user_id")
moss = mosspy.Moss(user_id=user_id, language="java")


def unzip_canvas_submission(canvas_zip, zip_output, original_name=False) -> None:
    """
    Unzip the Canvas submission folder and place them in a folder.
    Set `original_name` to `True` to keep student's ZIP file original name.
    This doesn't work consistently, notably with resubmissions.
    """
    with zipfile.ZipFile(canvas_zip, "r") as zf:
        for submission in zf.filelist:
            if original_name:
                folder_name = None
            else:
                folder_name = re.match(r"(\w+_\w*_\d+\d+)", submission.filename)
                folder_name = folder_name[0] if folder_name else None
            logging.debug(f"Extracting {folder_name}")

            b = zf.open(submission, "r")
            with zipfile.ZipFile(b) as student_zip:
                student_zip.extractall(path=os.path.join(zip_output, folder_name))


def stage_moss_files(zip_output, language: str = "", max_submissions=0):
    files = []
    submission_folders = []
    extensions = LANGUAGE_EXTENSIONS.get(language.lower(), [""])

    if max_submissions:
        folders = glob.glob(f"{zip_output}/*", recursive=True)
        random.shuffle(folders)
        submission_folders = folders[:max_submissions]
    else:
        submission_folders = [zip_output]

    for ext in extensions:
        for folder in submission_folders:
            files += glob.glob(f"{folder}/**/*{ext}", recursive=True)

    for f in files:
        if (
            os.path.isfile(f)
            and not f.endswith("pdf")
            and not f.endswith("jar")
            and os.path.getsize(f) > 0
        ):
            logging.debug(f"Adding {f} to MOSS")
            moss.addFile(f)

    pprint(files)
    moss.setDirectoryMode(1)


def send_to_moss():
    # progress function optional, run on every file uploaded
    # result is submission URL
    url = moss.send(lambda file_path, display_name: print("*", end="", flush=True))

    print()

    print("Report Url: " + url)

    # Save report file
    moss.saveWebPage(url, "./report.html")

    # Download whole report locally including code diff links
    mosspy.download_report(
        url,
        "./report",
        connections=8,
        log_level=10,
        on_read=lambda url: print("*", end="", flush=True),
    )
    # log_level=logging.DEBUG (20 to disable)
    # on_read function run for every downloaded file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Utility for unzipping Canvas submission and uploading files to MOSS."
    )

    parser.add_argument("zip_file", help="The submission ZIP file from Canvas.")
    parser.add_argument("language", help="Programming language for the assignment.")

    parser.add_argument(
        "--save-report",
        help="Save MOSS report to local machine.",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "--original-name",
        help="""
        Keep the submission's original name when unzipping.
        Note that this doesn't work consistently, notably with resubmissions.
        """,
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-n",
        "--max-submissions",
        metavar="n",
        help="Maximum number of submissions per batch.",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-r",
        "--repeat",
        metavar="n",
        help="Number of times to perform repeated submissions.",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-o",
        "--zip-output",
        metavar="path",
        help="Path to extract the submission ZIP file into.",
        default="./zip_output",
    )
    parser.add_argument(
        "-ro",
        "--report-output",
        metavar="path",
        help="Path to save the MOSS report.",
        default="./report",
    )

    return parser.parse_args()


if __name__ == "__main__":
    stage_moss_files(DEFAULT_ZIP_OUTPUT, "java")
    pass

    # unzip_canvas_submission()
    # stage_moss_files("")

    # pprint(moss.__dict__)
