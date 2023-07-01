import zipfile

import mosspy

submission_zip = "submissions.zip"
zip_output = "./zip_output"

with zipfile.ZipFile(submission_zip, "r") as f:
    f.extractall(zip_output)

