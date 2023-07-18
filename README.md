# mos-moss

## Requirements

* Python 3.10+
* `pip install mosspy`
* Set `MOSS_ID` at the top of `mos_moss.py` file.
  * Or set your environment variable `MOSS_ID`.
  * Or supply the ID using `-i` at runtime.

## Usage

Minimal usage: specify ZIP file name and programming language. Unzips submissions in `submissions.zip` and sends all files to MOSS for processing.

```sh
python mos_moss.py submissions.zip language
```
After running, check log file for MOSS links.

For help:
```sh
python mos_moss.py -h
```

### Examples

```sh
python mos_moss.py submissions.zip cpp -s online_solutions -b starters -n 20 -r 5
```

```sh
python mos_moss.py submissions.zip cpp -s online_solutions -b starters -n 20 -r 5 --original-name --verbose
```

---

```
usage: mos_moss.py [-h] [--no-report] [--original-name] [--verbose] [-n n] [-r n] [-o path] [-ro path] [-b path]
                   [-s path] [-i id]
                   zip_file language

Utility for unzipping Canvas submission and uploading files to MOSS.

positional arguments:
  zip_file              The submission ZIP file from Canvas.
  language              Programming language for the assignment.

options:
  -h, --help            show this help message and exit
  --no-report           Do not save MOSS report to local machine.
  --original-name       Keep the submission's original name when unzipping. Note that this doesn't work
                        consistently, notably with resubmissions.
  --verbose             Log everything.
  -n n, --max-submissions n
                        Maximum number of submissions per batch.
  -r n, --repeat n      Number of times to perform repeated submissions.
  -o path, --zip-output path
                        Path to extract the submission ZIP file into.
  -ro path, --report-output path
                        Path to save MOSS report(s).
  -b path, --base-files path
                        Path to base files provided by the instructor, such as starter code. Helps MOSS filter
                        boilerplates that are common throughout submissions.
  -s path, --solutions path
                        Path to online solutions to check against. This will be sent to MOSS alongside student's
                        submissions. Bypasses maximum number of submissions, if supplied.
  -i id, --moss-id id   MOSS ID to use when submitting request to MOSS. If supplied, this value will be used over
                        the value set for the `MOSS_ID` variable at the top of the file or in the environment
                        variables.
```
