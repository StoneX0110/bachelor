import os
import re
import string

# PDFBox https://pdfbox.apache.org

# directory of pdf to be converted, asked in user prompt
inputDir = input("Enter a path to the PDF file (please use slashes '/', not backslashes!): ")
while not os.path.exists(inputDir):
    print("File could not be found at " + str(inputDir))
    inputDir = input("Please enter a valid path: ")

# directory of output to be stored at, asked in user prompt
outputDir = input(
    "Enter a path to a folder where the output file(s) should be stored at (please use slashes '/', not backslashes!): ")
while not os.path.exists(outputDir):
    print("Path '" + str(outputDir) + "' does not exist.")
    outputDir = input("Please enter a valid path: ")
output_name = '/' + input("Enter name of output file(s): ") + '.txt'

# granularity by which the document will be split (by its chapters, articles, etc.) into multiple documents
granularity = input("Enter granularity of splitting (available options: chapter | section | article | none): ")
while granularity != "chapter" and granularity != "section" and granularity != "article" and granularity != "none":
    granularity = input("Please enter a valid option (available options: chapter | section | article | none): ")

print("Converting PDF to plain text...")
# convert pdf to plain text
os.system(f'java -jar pdfbox-app-3.0.0-RC1.jar export:text -i={inputDir}')

input_file = open(inputDir.replace(".pdf", ".txt"), encoding='UTF-8')
output = open(outputDir + output_name, 'w', encoding='UTF-8')


def editor(line, footnote):
    global ends_with_comma
    # filter out page headers
    if not re.search(date, line) or not re.search(issue, line) or not re.search(title, line) or not re.search(language, line):

        if footnote:  # stores whether it is possible that the next paragraph is a footnote
            paragraph = ""  # stores current paragraph
            # footnotes always start with a number within brackets
            if re.match('\( ?[0-9]+ ?\)', line):
                # store current paragraph (end of paragraph indicated by punctuation mark)
                while not re.search('\.[ ]*\n', line) and not re.search(';[ ]*\n', line) and not re.search(':[ ]*\n', line):
                    paragraph += line
                    line = input_file.readline()
                paragraph += line
                line = input_file.readline()

                # check if paragraph is a footnote
                if "OJ" not in paragraph and paragraph != "":
                    # if it is not a footnote, the paragraph is put into the method again
                    ewc_temp = ends_with_comma
                    ends_with_comma = False
                    paragraph = paragraph.split('\n')
                    for line_of_text in paragraph:
                        editor(line_of_text + '\n', False)
                    ends_with_comma = ewc_temp

                editor(line, True)
                return

        if ends_with_comma:
            # check if previous comma separated different logical text blocks
            if line[0] not in string.ascii_lowercase:
                # comma separates text blocks, so we can add newline
                line = '\n' + line
            ends_with_comma = False

        # remove empty spaces and newline at end of line
        line = line[:re.search('[ ]*$', line).start()]
        # remove empty lines
        if line == "":
            return

        # check for punctuation mark at end of line
        if line[len(line) - 1] in punctuation_marks:
            # if comma at end, don't add newline in case it is normal comma within sentence
            if line[len(line) - 1] == ',':
                ends_with_comma = True
                line += " "
            else:
                # add newline if there is a punctuation mark at end of line
                line += '\n'
        else:
            # merge word which was separated at end of line (information loss in case of hyphenated word)
            if line.endswith('­'):
                line = line.removesuffix('­')
            else:
                line += " "

        output.write(line)


# regex to identify page headers
date = '[0-9]{1,2}.[0-9]{1,2}.[0-9]{2,4}'
issue = 'L [0-9]+/[0-9]+'
title = 'Official Journal of the European Union'
language = 'EN'

punctuation_marks = {',', '.', '!', '?', ';', ':'}

ends_with_comma = False  # stores whether previous line ended with comma

for line in input_file:
    editor(line, True)

output.close()
input_file.close()
os.remove(inputDir.replace(".pdf", ".txt"))

print("Finished conversion, splitting document...")

file = open('output_raw.txt', encoding='UTF-8')
raw = file.read()
file.close()
file = open('output_filtered.txt', encoding='UTF-8')
filtered = file.read()
file.close()

# TODO split annex from rest of document

