# bachelor

## Required programs
The program has been developed and tested with Java 12.0.1 and Python 3.9.1.

## Install
```
git clone https://github.com/StoneX0110/bachelor
```

## Usage
Run Main.py from anywhere with the following arguments:
1. the path to the pdf file that should be processed
2. the directory where the output files should be stored at
3. optional: the granularity of the splitting

Important: to avoid any errors, enter paths with slashes, not backslashes
```
usage: Main.py [-h] [--granularity {chapter,section,article}] input_file output_path

positional arguments:
  input_file            path to pdf file
  output_path           path to output directory

optional arguments:
  -h, --help            show this help message and exit
  --granularity {chapter,section,article}, -g {chapter,section,article}
                        granularity of splitting
```

Example (Windows):
```
py C:/Users/USER/bachelor/src/Main.py C:/Users/USER/Documents/pdf_document.pdf C:/Users/USER/Documents/Output -granularity article
```
This would process `pdf_document.pdf`, split it by its articles and store the output files in `C:/Users/USER/Documents/Output`
