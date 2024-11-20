import hashlib
from flask import Flask, render_template, request, redirect, session, url_for, g, flash
import os
import sqlite3 as sq
from ast import literal_eval
from flask_mail import Mail, Message

app = Flask(__name__)

#Configuro email
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'fdec77fbb3da32'
app.config['MAIL_PASSWORD'] = '70cb8801b93640'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def check_time(db,time,date):
    if db is None:
        return False
    
    cur = db.cursor()
    cur.execute("SELECT id FROM books where hour = ? and date = ?" , (time,date))
    full = cur.fetchone()
    if full is None:
        return 0
    else:
        return 1
    
def write_booking2(db,name,date,time,email):
    if db is None:
        return False

    cur = db.cursor()
    cur.execute("INSERT INTO books (name,date,hour,email) VALUES (?,?,?,?);", (name,date,time,email))
    db.commit()

def delete_booking2(db,id):
    if db is None:
        return False
    print(id)
    cur = db.cursor()
    cur.execute("DELETE FROM books WHERE id = ?", (id,))
    db.commit()

def send_email(email,date,time,type):
    db = g.db
    if db is None:
        return False
    cur = db.cursor()
    cur.execute("SELECT id FROM books where email = ?", (email,))
    id = cur.fetchone()
    id_b = id[0]

    if type == 'SUCCESS':
        msg = Message(subject='Prenotazione effettuata!', sender='barber@hotmail.com', recipients=[email])
        msg.body = f"Prenotazione andata a buon fine! Ci vediamo il {date} alle ore {time}. Per modificare la prenotazione clicca qui: http://127.0.0.1:5000/view_bookings_user/{id_b}"
    if type == 'CANCEL':
        msg = Message(subject='Prenotazione cancellata!', sender='barber@hotmail.com', recipients=[email])
        msg.body = f"La tua prenotazione in data: {date} alle ore {time} è stata cancellata da un operatore!"

    mail.send(msg)
    return "Message sent!"
            

def check_password(db,username, password):
    if db is None:
        return False

    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    print(user)
    if user is None:
        return False
    return user[0] == password

def read_book2(db):
    if db is None:
        return False
    cur = db.cursor()
    cur.execute("SELECT id,name,date,hour,email FROM books ORDER BY date ASC")
    books = cur.fetchall()
    return books

def read_book_user(db,id_book):
    if db is None:
        return False
    cur = db.cursor()
    cur.execute("SELECT id,name,date,hour,email FROM books where ID = ?", (id_book,))
    books = cur.fetchall()
    return books
    

@app.route('/')
def index():
    return render_template('index.html')


# Funzione per aprire il database prima di ogni richiesta
@app.before_request
def before_request():
    db = sq.connect("database.db")
    g.db = db

# Funzione per chiudere il database dopo ogni richiesta
@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    date = request.form['date']
    time = request.form['time']
    email = request.form['email']
    db = g.db
    full = check_time(db,time,date)
    if full == 0:
        write_booking2(db,name,date,time,email)
        flash(f"Prenotazione andata a buon fine! Ci vediamo il {date} alle ore {time} ")
        send_email(email,date,time,'SUCCESS')

    else:
        flash("Nella DATA/ORA inserita non è disponibile nessuno slot, ri-prenotare!", "info" )
    return redirect('/')

@app.post("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for("view_bookings"))
    else:
        if request.method == "GET":
            return render_template('login.html')
        else:
            username = request.form["username"]
            password = request.form["password"]
            password = hashlib.sha256(password.encode()).hexdigest()
            db = g.db
            if check_password(db,username, password):
                session["username"] = username
                return redirect(url_for("view_bookings"))
            else:
                flash("Credenziali ERRATE. Riprovare!", "info" )
                return redirect(url_for("login"))
        
            
@app.route('/view_bookings')
def view_bookings():
    if 'username' in session:
        username = session["username"]
        db = g.db
        bookings = read_book2(db)
        return render_template('view_bookings.html', bookings=bookings,username=username)
    else:
        return redirect(url_for("login"))
    
@app.route('/view_bookings_user/<int:id_book>')
def view_bookings_user(id_book: int):
        db = g.db
        bookings = read_book_user(db,id_book)
        return render_template('view_bookings_user.html', bookings=bookings)
        

@app.route('/delete_booking', methods=['POST'])
def delete_booking_route():
    booking = request.form['booking']
    id_booking = literal_eval(booking)
    db = g.db
    print(id_booking)
    delete_booking2(db,id_booking[0])
    #send_email(id_booking[4],id_booking[2],id_booking[3],'CANCEL')
    return redirect('/view_bookings')

if __name__ == '__main__':
    app.run(debug=True)
