from flask import Flask, render_template, request, redirect, url_for,session

app = Flask(__name__)
app.secret_key = "mysecretkey"

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == "admin@gmail.com" and password == "1234":
        session['user'] = email
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html',error="Invalid email or password",email=email)
    
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

if __name__ == '__main__':
    app.run(debug=True)