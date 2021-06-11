import os
import re

# PdfAct https://github.com/ad-freiburg/pdfact

# directory of pdfact.jar
jarDir = os.getcwd().removesuffix('src') + 'pdfact\\bin\\pdfact.jar'

# directory of pdf to be converted, asked in user prompt
inputDir = input("Enter a path to the PDF file (please use backslashes '\\', not slashes!): ")
while not os.path.exists(inputDir):
    print("File could not be found at " + str(inputDir))
    inputDir = input("Please enter a valid path: ")

# directory of output to be stored at, asked in user prompt
outputDir = input("Enter a path for the output file to be stored at (please use backslashes '\\', not slashes!): ")
while not os.path.exists(outputDir):
    print("Path '" + str(outputDir) + "' does not exist.")
    outputDir = input("Please enter a valid path: ")
outputDir += '\\' + input("Enter name of output file: ") + '.txt'

print("Converting PDF to plain text...")
# convert pdf to plain text
os.system('java -jar ' + jarDir + ' ' + inputDir + ' output.txt' + ' --include body')
print("Finished conversion, removing noise...")

input_file = open('output.txt', encoding='UTF-8')
output = open(outputDir, 'w', encoding='UTF-8')

# patterns of noise
number_rb = '\([0-9]+\)'  # number within round brackets, e.g. "(1)"
number_fs = '[0-9]+\.'  # number ending with full stop, e.g. "1."
letter_rb = ' \(?[a-z]\)'  # lower-case letter within round brackets
roman_rb = '\([x,i,v]{1,4}\)'  # roman numerals within round brackets, recognizes up to no. 17 (xvii)
regulation = '\(E?E[CU]\) (No )?[0-9]+/[0-9]+'  # name of a Regulation, e.g. "(EEC) No 2956/84"
directive_old = '(No )?[0-9]+/[0-9]+/[A-Z]+'  # name of a Directive or Decision before 1 January 2015, e.g. "91/477/EEC"
directive_new = '(\(EU\)|\(Euratom\)|\(EU, Euratom\)|\(CFSP\)) [0-9]+/[0-9]+'  # name of a Directive or Decision after 1 January 2015, e.g. "(EU) 2016/680"
patterns = (number_fs, number_rb, letter_rb, roman_rb, regulation, directive_old, directive_new)


for line in input_file:  # line = one text block in PDF
    if line != '\n':
        # remove enumeration at start of each text block
        match = re.match(number_rb, line)
        if match:
            line = line.removeprefix(match.group(0))[1:]
        match = re.match(number_fs, line)
        if match:
            line = line.removeprefix(match.group(0))[1:]

        # remove noise within text blocks
        for pattern in patterns:
            line = re.sub(pattern, '', line)

    output.write(line)

input_file.close()
output.close()
