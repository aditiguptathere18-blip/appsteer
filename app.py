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
    if session['role'] == 'admin':
        return render_template('dashboard.html')
    else:
            return render_template('employee_dashboard.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))    
  
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
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
    else:
        cursor.execute(
            "SELECT * FROM attendance WHERE name=%s ORDER BY id DESC",
            (session['user'],)
        )

    data = cursor.fetchall()
    return render_template('view_attendance.html', data=data)

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
 
if __name__ == '__main__':
    app.run(debug=True)