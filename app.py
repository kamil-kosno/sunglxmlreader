from flask import render_template, Flask, request, send_file
from fileoperations import FileOperations
import datetime
import uuid
import secrets


def get_guid():
    return str(uuid.uuid4())


def get_secret():
    return secrets.token_hex()

#guid is used to create unique subfolder
app = Flask(get_guid())
app.secret_key = get_secret()


@app.route('/')
def home():    
    current_year = datetime.datetime.now().year
    return render_template('index.html', footer_year=current_year)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        fo = FileOperations(app.name)
        fo.clean_temp_folder()
        f = request.files['sungl_response_file']
        file_path = fo.get_file_path(f.filename)
        f.save(file_path)
        app.config['DOWNLOAD_FILE_PATH'] = (f.filename + '_rejected.csv')
        fo.parse_xml(file_path)
        header_df = fo.get_header()
        payload_df = fo.get_payload()
        return render_template("parsed_response.html",
                               header_df=header_df,
                               payload_df=payload_df,
                               filename=f.filename
                               )
    else:
        return None


@app.route('/download', methods=['GET'])
def download():
    fo = FileOperations(app.name)
    return send_file(fo.get_combined_file_path(), download_name=app.config['DOWNLOAD_FILE_PATH'])


if __name__ == '__main__':
    app.run(debug=True)
