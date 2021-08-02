import io
import os
import shutil
import zipfile
import argparse
from flask import Flask, request, redirect, send_file
from werkzeug.utils import secure_filename
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("data_storage", help="path to directory where user files will be stored at")
args = parser.parse_args()

os.chdir(args.data_storage)
if not os.path.exists("output"):
    os.mkdir("output")

# directory of Main-program for later execution
main_dir = os.path.join(Path(__file__).parent, "Main.py")

extensions = {'pdf'}
app = Flask(__name__)


# checks whether uploaded file is a pdf
def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


# removes output of previous document
def cleanup():
    shutil.rmtree("output")
    os.mkdir("output")


@app.route("/", methods=["GET", "POST"])
def index():
    # if user uploaded a file
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        # if file is a pdf
        if allowed(file.filename):
            cleanup()
            filename = secure_filename(file.filename)
            file.save(filename)
            # execute code from Main.py
            if request.form.get("granularity") == "none":
                os.system(f"py {main_dir} {os.path.join(os.getcwd(), filename)} {os.path.join(os.getcwd(), 'output')}")
            else:
                os.system(
                    f"py {main_dir} {os.path.join(os.getcwd(), filename)} {os.path.join(os.getcwd(), 'output')} -g {request.form.get('granularity')}")
            os.remove(f'{os.path.join(os.getcwd(), filename)}')
            # redirect to site which provides output to user
            return redirect("output")
    # main page
    return '''
        <h1>Document Clean-Up</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <br><br>
        Granularity of Splitting: <select name="granularity">
            <option value="none" selected>None</option>
            <option value="chapter">Chapter</option>
            <option value="section">Section</option>
            <option value="article">Article</option>
        </select>
        <input type=submit value=Submit>
    '''


@app.route("/output")
def output():
    data = io.BytesIO()
    # zip output files
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in os.listdir('output'):
            z.write(os.path.join('output', f_name))
    data.seek(0)
    # send zip-file to user
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        download_name='data.zip'
    )


if __name__ == "__main__":
    app.run(port=1337)
