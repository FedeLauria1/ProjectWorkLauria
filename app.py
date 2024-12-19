import hashlib
from flask import Flask, render_template, request, redirect, session, url_for, g, flash
import os
import sqlite3 as sq
from ast import literal_eval
from flask_mail import Mail, Message
from Utente import *
from Prenotazione import *
from db import *

app = Flask(__name__)

#Configuro email
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'fdec77fbb3da32'
app.config['MAIL_PASSWORD'] = '70cb8801b93640'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mail = Mail(app)

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()




"""def send_email(email,date,time,type):
    db = g.db
    if db is None:
        return False
    cur = db.cursor()
    cur.execute("SELECT id FROM bookings where email = ?", (email,))
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
  """          

def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("Devi essere loggato per accedere a questa pagina.", "warning")
            return redirect(url_for("login"))

        try:
            db = g.db
            cur = db.cursor()
            cur.execute("SELECT is_admin FROM users WHERE username = ?", (session["username"],))
            user = cur.fetchone()
            print(f"Query result: {user}")
            if user is None or user[0] != 1:
                flash("Accesso negato. Non sei autorizzato a visualizzare questa pagina.", "danger")
                return redirect(url_for("booking"))
        except Exception as e:
            print(f"Error during admin check: {e}")
            raise

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


    

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')


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
    date = request.form['date']
    time = request.form['time']

    full = Prenotazione.controllo_orario(date,time)
    if full == 0:
        Prenotazione.inserisci_prenotazione(session,date,time)
        flash(f"Prenotazione andata a buon fine! Ci vediamo il {date} alle ore {time}")
        #send_email(date,time,'SUCCESS')
    else:
        flash("Nella DATA/ORA inserita non è disponibile nessuno slot, ri-prenotare!", "info" )
    return redirect('/booking')

@app.post("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for("booking"))
    else:
        if request.method == "GET":
            return render_template('login.html')
        else:
            username = request.form["username"]
            password = request.form["password"]
            password = hashlib.sha256(password.encode()).hexdigest()
            db = g.db
            print(Utente.check_password(username,password))
            if Utente.check_password(username,password):
                session["username"] = username
                return redirect(url_for("booking"))
            else:
                flash("Credenziali ERRATE. Riprovare!", "info" )
                return redirect(url_for("login"))
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form["password"]
        email = request.form["email"]
        password = hashlib.sha256(password.encode()).hexdigest()
        new_utente = Utente(username,password,0,email)
        return redirect(url_for('login'))
    return render_template('register.html')
            
@app.route('/view_bookings')
@admin_required
def view_bookings():
    if 'username' in session:
        username = session["username"]
        bookings = Prenotazione.estraiPrenotazioni()
        return render_template('view_bookings.html', bookings=bookings,username=username)
    else:
        return redirect(url_for("login"))
    
@app.route('/view_bookings_user')
def view_bookings_user():
        if 'username' not in session:
            flash("Devi essere loggato per accedere a questa pagina.", "warning")
            return redirect(url_for("login"))
        bookings = Prenotazione.estraiPrenotazioni_u(session)
        return render_template('view_bookings_user.html', bookings=bookings,username=session["username"])
        

@app.route('/delete_booking', methods=['POST'])
def delete_booking_route():
    booking = request.form['booking']
    Prenotazione.cancella_prenotazione(booking)
    #send_email(id_booking[4],id_booking[2],id_booking[3],'CANCEL')
    return redirect('/booking')

if __name__ == '__main__':
    app.run(debug=True)
