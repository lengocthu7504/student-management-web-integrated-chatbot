from flask import Flask, render_template, request, redirect, url_for

import pandas as pd
import os

# os.add_dll_directory('C:\\Users\\lengo\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python312\\site-packages\\bin') 
import ibm_db

app = Flask(__name__)

# IBM DB2 connection setup
dsn_hostname = os.getenv('DB_HOST', '') # change this
dsn_uid = os.getenv('DB_UID', '')  # change this
dsn_pwd = os.getenv('DB_PWD', '')  # change this
dsn_port = os.getenv('DB_PORT', '')  # change this
dsn_database = "bludb"  # change if necessary
dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_protocol = "TCPIP"
dsn_security = "SSL"

dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd, dsn_security)

# Fetch students from DB2
def fetch_students():
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = "SELECT * FROM CB106"
        stmt = ibm_db.exec_immediate(conn, query)
        rows = []
        result = ibm_db.fetch_assoc(stmt)
        while result:
            rows.append(result)
            result = ibm_db.fetch_assoc(stmt)
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        print("Error fetching students from DB2: ", str(e))
        return None
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)

# Add a student to DB2
def add_student(name, birth_date, student_id, major):
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = """
        INSERT INTO CB106 ("Tên Sinh Viên", "Ngày Sinh", "Mã Số", "Chuyên Ngành")
        VALUES (?, ?, ?, ?)
        """
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.bind_param(stmt, 2, birth_date)
        ibm_db.bind_param(stmt, 3, student_id)
        ibm_db.bind_param(stmt, 4, major)
        ibm_db.execute(stmt)
    except Exception as e:
        print("Error adding student to DB2: ", str(e))
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)


# Delete a student from DB2
def delete_student(student_id):
    try:
        conn = ibm_db.connect(dsn, "", "")
        query = "DELETE FROM CB106 WHERE \"Mã Số\" = ?"
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt, 1, student_id)
        ibm_db.execute(stmt)
    except Exception as e:
        print("Error deleting student from DB2: ", str(e))
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)


# Main route to display student data and handle add/delete requests
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            birth_date = request.form['birth_date']
            student_id = request.form['student_id']
            major = request.form['major']
            # Add student to DB2
            add_student(name, birth_date, student_id, major)
        elif 'delete' in request.form:
            student_id = request.form['student_id']
            # Delete student from DB2
            delete_student(student_id)
        # After updating DB2, redirect to refresh the page with updated student list
        return redirect(url_for('index'))

    # Fetch updated student list from DB2 and display
    students = fetch_students()
    return render_template('index.html', students=students)

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
