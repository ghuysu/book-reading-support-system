from flask import Blueprint, jsonify
from controllers.text_recognise_controller import Text_Recognise_Controller

text_recognise_route_app = Blueprint('text_recognise_route_app', __name__)

@text_recognise_route_app.route('/text-recognise', methods=['POST'])
def text_recognise_route():
    return Text_Recognise_Controller.text_recognise()

@text_recognise_route_app.route('/get-request', methods=['POST'])
def get_request():
    return Text_Recognise_Controller.getRequest()

@text_recognise_route_app.route('/pdf-text-recognise', methods=['POST'])
def pdf_text_recognise():
    return Text_Recognise_Controller.pdf_handler()

@text_recognise_route_app.route('/get-files', methods=['POST'])
def get_files():
    return Text_Recognise_Controller.getFiles()

@text_recognise_route_app.route('/remove-file', methods=['POST'])
def remove_file():
    return Text_Recognise_Controller.remove_file()