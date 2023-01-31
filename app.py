from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import mysql.connector
import module as md
import pandas as pd

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
    cursor.execute("""
        SELECT prs_nbr, prs_name, prs_role, prs_active, prs_added
        FROM prs_mstr
        """)
    data = cursor.fetchall()
    return render_template('index.html', data=data)


@app.route('/add_person')
def add_person():
    cursor.execute("""
        SELECT ifnull(max(prs_nbr) + 1, 101)
        FROM prs_mstr
        """)
    row = cursor.fetchone()
    nbr = row[0]
    return render_template('add_person.html', newnbr=int(nbr))


@app.route('/add_person_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    addprsn_submit.prsname = request.form.get('txtname')
    prsrole = request.form.get('optrole')

    cursor.execute("""
        INSERT INTO `prs_mstr`
        (`prs_nbr`, `prs_name`, `prs_role`)
        VALUES
        ('{}', '{}', '{}')
    """.format(prsnbr, addprsn_submit.prsname, prsrole))

    db.commit()
    return redirect(url_for('capture_photo_page', prs=prsnbr))


@app.route('/capture_photo/<prs>')
def capture_photo_page(prs):
    return render_template('capture_photo.html', prs=prs)


@app.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    return Response(md.capture_photo(addprsn_submit.prsname, nbr).tobytes(), mimetype='image/jpeg')


@app.route('/video_feed')
def video_feed():
    return Response(md.recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/fr_page')
def fr_page():
    cursor.execute("select a.accs_prsn, b.prs_name, b.prs_role, a.accs_added "
                   "  from accs_hist a "
                   "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
                   " where a.accs_date = curdate() "
                   " order by 1 desc")
    data = cursor.fetchall()
    table = pd.read_csv("Attendance.csv")
    table = table.to_html(classes='table table-hover')
    return render_template('fr_page.html', data=data, table=table)


@app.route('/countTodayScan')
def countTodayScan():
    cursor.execute("""
                SELECT COUNT(*)
                FROM accs_hist
                WHERE accs_date = curdate() 
                """)
    row = cursor.fetchone()
    rowcount = row[0]
    return jsonify({'rowcount': rowcount})


@app.route('/loadData', methods=['GET', 'POST'])
def loadData():
    data = pd.read_csv("Attendance.csv")
    data = data.to_json()
    print(data)
    # db = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     passwd="",
    #     database="attendance_v2",
    # )

    # cursor = db.cursor()

    # cursor.execute("""
    #     SELECT DISTINCT a.accs_prsn, b.prs_name, b.prs_role, date_format(a.accs_added, '%H:%i:%s')
    #     FROM accs_hist a
    #     LEFT JOIN prs_mstr b ON a.accs_prsn = b.prs_nbr
    #     WHERE a.accs_date = curdate()
    #     ORDER BY 1 DESC
    # """)
    # data = cursor.fetchall()

    return jsonify(response=data)


if __name__ == "__main__":
    app.run()
