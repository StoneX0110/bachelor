import os
import re

# PdfAct https://github.com/ad-freiburg/pdfact
# read-in PDF file and convert to TXT
jarDir = os.getcwd().removesuffix('src') + 'pdfact\\bin\\pdfact.jar'

inputDir = input("Enter a path to the PDF file (please use backslashes '\\', not slashes!): ")
while not os.path.exists(inputDir):
    print("File could not be found at " + str(inputDir))
    inputDir = input("Please enter a valid path: ")

outputDir = input("Enter a path for the output file to be stored at (please use backslashes '\\', not slashes!): ")
while not os.path.exists(outputDir):
    print("File could not be found at " + str(outputDir))
    outputDir = input("Please enter a valid path: ")
outputDir += '\\' + input("Enter name of output file: ") + '.txt'

print("Converting PDF to plain text...")

os.system('java -jar ' + jarDir + ' ' + inputDir + ' output.txt' + ' --include body')

print("Finished conversion, removing noise...")

input_file = open('output.txt', encoding='UTF-8')
output = open(outputDir, 'w', encoding='UTF-8')

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
