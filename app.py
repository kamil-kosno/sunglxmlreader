from flask import render_template, Flask, request, send_file
from fileoperations import parse_xml, get_file_path, get_header, get_payload, clean_temp_folder, get_combined_file_path
import datetime

app = Flask(__name__)


@app.route('/')
def home():
    current_year = datetime.datetime.now().year
    return render_template('index.html', footer_year=current_year)


download_file_name = ['']


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        clean_temp_folder()
        f = request.files['sungl_response_file']
        file_path = get_file_path(f.filename)
        download_file_name[0] = (f.filename + '_rejected.csv')
        f.save(file_path)
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
    return send_file(get_combined_file_path(), download_name=download_file_name[0])


if __name__ == '__main__':
    app.run(debug=True)
