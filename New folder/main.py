from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# PostgreSQL connection
conn = psycopg2.connect(
    host="dpg-d7gtsmi8qa3s73cpm4l0-a.virginia-postgres.render.com",
    database="rajgadeducation",
    user="rajgadeducation_user",
    password="kWi4Wo0EcQIlvaB43OX1DeG4AI7BsfMX",
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
    data = request.form

    # Files
    photo = request.files.get('photo')
    id_proof = request.files.get('id_proof')

    photo_path = ""
    id_path = ""

    if photo:
        photo_path = os.path.join(UPLOAD_FOLDER, photo.filename)
        photo.save(photo_path)

    if id_proof:
        id_path = os.path.join(UPLOAD_FOLDER, id_proof.filename)
        id_proof.save(id_path)

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (
            candidate_name, dob, father_name, mother_name,
            email, mobile, address, city, state, pincode,
            school_10, school_12, marks, course,
            photo, id_proof
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        id_path
    ))

    conn.commit()
    cur.close()

    return "Admission Submitted Successfully ✅"

# ✅ Get all students
@app.route('/students')
def students():
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True)