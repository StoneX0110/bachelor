# bachelor

## Required programs
The program has been developed and tested with Java 12.0.1 and Python 3.9.1.

## Installation
Clone project
```
git clone https://github.com/StoneX0110/bachelor
```
Install dependencies
```
pip install -r requirements.txt
```

## Usage
### 1. Main
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
python C:/Users/USER/bachelor/src/Main.py C:/Users/USER/Documents/pdf_document.pdf C:/Users/USER/Documents/Output -granularity article
```
This would process `pdf_document.pdf`, split it by its articles and store the output files at `C:/Users/USER/Documents/Output`

### 2. Web Service
Run Web.py from anywhere with the following arguments:
1. the path to the folder where the processed files should be temporarily stored at

Important: to avoid any errors, enter paths with slashes, not backslashes
```
usage: Web.py [-h] data_storage

positional arguments:
  data_storage  path to directory where user files will be stored at

optional arguments:
  -h, --help    show this help message and exit
```

Example (Windows):
```
python C:/Users/USER/bachelor/src/Web.py C:/Users/USER/Documents/Web_Service_Storage
```
This would start the web service (available at localhost with port 1337) and temporarily store the processed files at `C:/Users/USER/Documents/Web_Service_Storage`
