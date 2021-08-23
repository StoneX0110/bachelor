import os
import re
import string
import argparse
from pathlib import Path

# PDFBox https://pdfbox.apache.org


# removes table of contents from input file
def remove_toc(input_file):
    result = ""
    for line in input_file:
        if re.match("TABLE OF CONTENTS", line):
            line = input_file.readline()
            identifier = line
            line = input_file.readline()
            while not re.match(line[:re.search('[ ]*$', line).start()], identifier):
                line = input_file.readline()
        result += line
    return result


documents = []  # stores names of all created documents for later processing
# patterns for all headings of subdivisions
heading_patterns = {"part": 'PART .+?\n', "title": 'TITLE .+?\n', "chapter": 'CHAPTER .+?\n',
                    "section": '((S ?E ?C ?T ?I ?O ?N)|(S ?e ?c ?t ?i ?o ?n))[ 0-9A-Z]*\n',
                    "sub-section": '((S ?U ?B ?- ?S ?E ?C ?T ?I ?O ?N)|(S ?u ?b ?- ?S ?e ?c ?t ?i ?o ?n))[ 0-9A-Z]*\n',
                    "article": 'Article[ 0-9]+\n',
                    "annex": 'ANNEX[I ]*\n'}  # pattern to recognize start of annex


# stores annex in file
def handle_annex(input_file, outputDir):
    with open(f'{outputDir}_annex.txt', 'w', encoding='UTF-8') as output:
        for line in input_file:
            output.write(line)


# split a document by granularity
def split(granularity, outputDir):
    global input_file

    counter = 0  # keeps track of chapter/article count
    last_line = ""
    for line in input_file:
        # store every part in its own file
        output = open(f'{outputDir}_{granularity}_{counter}.txt', 'w', encoding='UTF-8')
        documents.append(f'{outputDir}_{granularity}_{counter}.txt')
        counter += 1

        # adds the heading to this file (which is the last_line from previous file)
        if last_line != "":
            output.write(last_line)

        # break when new chapter is reached
        while not re.match(heading_patterns[granularity], line) and line != "":
            # stops when annex is reached
            if re.match(heading_patterns["annex"], line):
                output.close()
                handle_annex(input_file, outputDir)
                return counter
            output.write(line)
            line = input_file.readline()
        output.close()
        last_line = line
    return counter


# adds identifier to all remaining titles of subdivisions in a document
def remove_titles(file):
    global input_file

    input_file = open(file, encoding='UTF-8')

    # update file
    text = ""
    for line in input_file:
        for pattern in heading_patterns.values():
            # marks all titles with identifier for later recognition
            if re.match(pattern, line):
                line = input_file.readline()
                line = line.removesuffix("\n")
                text += line + "TITLE_IDENT\n"
                line = input_file.readline()
                while line != "" and line[0] in string.ascii_lowercase:
                    line = line.removesuffix("\n")
                    text += line + "TITLE_IDENT\n"
                    line = input_file.readline()
        text += line
    with open(file, 'w', encoding='UTF-8') as output:
        output.write(text)


# regex to identify page headers
date = '[0-9]{1,2}.[0-9]{1,2}.[0-9]{2,4}'
issue = 'L [0-9]+/[0-9]+'
title = 'Official Journal of the European Union'
language = 'EN'

punctuation_marks = {',', '.', '!', '?', ';', ':'}

ends_with_comma = False  # stores whether previous line ended with comma


# removes spurious newlines, page headers and footnotes
def editor(line, footnote):
    global ends_with_comma, result, input_file

    # recognize titles through identifier
    while line.endswith("TITLE_IDENT\n"):
        # remove identifier
        line = line.removesuffix("TITLE_IDENT\n")
        # put raw title in result
        result += line + "\n"
        line = input_file.readline()

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
                    if not re.search('[Ss]ee( |\n)+page( |\n)+[0-9]+( |\n)+of( |\n)+this( |\n)+Official( |\n)+Journal', paragraph) and not re.search(
                            'not( |\n)+yet( |\n)+published( |\n)+in( |\n)+the( |\n)+Official( |\n)+Journal', paragraph):
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
# remark: number_fs is only checked at start of line, because otherwise in e.g. "[...] Regulation (EC) 183/2005. [...]" the 2005 gets removed
patterns = (number_rb, letter_rb, roman_rb, regulation, directive_old, directive_new)
# TODO let names of legal acts be removed first (move pattern at start of list above)
#  so that we can remove number_fs with re.sub and not just at the beginning of a line (needs to be tested, though)


