from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="attendance_v2",
)

cursor = db.cursor()


@app.route("/")
def root():
    cursor.execute(
        "select prs_nbr, prs_name, prs_role, prs_active, prs_added from prs_mstr")
    data = cursor.fetchall()

    return render_template('index.html', data=data)


if __name__ == "__main__":
    app.run()
