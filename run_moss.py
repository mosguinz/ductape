import zipfile
import os
import re
import glob
import logging
from pprint import pprint

import mosspy

logging.basicConfig(level=logging.DEBUG)

LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "java": ["java"],
    "cpp": [".cpp", ".h", ".hpp"],
}

canvas_zip = "submissions.zip"
zip_output = "./zip_output"

user_id = os.getenv("user_id")
moss = mosspy.Moss(user_id=user_id, language="java")


def unzip_canvas_submission(original_name=False) -> None:
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


def stage_moss_files(language: str = ""):
    files = []
    extensions = LANGUAGE_EXTENSIONS.get(language.lower(), [""])

    for ext in extensions:
        files += glob.glob(f"{zip_output}/**/*{ext}", recursive=True)
    for f in files:
        if (
            os.path.isfile(f)
            and not f.endswith("pdf")
            and not f.endswith("jar")
            and os.path.getsize(f) > 0
        ):
            logging.debug(f"Adding {f} to MOSS")
            moss.addFile(f)

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


if __name__ == "__main__":
    unzip_canvas_submission()
    stage_moss_files("")

    pprint(moss.__dict__)
