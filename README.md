# mos-moss

## Requirements

* Python 3.10+
* `pip install mosspy`

## Usage

Minimally usage: specify ZIP file name and programming language. Unzips submissions in `submissions.zip` and sends all files to MOSS for processing.

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
