from flask import Blueprint, render_template
from controllers.access_controller import Access_Controller

access_route_app = Blueprint('access_route_app', __name__)

@access_route_app.route('/login', methods=['POST'])
def sign_in_post_route():
    return Access_Controller.login()

@access_route_app.route('/login', methods=['GET'])
def sign_in_get_route():
    return render_template("login.html")

@access_route_app.route('/signup', methods=['POST'])
def sign_up_post_route():
    return Access_Controller.signup()

@access_route_app.route('/signup', methods=['GET'])
def sign_up_get_route():
    return render_template("signup.html")