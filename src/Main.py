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
outputDir += '/' + input("Enter name of output file(s): ")

# granularity by which the document will be split (by its chapters, articles, etc.) into multiple documents
granularity = input("Enter granularity of splitting (available options: chapter | section | article | none): ")
while granularity != "chapter" and granularity != "section" and granularity != "article" and granularity != "none":
    granularity = input("Please enter a valid option (available options: chapter | section | article | none): ")

print("Converting PDF to plain text...")
# convert pdf to plain text
os.system(f'java -jar pdfbox-app-3.0.0-RC1.jar export:text -i={inputDir}')

print("Splitting document...")


# gets thrown when annex is reached when reading the input
class GetOutOfLoop(Exception):
    pass


input_file = open(inputDir.replace(".pdf", ".txt"), encoding='UTF-8')
counter = 0  # keeps track of chapter/article count
documents = []  # stores names of all created documents for later processing
annex = 'ANNEX [I ]+\n'  # pattern to recognize start of annex

if granularity == "chapter" or granularity == "section":
    pattern = 'CHAPTER .+?\n'
    try:
        for line in input_file:
            # store every chapter in its own file
            output = open(f'{outputDir}_chapter_{counter}.txt', 'w', encoding='UTF-8')
            documents.append(f'{outputDir}_chapter_{counter}.txt')
            counter += 1
            # break when new chapter is reached
            while not re.match(pattern, line) and line != "":
                if re.match(annex, line):
                    output.close()
                    raise GetOutOfLoop
                output.write(line)
                line = input_file.readline()
            output.close()
    except GetOutOfLoop:
        pass

    if granularity == "section":
        pattern = '((S ?E ?C ?T ?I ?O ?N)|(S ?e ?c ?t ?i ?o ?n))[ 0-9A-Z]*\n'
        # if counter > 1 ?
        # search every chapter for sections
        for i in range(counter - 1):
            counter2 = 0  # keeps track of section count
            chapter = open(f'{outputDir}_chapter_{i + 1}.txt', encoding='UTF-8')
            for line in chapter:
                # store every section in its own file
                output = open(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt', 'w', encoding='UTF-8')
                documents.append(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt')
                # break when new section is reached
                while not re.match(pattern, line) and line != "":
                    output.write(line)
                    line = chapter.readline()
                if re.match(pattern, line):
                    counter2 += 1
                output.close()
            chapter.close()
            # if there were sections in the chapter, the original chapter file gets removed
            if counter2 > 0:
                documents.remove(f'{outputDir}_chapter_{i + 1}.txt')
                os.remove(f'{outputDir}_chapter_{i + 1}.txt')
                documents.remove(f'{outputDir}_chapter_{i + 1}_section_{0}.txt')
                os.remove(f'{outputDir}_chapter_{i + 1}_section_{0}.txt')
            # if there were no sections, we need to remove the document of 'section 0' (it has the same text as the respective chapter document)
            elif counter2 == 0:
                documents.remove(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt')
                os.remove(f'{outputDir}_chapter_{i + 1}_section_{counter2}.txt')

elif granularity == "article":
    pattern = 'Article[ 0-9]+\n'
    try:
        for line in input_file:
            # store every article in its own file
            output = open(f'{outputDir}_article_{counter}.txt', 'w', encoding='UTF-8')
            documents.append(f'{outputDir}_article_{counter}.txt')
            counter += 1
            # break when new article is reached
            while not re.match(pattern, line) and line != "":
                if re.match(annex, line):
                    output.close()
                    raise GetOutOfLoop
                output.write(line)
                line = input_file.readline()
            output.close()
    except GetOutOfLoop:
        pass

else:
    # everything is put into one document
    output = open(f'{outputDir}.txt', 'w', encoding='UTF-8')
    documents.append(f'{outputDir}.txt')
    try:
        for line in input_file:
            if re.match(annex, line):
                output.close()
                raise GetOutOfLoop
            else:
                output.write(line)
        output.close()
    except GetOutOfLoop:
        pass

input_file.close()
os.remove(inputDir.replace(".pdf", ".txt"))

print("Removing noise...")


# removes all remaining titles of subdivisions in a document
def remove_titles(file):
    patterns = ('PART .+?\n', 'TITLE .+?\n', 'CHAPTER .+?\n', '((S ?E ?C ?T ?I ?O ?N)|(S ?e ?c ?t ?i ?o ?n))[ 0-9A-Z]*\n',
                '((S ?U ?B ?- ?S ?E ?C ?T ?I ?O ?N)|(S ?u ?b ?- ?S ?e ?c ?t ?i ?o ?n))[ 0-9A-Z]*\n', 'Article[ 0-9]+\n')

    input_file = open(file, encoding='UTF-8')
    # delete all titles
    # for pattern in patterns:
    #     input_file = re.sub(pattern, '', input_file)

    # update file
    text = ""
    for line in input_file:
        for pattern in patterns:
            if re.match(pattern, line):
                line = input_file.readline()
                line = input_file.readline()
                while line[0] in string.ascii_lowercase:
                    line = input_file.readline()
        text += line
    output = open(file, 'w', encoding='UTF-8')
    output.write(text)
    output.close()


# regex to identify page headers
date = '[0-9]{1,2}.[0-9]{1,2}.[0-9]{2,4}'
issue = 'L [0-9]+/[0-9]+'
title = 'Official Journal of the European Union'
language = 'EN'

punctuation_marks = {',', '.', '!', '?', ';', ':'}

ends_with_comma = False  # stores whether previous line ended with comma


# removes spurious newlines, page headers and footnotes
def editor(line, footnote):
    global ends_with_comma
    global result
    # filter out page headers
    if not re.search(date, line) or not re.search(issue, line) or not re.search(title, line) or not re.search(language, line):

        if footnote:  # stores whether it is possible that the current paragraph is a footnote
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

        result += line


# patterns of noise
number_rb = '\( ?[0-9]+ ?\)'  # number within round brackets, e.g. "(1)"
number_fs = '[0-9]+\.'  # number ending with full stop, e.g. "1."
letter_rb = '\([a-z]\)'  # lower-case letter within round brackets, e.g. "(a)"
roman_rb = '\([x,i,v]{1,4}\)'  # roman numerals within round brackets, recognizes up to no. 17 (xvii)
regulation = '\(E?E[CU]\) (No )?[0-9]+/[0-9]+'  # name of a Regulation, e.g. "(EEC) No 2956/84"
directive_old = '(No )?[0-9]+/[0-9]+/[A-Z]+'  # name of a Directive/Decision before 01.01.2015, e.g. "91/477/EEC"
directive_new = '(\(EU\)|\(Euratom\)|\(EU, Euratom\)|\(CFSP\)) [0-9]+/[0-9]+'  # name of a Directive/Decision after 01.01.2015, e.g. "(EU) 2016/680"
patterns = (number_fs, number_rb, letter_rb, roman_rb, regulation, directive_old, directive_new)


# remove noise from each previously created document
def remove_noise(line):
    global result
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

    result += line


# remove noise in documents
for document in documents:
    # remove remaining titles in document
    remove_titles(document)

    # remove spurious newlines, page headers and footnotes
    input_file = open(document, encoding='UTF-8')
    result = ""
    for line in input_file:
        editor(line, True)
    input_file.close()
    output = open(document, 'w', encoding='UTF-8')
    output.write(result)
    output.close()

    # remove remaining noise
    input_file = open(document, encoding='UTF-8')
    result = ""
    for line in input_file:
        remove_noise(line)
    input_file.close()
    output = open(document, 'w', encoding='UTF-8')
    output.write(result)
    output.close()
