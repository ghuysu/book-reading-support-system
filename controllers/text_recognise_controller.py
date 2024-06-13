import base64
import datetime
import io
import os
import cv2
import numpy as np
from PIL import Image
from flask import url_for
from keras.preprocessing.image import img_to_array
from keras.preprocessing.sequence import pad_sequences
from pytesseract import pytesseract
from flask import request, jsonify
from models.file_model import File
import datetime
from pdf2image import convert_from_path
import tensorflow.keras as keras
from keras import Model
from keras.src.applications.densenet import DenseNet201
import pickle

def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'model.keras')
    tokenizer_path = os.path.join(os.path.dirname(__file__), 'tokenizer.pkl')
    caption_model = keras.models.load_model(model_path)
    max_length = 44
    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
    base_model = DenseNet201(weights='imagenet')
    fe = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
    return caption_model, max_length, tokenizer, base_model, fe

caption_model, max_length, tokenizer, base_model, fe = load_model()
print(caption_model, max_length, tokenizer, base_model, fe)


def deleteFile(image_path):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn tuyệt đối đến thư mục chứa file Python hiện tại
        file_path = os.path.join(base_dir, ".." + image_path)  # Đường dẫn tuyệt đối đến tệp tin cần xoá
        os.unlink(file_path)
        print(f"File '{image_path}' deleted successfully")
    except FileNotFoundError:
        print(f"File '{image_path}' not found")
    except Exception as e:
        print(f"An error occurred while deleting file '{image_path}': {e}")


def readImage(image_data, img_size=224):
    img = image_data.convert('RGB').resize((img_size, img_size))
    img = img_to_array(img)
    img = img / 255.
    img = np.expand_dims(img, axis=0)
    return img

def saveImg(image):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    static_dir = os.path.join(os.getcwd(), 'src', 'static', 'images')
    image_path = os.path.join(static_dir, f'image_{timestamp}.jpg')
    image.save(image_path)
    image_url = url_for('static', filename=f'images/image_{timestamp}.jpg')
    return image_url

def extract_features(image_data, model, img_size=224):
    img = readImage(image_data, img_size)
    features = model.predict(img, verbose=0)
    return features

def generate_caption(model, tokenizer, photo, max_length):
    in_text = 'startseq'
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_length)
        yhat = model.predict([photo, sequence], verbose=0)
        yhat = np.argmax(yhat)
        word = tokenizer.index_word[yhat]
        if word is None:
            break
        in_text += ' ' + word
        if word == 'endseq':
            break
    final_caption = in_text.replace('startseq ', '').replace(' endseq', '')
    return final_caption

def image_caption(image_base64):
    features = extract_features(image_base64, fe)
    caption = generate_caption(caption_model, tokenizer, features, max_length)
    return caption

def imageToText(images_base64, user_id):
    predictions = []
    urls = []
    for image_base64 in images_base64:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        url = saveImg(image)
        text = pytesseract.image_to_string(image)
        text = text.strip().replace("\n", " ")
        if len(text) == 0:
            text = image_caption(image)
        predictions.append(text)
        urls.append(url)
    user = user_id
    if not user_id:
        user = "guest"
    new_file = File(user=user, img_urls=urls, predictions=predictions, date=datetime.date.today())
    new_file.save()
    return predictions

