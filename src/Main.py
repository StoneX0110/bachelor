import os
import re

# PdfAct https://github.com/ad-freiburg/pdfact
# read-in PDF file and convert to TXT
jarDir = os.getcwd().removesuffix('src') + 'pdfact\\bin\\pdfact.jar'
inputDir = 'C:\\Users\\Patrick\\Desktop\\dsgvo.pdf'  # TODO User prompt?
outputDir = 'C:\\Users\\Patrick\\Desktop\\output.txt'  # TODO User prompt?
os.system('java -jar ' + jarDir + ' ' + inputDir + ' ' + outputDir + ' --include body')

input_file = open('C:\\Users\\Patrick\\Desktop\\text.txt', encoding='UTF-8')
output = open('output.txt', 'w', encoding='UTF-8')

for line in input_file:
    if line != '\n':
        # look for enumeration at the start
        match = re.match('\([0-9]+\)', line)
        if match:
            # remove starting enumeration and following empty space
            line = line.removeprefix(match.group(0))[1:]
    output.write(line)

input_file.close()
output.close()
