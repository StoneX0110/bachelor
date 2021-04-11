import os

# PdfAct https://github.com/ad-freiburg/pdfact
# read-in PDF file and convert to TXT
jarDir = os.getcwd().removesuffix('src') + 'pdfact\\bin\\pdfact.jar'
inputDir = 'C:\\Users\\Patrick\\Desktop\\dsgvo.pdf'  # TODO User prompt?
outputDir = 'C:\\Users\\Patrick\\Desktop\\output.txt'  # TODO User prompt?
os.system('java -jar ' + jarDir + ' ' + inputDir + ' ' + outputDir + ' --include body')

