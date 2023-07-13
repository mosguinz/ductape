import zipfile
import os
import re
import glob
import logging
import argparse
import pathlib
import itertools
import shutil
import random
from pprint import pprint

import mosspy

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "java": ["java"],
    "cpp": [".cpp", ".h", ".hpp"],
}

DEFAULT_CANVAS_ZIP = "submissions.zip"
DEFAULT_ZIP_OUTPUT = "./zip_output"

## TODO: online solutions and basefile


def cleanup_files(path):
    """Currently just removes __MACOSX folders."""
    macos_folders = glob.glob(f"{path}/**/__MACOSX", recursive=True)
    for f in macos_folders:
        shutil.rmtree(f)


def flatten_folder(destination):
    """Flatten folders containing a single folder."""
    content = os.listdir(destination)
    if len(content) == 1:
        folder = os.path.join(destination, content[0])

        log.debug(f"Flattening {folder}")
        for f in os.listdir(folder):
            shutil.move(os.path.join(folder, f), destination)
        os.rmdir(folder)


def unzip_canvas_submission(canvas_zip, zip_output, original_name=False) -> None:
    """
    Unzip the Canvas submission folder and place them in a folder.
    Set `original_name` to `True` to keep student's ZIP file original name.
    This doesn't work consistently, notably with resubmissions.
    """
    with zipfile.ZipFile(canvas_zip, "r") as zf:
        for submission in zf.infolist():
            # [last][first]_[int]_[int]_[original_filename]
            res = re.match(r"(\w+_\w*_\d+\d+)_(.+)\.", submission.filename)
            try:
                folder_name = res[2] if original_name else res[1]
            except TypeError:
                folder_name = submission.filename

            # log.debug(f"Extracting {folder_name}")

            b = zf.open(submission, "r")
            with zipfile.ZipFile(b) as student_zip:
                path = os.path.join(zip_output, folder_name)
                student_zip.extractall(path=path)
                cleanup_files(path)
                flatten_folder(path)


def stage_moss_files(
    zip_output,
    language: str = "",
    max_submissions=0,
    base_files=None,
    solutions=None,
) -> mosspy.Moss:
    moss = mosspy.Moss(user_id=None, language=language)

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
            log.debug(f"Adding {f} to MOSS")
            moss.addFile(f)

    if base_files:
        files = glob.glob(f"{base_files}/**/*", recursive=True)
        if not files:
            raise FileNotFoundError(f"{base_files} returned no matches for base files")
        for f in files:
            moss.addBaseFile(f)

    if solutions:
        files = glob.glob(f"{solutions}/**/*", recursive=True)
        if not files:
            raise FileNotFoundError(
                f"{base_files} returned no matches for online solutions"
            )
        for f in files:
            moss.addFile(f)

    moss.setDirectoryMode(1)
    pprint(moss.__dict__)

    return moss


def send_to_moss(moss: mosspy.Moss, user_id=None, no_report=False):
    moss.user_id = user_id or os.getenv("user_id")

    url = moss.send(lambda file_path, _: log.debug(f"Uploading: {file_path}"))
    log.info("Report URL: " + url)

    log.info("Saving report page")
    moss.saveWebPage(url, "./report.html")

    if no_report:
        return

    log.info("Downloading report")
    mosspy.download_report(url, "./report", connections=8, log_level=log.level)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Utility for unzipping Canvas submission and uploading files to MOSS."
    )

    parser.add_argument("zip_file", help="The submission ZIP file from Canvas.")
    parser.add_argument("language", help="Programming language for the assignment.")

    parser.add_argument(
        "--no-report",
        help="Do not save MOSS report to local machine.",
        action="store_true",
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
    parser.add_argument(
        "-b",
        "--base-files",
        metavar="path",
        help="""
        Path to base files provided by the instructor, such as starter code.
        Helps MOSS filter boilerplates that are common throughout submissions.
        """,
    )
    parser.add_argument(
        "-s",
        "--solutions",
        metavar="path",
        help="""
        Path to online solutions to check against.
        This will be sent to MOSS alongside student's submissions.
        Bypasses maximum number of submissions, if supplied.
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    opt = parse_args()
    pprint(opt.__dict__)

    unzip_canvas_submission(
        canvas_zip=opt.zip_file,
        zip_output=opt.zip_output,
        original_name=opt.original_name,
    )
    moss = stage_moss_files(
        zip_output=opt.zip_output,
        language=opt.language,
        max_submissions=opt.max_submissions,
        base_files=opt.base_files,
        solutions=opt.solutions,
    )
    # send_to_moss(moss, no_report=opt.no_report)
