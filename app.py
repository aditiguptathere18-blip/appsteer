from flask import Flask, render_template, request, redirect, url_for,session
import psycopg2
app = Flask(__name__)
app.secret_key = "mysecretkey"

conn = psycopg2.connect(
    host="localhost",
    database="attendance_db",
    user="postgres",
    password="jessie32"
)

cursor = conn.cursor()

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute(
        "SELECT * FROM public.users WHERE email=%s AND password=%s",(email, password)
    )
    user = cursor.fetchone()

    if user:
        session['user'] = user[1]
        session['role'] = user[3]
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html',error="Invalid email or password")
    
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect(url_for('login_page'))

    user_email = session['user']

    # TOTAL ATTENDANCE
    if session['role'] == 'admin':

        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM productivity")
        total_productivity = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(duration),0)
            FROM productivity
        """)
        total_duration = cursor.fetchone()[0]

        return render_template(
            'dashboard.html',
            total_attendance=total_attendance,
            total_productivity=total_productivity,
            total_users=total_users,
            total_duration=total_duration
        )

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE name=%s
        """, (user_email,))
        total_attendance = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM productivity
            WHERE employee_email=%s
        """, (user_email,))
        total_productivity = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(duration),0)
            FROM productivity
            WHERE employee_email=%s
        """, (user_email,))
        total_duration = cursor.fetchone()[0]

        return render_template(
            'employee_dashboard.html',
            total_attendance=total_attendance,
            total_productivity=total_productivity,
            total_duration=total_duration
        )    
  
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        name= session['user']
        date= request.form.get('date')
        status= request.form.get('status')
        latitude= request.form.get('latitude')
        longitude= request.form.get('longitude')

        cursor.execute(
            "SELECT * FROM attendance WHERE name=%s AND date=%s",
            (name, date)
        )
        existing = cursor.fetchone()
        if existing:
            return "Attendance already marked for today"

        cursor.execute(
            "INSERT INTO attendance(name,date,status,latitude,longitude) VALUES (%s, %s, %s, %s, %s)",
            (name, date, status, latitude, longitude)

    )
        conn.commit()
        return redirect(url_for('dashboard'))
    return render_template('attendance.html')

@app.route('/view_attendance')
def view_attendance():

    if 'user' not in session:
        return redirect(url_for('login_page'))

    selected_date = request.args.get('date')

    # ADMIN
    if session['role'] == 'admin':

        if selected_date:

            cursor.execute("""
                SELECT * FROM attendance
                WHERE date=%s
                ORDER BY id DESC
            """, (selected_date,))

        else:

            cursor.execute("""
                SELECT * FROM attendance
                ORDER BY id DESC
            """)

    # EMPLOYEE
    else:

        if selected_date:

            cursor.execute("""
                SELECT * FROM attendance
                WHERE name=%s
                AND date=%s
                ORDER BY id DESC
            """, (
                session['user'],
                selected_date
            ))

        else:

            cursor.execute("""
                SELECT * FROM attendance
                WHERE name=%s
                ORDER BY id DESC
            """, (session['user'],))

    data = cursor.fetchall()

    return render_template(
        'view_attendance.html',
        data=data
    )

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM attendance WHERE id=%s",(id,))
    conn.commit()
    return redirect(url_for('view_attendance'))

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        date=request.form.get('date')
        status=request.form.get('status')

        cursor.execute(
            "UPDATE attendance SET date=%s, status=%s WHERE id=%s",
            (date,status,id)
        )
        conn.commit()
        return redirect(url_for('view_attendance'))
    cursor.execute("SELECT * FROM attendance WHERE id=%s",(id,))
    record=cursor.fetchone()
    return render_template('edit_attendance.html', record=record)

@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if 'user' not in session or session['role'] != 'admin':
        return "Access Denied"
    if request.method == 'POST':
        email= request.form.get('email')
        password= request.form.get('password')

        cursor.execute(
            "INSERT INTO users (email,password,role) VALUES (%s, %s, %s)",
            (email,password,'employee')
        )
        conn.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_user.html')

@app.route('/view_users')
def view_users():
    if 'user' not in session or session['role']!= 'admin':
        return "Access Denied"
    
    cursor.execute("SELECT * FROM users")
    users= cursor.fetchall()
    return render_template('view_users.html', users=users)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if 'user' not in session or session['role']!= 'admin':
        return "Access Denied"
    
    cursor.execute("SELECT role FROM users  WHERE id=%s", (id,))
    user=cursor.fetchone()

    if user and user[0] == 'admin':
        return "Admin cannot be deleted"
    
    cursor.execute(
        "DELETE FROM users WHERE id=%s",(id,))
    conn.commit()
    return redirect(url_for('view_users')
    )
    