class Text_Recognise_Controller:
    @staticmethod
    def text_recognise():
        try:
            images_base64 = request.json.get('images', None)
            user_id = request.json.get('user_id', None)
            if not images_base64 or len(images_base64) == 0:
                raise ValueError("No Images Found")
            text_predictions = imageToText(images_base64, user_id)
            return jsonify({
                "status": 200,
                "message": "Handled Successfully",
                "result": text_predictions
            }), 200
        except Exception as e:
            print(e)
            return jsonify({
                "status": "Error",
                "code": 500,
                "message": str(e)
            }), 500

    @staticmethod
    def getRequest():
        date = request.json.get("date", None)
        if not date:
            date = datetime.date.today()
        pipeline = [
            {'$match': {'user': 'guest'}},  # Chỉ lấy các bản ghi của user_id đã đăng nhập
            {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}}}},
            {'$addFields': {'date': {'$dateFromString': {'dateString': '$_id'}}}},
            {'$project': {'_id': 0, 'date': 1}},
            {'$sort': {'date': 1}}  # Sắp xếp theo thứ tự ngày tăng dần
        ]
        date_list = [doc['date'].date() for doc in File.objects.aggregate(pipeline)]

        # Lấy các bản ghi tương ứng với ngày đã chọn
        records = [record.to_dict() for record in File.objects(date=date, user='guest')]
        print(records)
        return jsonify({
            "status": 200,
            "message": "Get records successfully",
            "metadata": {
                "records": records,
                "date": date,
                "date_list": date_list
            }
        })

    @staticmethod
    def pdf_handler():
        # Lấy file PDF từ request
        pdf_file = request.files['pdfFile']
        if not pdf_file:
            return jsonify({
                "status": 400,
                "message": "No PDF file provided"
            })
        try:
            pdf_path = f"/Users/ghuy/Desktop/fortest/pbl5/src/static/files/{pdf_file.filename}"
            pdf_file.save(pdf_path)
            images = convert_from_path(pdf_path)
            os.remove(pdf_path)

            # Lưu mỗi trang thành một ảnh riêng lẻ
            image_urls = []
            predictions = []
            for i, image in enumerate(images):
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                image_path = f"/Users/ghuy/Desktop/fortest/pbl5/src/static/images/page_{i}_{timestamp}.jpg"
                image.save(image_path, 'JPEG')
                image_url = url_for('static', filename=f'images/page_{i}_{timestamp}.jpg')
                image_urls.append(image_url)
                predictions.append(predict(image))

            user_id = request.cookies.get('user_id')
            new_file = File(user=user_id, img_urls=image_urls, predictions=predictions, date=datetime.date.today(), file_name=pdf_file.filename)
            new_file.save()
            return jsonify({
                "status": 200,
                "message": "PDF processed successfully",
                "file": new_file.to_dict()
            })
        except Exception as e:
            print(e)
            return jsonify({
                "status": 500,
                "message": str(e)
            })

    @staticmethod
    def getFiles():
        date = request.json.get("date", None)
        if not date:
            date = datetime.date.today()

        # Lấy danh sách ngày duy nhất từ tất cả các tài liệu trong collection Files
        user_id = request.cookies.get('user_id')
        pipeline = [
            {'$match': {'user': user_id}},  # Chỉ lấy các bản ghi của user_id đã đăng nhập
            {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}}}},
            {'$addFields': {'date': {'$dateFromString': {'dateString': '$_id'}}}},
            {'$project': {'_id': 0, 'date': 1}},
            {'$sort': {'date': 1}}  # Sắp xếp theo thứ tự ngày tăng dần
        ]
        date_list = [doc['date'].date() for doc in File.objects.aggregate(pipeline)]
        # Lấy các bản ghi tương ứng với ngày đã chọn
        records = [record.to_dict() for record in File.objects(date=date, user=user_id)]
        print(records)
        return jsonify({
            "status": 200,
            "message": "Get records successfully",
            "metadata": {
                "records": records,
                "date": date,
                "date_list": date_list
            }
        })

    @staticmethod
    def remove_file():
        file_id = request.json.get("id")
        user_id = request.json.get("user_id", None)
        if user_id == None:
            user_id = request.cookies.get('user_id')
        file = File.objects(id=file_id, user=user_id).first()
        if not file:
            return jsonify({
                "status": 404,
                "message": "File not found or you don't have permission to remove it."
            })
        try:
            # Xóa các tệp ảnh liên quan
            for image_url in file.img_urls:
                image_path = str(image_url)
                deleteFile(image_path)
            file.delete()
            return jsonify({
                "status": 200,
                "message": "File removed successfully."
            })
        except Exception as e:
            print(e)
            return jsonify({
                "status": 500,
                "message": str(e)
            })

def predict(image):
    text = pytesseract.image_to_string(image)
    text = text.strip().replace("\n", " ")
    if len(text) == 0:
        text = '"' + image_caption(image).capitalize() + '"'
    return text

