from hashlib import new
from re import sub
from time import time
from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
import json
import file_utils
import os,zipfile


logger = file_utils.init_logger()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/version", methods=['POST'])
def get_version():
    deviceInfo = request.get_json()
    result = "pocket"
    logger.info("version: " + json.dumps(deviceInfo) + " res: " + result)
    return result


def backup(file, meta_str):
    backup_datetime_path = file_utils.get_backup_datetime_path()
    file_path = os.path.join(backup_datetime_path, file.filename)
    file_utils.mkdir(backup_datetime_path)
    file_utils.save_file(file, file_path)
    meta_path = os.path.join(backup_datetime_path, file.filename + '.meta')
    with open(meta_path, 'w') as fout:
        fout.write(meta_str)
    return file_path

'''
Name: upload_collected_data
Method: Post
Content-Type: multipart/form-data
Form:
    - file
    - fileType
        - 0 sensor bin
    - userId
    - name
    - commit
    - timestamp


    /dex
        /userId
            /name
                /timestamp
                    - {}.bin
'''
@app.route("/collected_data", methods=['POST'])
def upload_collected_data():
    file = request.files["file"]
    print(file.filename, flush=True)
    meta_str = request.form.get("meta")
    logger.info("get file: " + file.filename)
    logger.info("get meta: " + meta_str)
    try:
        file_path = backup(file, meta_str)
        meta = json.loads(meta_str)
        print(meta, flush=True)
        if file.filename[-4:] == '.zip':
            with zipfile.ZipFile(file_path, 'r') as file_zip:
                for m in meta:
                    if m['file'] not in file_zip.namelist():
                        logger.error("Not in zip's name list: " + m['file'])
                for name in file_zip.namelist():
                    print(name, flush=True)
                    meta_ = None
                    for m in meta:
                        if m['file'] == name:
                            meta_ = m
                    print(meta_, flush=True)
                    if meta_ is not None:
                        path = file_utils.get_dex_path(meta_['userId'], meta_['name'], str(meta_['timestamp']))
                        extracted_file_path = os.path.join(path, meta_['file'])
                        if os.path.exists(extracted_file_path):
                            logger.error("already uploaded, override: " + extracted_file_path)
                        else:
                            logger.info("extract: " + extracted_file_path)
                        file_utils.mkdir(path)
                        file_zip.extract(meta_['file'], path)
                        with open(os.path.join(path, meta_['file'] + '.meta'), 'w') as fout:
                            fout.write(json.dumps(meta_))
                    else:
                        logger.error("Not in meta info: " + name)
        else:
            path = file_utils.get_dex_path(meta[0]['userId'], meta[0]['name'], str(meta[0]['timestamp']))
            file_utils.mkdir(path)
            file_path = os.path.join(path, meta[0]['file'])
            file_utils.save_file(file, file_path)
            with open(os.path.join(path, meta[0]['file'] + '.meta'), 'w') as fout:
                fout.write(json.dumps(meta[0]))
    except Exception as e:
        logger.exception("Exception happens")


    '''
    fileType = request.form.get("fileType")
    userId = request.form.get("userId")
    name = request.form.get("name")
    timestamp = request.form.get("timestamp")
    path = file_utils.get_dex_path(userId, name, timestamp)
    file_path = os.path.join(path, file.filename)
    print(f"saving file: {file_path}")
    file_utils.mkdir(path)
    file_utils.save_file(file, file_path)
    '''
    return {}


'''
Name: list_files in dir
Method: GET
Content-Type: multipart/form-data
Form:
    - name
'''
@app.route("/dir", methods=['GET'])
def list_file_dir():
    filename = request.args.get("name")
    return json.dumps(os.listdir(os.path.join(file_utils.DATA_FILE_ROOT, filename)))



'''
Name: download_file
Method: Post
Content-Type: multipart/form-data
Form:
    - filename
'''
@app.route("/file", methods=['GET'])
def download_file():
    filename = request.args.get("filename")
    return send_file(os.path.join(file_utils.DATA_FILE_ROOT, filename))




'''
Name: update_file
Method: Post
Content-Type: multipart/form-data
Form:
    - file
'''
@app.route("/file", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file:
        file_utils.save_file(file, os.path.join(file_utils.DATA_FILE_ROOT, file.filename))
        file_utils.update_md5()

    return {}


if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0")