@app.route('/productivity') 
def productivity():
    if'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('productivity.html')

@app.route("/submit_productivity", methods=["POST"])
def submit_productivity():

    if "user" not in session:
        return redirect("/")

    employee_email = session["user"]

    client_names = request.form.getlist("client_name[]")
    type_of_activity = request.form.getlist("type_of_activity[]")
    exact_nature = request.form.getlist("exact_nature[]")
    policy_number = request.form.getlist("policy_number[]")
    no_cases = request.form.getlist("no_cases[]")
    sum_assured = request.form.getlist("sum_assured[]")
    decision = request.form.getlist("decision[]")
    duration = request.form.getlist("duration[]")
    remarks = request.form.getlist("remarks[]")
    activity_date = request.form.getlist("activity_date[]")

    cur = cursor

    for i in range(len(client_names)):

        cur.execute("""
            INSERT INTO productivity (
                employee_email,
                client_name,
                type_of_activity,
                exact_nature,
                policy_number,
                no_cases,
                sum_assured,
                decision,
                duration,
                remarks,
                activity_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            employee_email,

            client_names[i] if i < len(client_names) else "",

            type_of_activity[i] if i < len(type_of_activity) else "",

            exact_nature[i] if i < len(exact_nature) else "",

            policy_number[i] if i < len(policy_number) else "",

            no_cases[i] if i < len(no_cases) else 0,

            sum_assured[i] if i < len(sum_assured) else 0,

            decision[i] if i < len(decision) else "",

            duration[i] if i < len(duration) else 0,

            remarks[i] if i < len(remarks) else "",

            activity_date[i] if i < len(activity_date) else None
        ))

    conn.commit()

    return "Productivity Submitted Successfully"

@app.route('/view_productivity')
def view_productivity():

    if 'user' not in session:
        return redirect(url_for('login_page'))

    selected_date = request.args.get('date')

    # ADMIN
    if session['role'] == 'admin':

        if selected_date:

            cursor.execute("""
                SELECT * FROM productivity
                WHERE activity_date=%s
                ORDER BY id DESC
            """, (selected_date,))

        else:

            cursor.execute("""
                SELECT * FROM productivity
                ORDER BY id DESC
            """)

    # EMPLOYEE
    else:

        if selected_date:

            cursor.execute("""
                SELECT * FROM productivity
                WHERE employee_email=%s
                AND activity_date=%s
                ORDER BY id DESC
            """, (
                session['user'],
                selected_date
            ))

        else:

            cursor.execute("""
                SELECT * FROM productivity
                WHERE employee_email=%s
                ORDER BY id DESC
            """, (session['user'],))

    data = cursor.fetchall()

    return render_template(
        'view_productivity.html',
        data=data
    )
                        
@app.route('/edit_productivity/<int:id>', methods=['GET', 'POST'])
def edit_productivity(id):

    if 'user' not in session:
        return redirect(url_for('login_page'))

    cursor.execute(
        "SELECT * FROM productivity WHERE id=%s",
        (id,)
    )

    record = cursor.fetchone()

    if request.method == 'POST':

        decision = request.form.get('decision')

        duration = request.form.get('duration')

        remarks = request.form.get('remarks')

        cursor.execute("""
            UPDATE productivity
            SET decision=%s,
                duration=%s,
                remarks=%s
            WHERE id=%s
        """, (
            decision,
            duration,
            remarks,
            id
        ))

        conn.commit()

        return redirect(url_for('view_productivity'))

    return render_template(
        'edit_productivity.html',
        record=record
    )

@app.route('/delete_productivity/<int:id>')
def delete_productivity(id):

    if 'user' not in session:
        return redirect(url_for('login_page'))

    cursor.execute(
        "SELECT * FROM productivity WHERE id=%s",
        (id,)
    )

    record = cursor.fetchone()

    # EMPLOYEE CAN DELETE ONLY OWN RECORD
    if session['role'] != 'admin':

        if record[1] != session['user']:
            return "Access Denied"

    cursor.execute(
        "DELETE FROM productivity WHERE id=%s",
        (id,)
    )

    conn.commit()

    return redirect(url_for('view_productivity'))

@app.route('/logout')
def logout():

    session.pop('user', None)

    session.pop('role', None)

    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)