from flask import Flask
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="attendance_v2",
)


@app.route("/")
def root():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
