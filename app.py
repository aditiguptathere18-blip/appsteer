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
        session['user'] = email
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html',error="Invalid email or password")
    
@app.route('/dashboard')
def dashboard():
        if 'user' in session:
          return render_template('dashboard.html')
        else:
            return redirect(url_for('login_page'))
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))      
  
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        name= request.form.get('name')
        date= request.form.get('date')
        status= request.form.get('status')

        cursor.execute(
            "INSERT INTO attendance(name,date,status) VALUES (%s, %s, %s)",
            (name, date, status)

    )
        conn.commit()
        return "Attendance Recorded Successfully"
    return render_template('attendance.html')

if __name__ == '__main__':
    app.run(debug=True)