from flask import render_template, Flask, request, send_file, session
from fileoperations import parse_xml, get_file_path, get_header, get_payload, clean_temp_folder, get_combined_file_path
import datetime
import uuid
import secrets


def get_guid():
    return str(uuid.uuid4())


def get_secret():
    return secrets.token_hex()


app = Flask(__name__)
app.secret_key = get_secret()


@app.route('/')
def home():
    if 'id' not in session:
        session['id'] = get_guid()
    current_year = datetime.datetime.now().year
    return render_template('index.html', footer_year=current_year)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        clean_temp_folder()
        f = request.files['sungl_response_file']
        file_path = get_file_path(f.filename)
        f.save(file_path)
        session['download_file_name'] = (f.filename + '_rejected.csv')
        parse_xml(file_path)
        header_df = get_header()
        payload_df = get_payload()
        return render_template("parsed_response.html",
                               header_df=header_df,
                               payload_df=payload_df,
                               filename=f.filename
                               )
    else:
        return None


@app.route('/download', methods=['GET'])
def download():
    return send_file(get_combined_file_path(), download_name=session['download_file_name'])


if __name__ == '__main__':
    app.run(debug=True)