# TODO rework this part because of new text extraction tool
counter = 0
if granularity == "chapter" or granularity == "section":
    # search for all chapters
    pattern = '\nCHAPTER .+?Article [0-9]+\n'
    m = re.search(pattern, raw, re.DOTALL)
    c_beginnings = []  # stores the articles where the chapters start at
    while m:
        c_beginnings.append(m.group(0)[m.group(0).find('Article'):])
        raw = raw[:m.start()] + raw[m.end():]
        m = re.search(pattern, raw, re.DOTALL)

    if len(c_beginnings) > 0:
        # create files for each chapter
        for chapter in c_beginnings:
            output = open(f'{outputDir}_chapter_{counter}.txt', 'w', encoding='UTF-8')
            output.write(filtered.split(chapter)[0])
            filtered = filtered.split(chapter)[1]
            output.close()
            counter += 1
        output = open(f'{outputDir}_chapter_{counter}.txt', 'w', encoding='UTF-8')
        output.write(filtered)
        output.close()

        if granularity == "section":
            for i in range(counter):
                # search for section at start of chapter
                pattern = '\n[SECTIONsection ]{7,}.+?Article [0-9]+\n'
                file = open(f'{outputDir}_chapter_{i + 1}.txt', 'r', encoding='UTF-8')
                chapter = file.read()
                file.close()
                m = re.search(pattern, chapter, re.DOTALL)
                s_beginnings = []  # stores the articles where the sections start at
                while m:
                    s_beginnings.append(m.group(0)[m.group(0).find('Article'):])
                    chapter = chapter.replace(m.group(0)[:m.group(0).find('Article')], '')
                    m = re.search(pattern, chapter, re.DOTALL)

                if len(s_beginnings) > 0:
                    counter2 = 0
                    # create files for each chapter
                    for section in s_beginnings:
                        if counter2 != 0:
                            output = open(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt', 'w', encoding='UTF-8')
                            output.write(chapter.split(section)[0])
                            chapter = chapter.split(section)[1]
                            output.close()
                        counter2 += 1
                    output = open(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt', 'w', encoding='UTF-8')
                    output.write(chapter)
                    output.close()

                    os.remove(f'{outputDir}_chapter_{i + 1}.txt')
    else:
        output = open(f'{outputDir}_chapter_{counter}.txt', 'w', encoding='UTF-8')
        output.write(filtered)
        output.close()

elif granularity == "article":
    # search for all articles
    pattern = 'Article [0-9]+\n'
    m = re.search(pattern, raw)
    beginnings = []  # stores heading of articles (without title)
    while m:
        beginnings.append(m.group(0))
        raw = raw[:m.start()] + raw[m.end():]
        m = re.search(pattern, raw)

    # create files for each article
    for article in beginnings:
        output = open(f'{outputDir}_{granularity}_{counter}.txt', 'w', encoding='UTF-8')
        output.write(filtered.split(article)[0])
        filtered = filtered.split(article)[1]
        output.close()
        counter += 1
    output = open(f'{outputDir}_{granularity}_{counter}.txt', 'w', encoding='UTF-8')
    output.write(filtered)
    output.close()

print("Removing noise...")

# TODO rework this part because of new text extraction tool
# patterns of noise
# TODO remove remaining titles of article/chapter/section/sub-section/etc. ('Article [0-9]+\n' or similar)
number_rb = '\([0-9]+\)'  # number within round brackets, e.g. "(1)"
number_fs = '[0-9]+\.'  # number ending with full stop, e.g. "1."
letter_rb = ' \(?[a-z]\)'  # lower-case letter within round brackets
roman_rb = '\([x,i,v]{1,4}\)'  # roman numerals within round brackets, recognizes up to no. 17 (xvii)
regulation = '\(E?E[CU]\) (No )?[0-9]+/[0-9]+'  # name of a Regulation, e.g. "(EEC) No 2956/84"
directive_old = '(No )?[0-9]+/[0-9]+/[A-Z]+'  # name of a Directive or Decision before 1 January 2015, e.g. "91/477/EEC"
directive_new = '(\(EU\)|\(Euratom\)|\(EU, Euratom\)|\(CFSP\)) [0-9]+/[0-9]+'  # name of a Directive or Decision after 1 January 2015, e.g. "(EU) 2016/680"
patterns = (number_fs, number_rb, letter_rb, roman_rb, regulation, directive_old, directive_new)

# remove noise from each previously created document
input_file = open(outputDir, encoding='UTF-8')  # TODO implement iteration through all previously split documents
output = open(outputDir, 'w', encoding='UTF-8')  # TODO see above
for line in input_file:
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
