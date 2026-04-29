from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIG (UPLOAD PATH)
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '..', 'uploads'))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# ===============================
# DB CONFIG (FROM ENV)
# ===============================
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432))
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ===============================
# SAFE TABLE CREATION
# ===============================
def create_table():
    try:
        conn = get_connection()
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
        conn.close()

        print("Table ready ✅")

    except Exception as e:
        print("DB connection failed:", e)

# ⚠️ Do NOT crash app if DB fails
create_table()

# ===============================
# FILE HANDLING
# ===============================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and file.filename != "":
        if not allowed_file(file.filename):
            raise Exception("Invalid file type")

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        return unique_name

    return None

# ===============================
# ROUTES
# ===============================

@app.route('/')
def home():
    return "Server running ✅"


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.form

        photo = save_file(request.files.get('photo'))
        id_proof = save_file(request.files.get('id_proof'))
        marksheet_10 = save_file(request.files.get('marksheet_10'))
        marksheet_12 = save_file(request.files.get('marksheet_12'))
        leaving_certificate = save_file(request.files.get('leaving_certificate'))
        payment_proof = save_file(request.files.get('payment_proof'))

        conn = get_connection()
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
            photo,
            id_proof,
            marksheet_10,
            marksheet_12,
            leaving_certificate,
            payment_proof
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/students')
def students():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM students ORDER BY id ASC")
        rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description]
        data = [dict(zip(columns, row)) for row in rows]

        cur.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===============================
# RUN (RENDER SAFE)
# ===============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)