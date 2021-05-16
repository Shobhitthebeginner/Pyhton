import flask
from flask import request
from flask import jsonify
import face_recognition
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import urllib
import urllib.request
import numpy as np
import pyrebase
import os
import cv2
from PIL import Image
import requests
from io import BytesIO
import requests
from PIL import Image
from io import BytesIO
import numpy as np

config = {
    "type": "",
    "project_id": "",
    "private_key_id": "",
    "private_key": "",
    "client_email": "",
    "client_id": "",
    "auth_uri": "",
    "token_uri": ""
    "client_x509_cert_url": ""
}

cred = credentials.Certificate(config)
firebase_admin.initialize_app(cred)
db = firestore.client()
user = db.collection('image').document('images').get().to_dict()
Name = list(user.keys())
Urls = list(user.values())
images = []
classNames = []
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')





app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    try:
        for i in range(len(Urls)):
            req = urllib.request.urlopen(Urls[i])
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            images.append(img)
            classNames.append(Name[i])
        encodeListKnown = findEncodings(images)
        cpp = cv2.VideoCapture(0)
        while True:
            success, img = cpp.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurrFrame = face_recognition.face_locations(imgS)  # faces location in webcam
            encodeCurrFrame = face_recognition.face_encodings(imgS, facesCurrFrame)

            for encodeFace, faceloc in zip(encodeCurrFrame, facesCurrFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    y1, x2, y2, x1 = faceloc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), 2, cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)
                    markAttendance(name)
            if (cv2.waitKey(20) & 0xFF == ord('q')):
                break

            cv2.imshow('WebCam', img)
        cpp.release()
        return jsonify({"response" : 'hi this is python'})
    except KeyError:
        return jsonify({"response" : 'error'})