# remove noise from each previously created document
def remove_noise(line):
    global result
    if line != '\n':
        # remove enumeration at start of each text block
        match = re.match('\(? ?[0-9]+ ?\)', line)
        if match:
            line = line.removeprefix(match.group(0))[1:]
        match = re.match(number_fs, line)
        if match:
            line = line.removeprefix(match.group(0))[1:]

        # remove noise within text blocks
        for pattern in patterns:
            line = re.sub(pattern, '', line)

    result += line


def main(inputDir, outputDir, granularity):
    global input_file, result

    outputDir += '/' + os.path.basename(inputDir).rsplit(".", 1)[0]

    print("Converting PDF to plain text...")
    # convert pdf to plain text
    os.system(f'java -jar {os.path.join(Path(__file__).parent, "pdfbox-app-3.0.0-RC1.jar")} export:text -i={inputDir}')

    print("Splitting document...")
    # remove table of contents
    with open(inputDir.replace(".pdf", ".txt"), encoding='UTF-8') as input_file:
        result = remove_toc(input_file)
    with open(inputDir.replace(".pdf", ".txt"), 'w', encoding='UTF-8') as input_file:
        input_file.write(result)
    with open(inputDir.replace(".pdf", ".txt"), encoding='UTF-8') as input_file:
        if granularity == "chapter" or granularity == "section":
            chapter_count = split("chapter", outputDir)

            if granularity == "section":
                # if counter > 1 ?
                # search every chapter for sections
                for i in range(chapter_count - 1):
                    section_count = 0  # keeps track of section count per chapter
                    chapter = open(f'{outputDir}_chapter_{i + 1}.txt', encoding='UTF-8')
                    last_line = ""
                    for line in chapter:
                        # store every section in its own file
                        output = open(f'{outputDir}_chapter_{i + 1}_section_{section_count}.txt', 'w', encoding='UTF-8')
                        documents.append(f'{outputDir}_chapter_{i + 1}_section_{section_count}.txt')

                        # adds the heading to this file (which is the last_line from previous file)
                        if last_line != "":
                            output.write(last_line)

                        # break when new section is reached
                        while not re.match(heading_patterns[granularity], line) and line != "":
                            output.write(line)
                            line = chapter.readline()
                        if re.match(heading_patterns[granularity], line):
                            section_count += 1
                        output.close()
                        last_line = line
                    chapter.close()

                    # if there were sections in the chapter, the original chapter file gets removed
                    if section_count > 0:
                        documents.remove(f'{outputDir}_chapter_{i + 1}.txt')
                        os.remove(f'{outputDir}_chapter_{i + 1}.txt')
                        documents.remove(f'{outputDir}_chapter_{i + 1}_section_{0}.txt')
                        os.remove(f'{outputDir}_chapter_{i + 1}_section_{0}.txt')
                    # if there were no sections, we need to remove the document of 'section 0' (it has the same text as the respective chapter document)
                    elif section_count == 0:
                        documents.remove(f'{outputDir}_chapter_{i + 1}_section_{section_count}.txt')
                        os.remove(f'{outputDir}_chapter_{i + 1}_section_{section_count}.txt')
            input_file.close()
            os.remove(inputDir.replace(".pdf", ".txt"))

        elif granularity == "article":
            split(granularity, outputDir)
            input_file.close()
            os.remove(inputDir.replace(".pdf", ".txt"))

        else:
            # everything is put into one document
            result = ""
            documents.append(f'{outputDir}.txt')
            for line in input_file:
                # stops when annex is reached
                if re.match(heading_patterns["annex"], line):
                    handle_annex(input_file, outputDir)
                    break
                else:
                    result += line
            with open(f'{outputDir}.txt', 'w', encoding='UTF-8') as output:
                output.write(result)
            # TODO remove converted txt file when input and output directory are different

    print("Removing noise...")

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
        with open(document, 'w', encoding='UTF-8') as output:
            output.write(result)

        # remove remaining noise
        input_file = open(document, encoding='UTF-8')
        result = ""
        for line in input_file:
            remove_noise(line)
        input_file.close()
        with open(document, 'w', encoding='UTF-8') as output:
            output.write(result)

    try:
        # remove noise in annex
        input_file = open(f'{outputDir}_annex.txt', encoding='UTF-8')
        result = ""
        for line in input_file:
            remove_noise(line)
        input_file.close()
        with open(f'{outputDir}_annex.txt', 'w', encoding='UTF-8') as output:
            output.write(result)
    # pass if there is no annex
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="path to pdf file")
    parser.add_argument("output_path", help="path to output directory")
    parser.add_argument("--granularity", "-g", help="granularity of splitting",
                        choices=["chapter", "section", "article"], default="none")
    args = parser.parse_args()

    # directory of pdf to be converted
    inputDir = args.input_file

    # directory where output will be stored at
    outputDir = args.output_path

    # granularity by which the document will be split into multiple documents
    granularity = args.granularity

    main(inputDir, outputDir, granularity)
