import os
from datetime import datetime
import face_recognition
import cv2
import numpy as np
import mysql.connector
from datetime import date

path = 'static/uploads'
images = []
classNames = []
myList = os.listdir(path)
cap = cv2.VideoCapture(0)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="attendance_v2",
)

cursor = db.cursor()

for cls in myList:
    curImg = cv2.imread(f'{path}/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    # with open('Attendance.csv', 'r+') as f:
    #     myDataList = f.readlines()
    #     nameList = []
    #     for line in myDataList:
    #         entry = line.split(',')
    #         nameList.append(entry[0])
    #     if name not in nameList:
    #         now = datetime.now()
    #         dtString = now.strftime('%H:%M:%S')
    #         f.writelines(f'\n{name},{dtString}')

    cursor.execute("""
        INSERT INTO `accs_hist` (accs_date, accs_prsn) 
        VALUES
        ('{}', '{}')
        """.format(str(date.today()), name))
    db.commit()


def capture_photo(name):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    ret, jpeg = cv2.imencode('.jpg', frame)
    cv2.imwrite("static/uploads/"+name+".jpg", frame)
    return jpeg


encodeListKnown = findEncodings(images)


def recognition():
    while True:
        success, frame = cap.read()
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurrFrame = face_recognition.face_locations(imgS)
        encodeCurrFrame = face_recognition.face_encodings(imgS, facesCurrFrame)

        for encodeFace, faceLoc in zip(encodeCurrFrame, facesCurrFrame):
            matches = face_recognition.compare_faces(
                encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(
                encodeListKnown, encodeFace)
            if len(faceDis) == 0:
                continue
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2),
                              (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1+6, y2-6),
                            cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                markAttendance(name)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
