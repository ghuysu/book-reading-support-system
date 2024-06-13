import os
from flask import Flask, jsonify, render_template, request
from models.account_model import Account
from routes.text_recognise_route import text_recognise_route_app
from routes.access_route import access_route_app
from controllers.db_connection import connect_to_mongodb

app = Flask(__name__)

app.register_blueprint(text_recognise_route_app)
app.register_blueprint(access_route_app)
@app.route('/', methods=['GET'])
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return render_template("login.html")
    account = Account.objects(id=user_id).first()
    if account.role == "manager":
        return render_template("supervise.html")
    else:
        return render_template("pdf_scanner.html")

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "status": "Error",
        "code": 404,
        "message": "Not Found"
    }), 404


if __name__ == '__main__':
    connect_to_mongodb()
    port = int(os.environ.get('PORT', 3400))
    app.run(host='0.0.0.0', port=port)


