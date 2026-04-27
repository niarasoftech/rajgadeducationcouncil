from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# PostgreSQL connection
conn = psycopg2.connect(
    host="db.ivcvxvuzlaujxraqqgdp.supabase.co",
    database="postgres",
    user="postgres",
    password="niarasoftech",
    port=5432
)

# ✅ Create table
def create_table():
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        candidate_name TEXT,
        dob TEXT,
        father_name TEXT,
        mother_name TEXT,
        email TEXT,
        mobile TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        school_10 TEXT,
        school_12 TEXT,
        marks TEXT,
        course TEXT,
        photo TEXT,
        id_proof TEXT,
        marksheet_10 TEXT,
        marksheet_12 TEXT,
        leaving_certificate TEXT,
        payment_proof TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()

create_table()


# ✅ Home route
@app.route('/')
def home():
    return "Server running ✅"


# ✅ Submit form
@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.form

        # 🔥 FILES
        photo = request.files.get('photo')
        id_proof = request.files.get('id_proof')
        marksheet_10 = request.files.get('marksheet_10')
        marksheet_12 = request.files.get('marksheet_12')
        leaving_certificate = request.files.get('leaving_certificate')
        payment_proof = request.files.get('payment_proof')

        # function to save files safely
        def save_file(file):
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                filename = str(datetime.now().timestamp()) + "_" + filename
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                return path
            return ""

        photo_path = save_file(photo)
        id_path = save_file(id_proof)
        m10_path = save_file(marksheet_10)
        m12_path = save_file(marksheet_12)
        lc_path = save_file(leaving_certificate)
        payment_path = save_file(payment_proof)

        # ✅ INSERT INTO DB
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students (
                candidate_name, dob, father_name, mother_name,
                email, mobile, address, city, state, pincode,
                school_10, school_12, marks, course,
                photo, id_proof, marksheet_10, marksheet_12,
                leaving_certificate, payment_proof
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('candidate_name'),
            data.get('dob'),
            data.get('father_name'),
            data.get('mother_name'),
            data.get('email'),
            data.get('mobile'),
            data.get('address'),
            data.get('city'),
            data.get('state'),
            data.get('pincode'),
            data.get('school_10'),
            data.get('school_12'),
            data.get('marks'),
            data.get('course'),
            photo_path,
            id_path,
            m10_path,
            m12_path,
            lc_path,
            payment_path
        ))

        conn.commit()
        cur.close()
        print("FORM HIT ✅")
        print(request.form)
        return jsonify({"message": "Admission Submitted Successfully ✅"})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ✅ Get all students
@app.route('/students')
def students():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)