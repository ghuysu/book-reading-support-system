from flask import jsonify, request
from models.account_model import Account
import bcrypt

class Access_Controller:
    @staticmethod
    def login():
        username = request.json.get("username")
        password = request.json.get("password")
        role = request.json.get("role")
        try:
            account = Account.objects(username=username, role=role).first()
            if not account:
                return jsonify({
                    "status": 500,
                    "error": "Account is not registered"
                })
            if not bcrypt.checkpw(password.encode('utf-8'), account.password.encode('utf-8')):
                return jsonify({
                    "status": 500,
                    "error": "Password is incorrect"
                })
            return jsonify({
                "status": 200,
                "message": "Login successfully",
                "metadata": {
                    "user_id": str(account.id)
                }
            })
        except Exception as e:
            print(e)
            return jsonify({
                "status": 500,
                "error": "Login failed"
            })

    @staticmethod
    def signup():
        username = request.json.get("username")
        password = request.json.get("password")
        try:
            account = Account.objects(username=username, role="user").first()
            if account:
                return jsonify({
                    "status": 500,
                    "error": "Username already registered"
                })
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_account = Account(username=username, password=hashed_password)
            new_account.save()
            return jsonify({
                "status": 201,
                "message": "Signup successfully",
                "metadata": {
                    "user": new_account.to_dict()
                }
            })
        except Exception as e:
            print(e)
            return jsonify({
                "status": 500,
                "error": "Signup failed"
            })
