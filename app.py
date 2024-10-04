import os
import re
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='L!kh!@2004',
        database='mysql'
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        reg_no = request.form['registration_number']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        degree = request.form['degree']
        department = request.form['department']
        year_of_study = request.form['year_of_study']

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('student_register'))

        if len(phone_number) != 10:
            flash('Phone number must be exactly 10 digits.', 'danger')
            return redirect(url_for('student_register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('student_register'))

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = "SELECT * FROM student_profile WHERE email = %s OR phone_number = %s"
        cursor.execute(query, (email, phone_number))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('User already exists.', 'danger')
            cursor.close()
            db.close()
            return redirect(url_for('student_register'))

        insert_query = "INSERT INTO student_profile (full_name, reg_no, email, phone_number, gender, password_hash, degree, department, year_of_study) " \
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (
            full_name, reg_no, email, phone_number, gender, generate_password_hash(password),
            degree, department, year_of_study))
        db.commit()

        cursor.close()
        db.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('home'))

    return render_template('student_register.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        employee_id = request.form['employee_id']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))

        if len(phone_number) != 10:
            flash('Phone number must be exactly 10 digits.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = "SELECT * FROM Faculty_Profile WHERE email = %s OR phone_number = %s"
        cursor.execute(query, (email, phone_number))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('User already exists. Please log in.', 'danger')
            cursor.close()
            db.close()
            return redirect(url_for('login'))

        insert_query = "INSERT INTO Faculty_Profile (full_name, employee_id, email, phone_number, gender, password_hash) " \
                       "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (
            full_name, employee_id, email, phone_number, gender, generate_password_hash(password)))
        db.commit()

        cursor.close()
        db.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = "SELECT * FROM Faculty_Profile WHERE email = %s"
        cursor.execute(query, (email_or_username,))
        profile = cursor.fetchone()

        cursor.close()
        db.close()

        if profile and check_password_hash(profile['password_hash'], password):
            session['user_email'] = profile['email']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email/username and password.', 'danger')

    return render_template('login.html')


@app.route('/home')
def home():
    if 'user_email' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('forgot_password'))

        new_password_hash = generate_password_hash(new_password)

        db = get_db_connection()
        cursor = db.cursor()

        update_query = "UPDATE Faculty_Profile SET password_hash = %s WHERE email = %s"
        cursor.execute(update_query, (new_password_hash, email))
        db.commit()

        cursor.close()
        db.close()

        flash('Password reset successful! Please log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')  # Changed to the correct template


@app.route('/hall_ticket_generation', methods=['GET', 'POST'])
def hall_ticket_generation():
    return render_template('HallTicket_Generation.html')


@app.route('/verify_registration_number', methods=['POST'])
def verify_registration_number():
    data = request.get_json()
    reg_no = data.get('reg_no')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM student_profile WHERE reg_no = %s"
    cursor.execute(query, (reg_no,))
    student = cursor.fetchone()

    cursor.close()
    db.close()

    return jsonify({'exists': bool(student)})


@app.route('/generate_hall_ticket', methods=['POST'])
def generate_hall_ticket():
    reg_no = request.form['reg_no']

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    student_query = "SELECT * FROM student_profile WHERE reg_no = %s"
    cursor.execute(student_query, (reg_no,))
    student = cursor.fetchone()

    timetable_query = """
        SELECT subject, exam_date, exam_time
        FROM exam_timetable
        WHERE reg_no = %s
        ORDER BY exam_date, exam_time
    """
    cursor.execute(timetable_query, (reg_no,))
    timetable = cursor.fetchall()

    cursor.close()
    db.close()

    if student:
        return render_template('hall_ticket.html', student=student, timetable=timetable)
    else:
        flash('Registration number not found.', 'danger')
        return redirect(url_for('hall_ticket_generation'))


@app.route('/print_hall_ticket', methods=['POST'])
def print_hall_ticket():
    reg_no = request.form['reg_no']

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM student_profile WHERE reg_no = %s"
    cursor.execute(query, (reg_no,))
    student = cursor.fetchone()

    cursor.close()
    db.close()

    if student:
        return render_template('hall_ticket.html', student=student)
    else:
        flash('Registration number not found.', 'danger')
        return redirect(url_for('hall_ticket_generation'))


@app.route('/exam_attendance', methods=['GET', 'POST'])
def exam_attendance():
    if request.method == 'POST':
        qr_data = request.json.get('qr_data')

        if qr_data:
            student_id = qr_data.get('student_id')[:50]
            date = datetime.now().date()

            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute(
                    'INSERT INTO attendance (student_id, date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE date=%s',
                    (student_id, date, date))

                connection.commit()
                cursor.close()
                connection.close()

                return jsonify({'status': 'success', 'message': 'Attendance marked successfully!'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'error', 'message': 'Invalid QR code data!'})

    return render_template('Exam_Attendance.html')


@app.route('/subject_enrollment', methods=['GET', 'POST'])
def subject_enrollment():
    if request.method == 'POST':
        sub_code = request.form['sub_code']
        sub_name = request.form['sub_name']
        semester = request.form.get('semester')

        if not sub_code or not sub_name or not semester:
            flash('Subject Code, Subject Name, and Semester are all required.', 'danger')
            return redirect(url_for('subject_enrollment'))

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = "SELECT * FROM Subject WHERE sub_code = %s"
        cursor.execute(query, (sub_code,))
        existing_subject = cursor.fetchone()

        if existing_subject:
            flash('Subject already exists.', 'danger')
            cursor.close()
            db.close()
            return redirect(url_for('subject_enrollment'))

        insert_query = "INSERT INTO Subject (sub_code, sub_name, semester) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (sub_code, sub_name, semester))
        db.commit()

        cursor.close()
        db.close()

        flash('Subject enrolled successfully!', 'success')
        return redirect(url_for('subject_enrollment'))

    return render_template('Subject_Enrollment.html')


@app.route('/exam_time_table')
def exam_time_table():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM exam_timetable")
    timetable_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('Exam_TimeTable.html', timetable=timetable_data)


if __name__ == '__main__':
    app.run()
