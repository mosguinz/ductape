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
python mos_moss.py submissions.zip java
```
After running, check log file for MOSS links.

For help:
```sh
python mos_moss.py -h
```

### Examples

```sh
python mos_moss.py submissions.zip cpp -s Online_solutions -b starters -n 20 -r 5
```

```sh
python mos_moss.py submissions.zip cpp -s Online_solutions -b starters -n 20 -r 5 --original-name --verbose
```
