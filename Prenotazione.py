from db import get_db
from Utente import *
from ast import literal_eval

class Prenotazione:
    def __init__(self,id_utente,date, hour):
        self.id_utente = id_utente
        self.date = date
        self.hour = hour
        self.salva_su_database()

    def salva_su_database(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO bookins (id_utente, date,hour) VALUES (?,?,?)', (self.id_utente, self.date, self.hour))
        db.commit()
    
    @staticmethod
    def estraiPrenotazioni():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username,date,hour,email FROM bookings join users on users.id = bookings.id_utente ORDER BY date ASC")
        books = cursor.fetchall()
        print(books)
        return books
    
    @staticmethod
    def estraiPrenotazioni_u(session):
        db = get_db()
        cursor = db.cursor()
        print(session["username"])
        cursor.execute("SELECT username,date,hour,email FROM bookings join users on users.id = bookings.id_utente where username = ? ORDER BY date ASC",(session["username"],))
        books = cursor.fetchall()
        print(books)
        return books
    
    @staticmethod
    def controllo_orario(time,date):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_utente FROM bookings where hour = ? and date = ?" , (time,date))
        full = cursor.fetchone()
        if full is None:
            return 0
        else:
            return 1
        
    @staticmethod
    def inserisci_prenotazione(session,date,time):
        db = get_db()
        cursor = db.cursor()
        utenti = Utente.get_dettagli_utenti(session["username"])
        cursor.execute("INSERT INTO bookings (id_utente,date,hour) VALUES (?,?,?);", (utenti['id'],date,time))
        db.commit()


    @staticmethod
    def cancella_prenotazione(booking):
        db = get_db()
        cursor = db.cursor()
        booking = literal_eval(booking)
        cursor.execute("""SELECT * FROM bookings JOIN users u 
                       ON u.id = bookings.id_utente WHERE u.username = ? 
                       AND date = ? AND HOUR = ? """,(booking[0],booking[1],booking[2]))
        
        books2 = cursor.fetchone()
        id_book = books2[0]
        cursor.execute("DELETE FROM bookings WHERE id_booking = ?", (id_book,))
        db.commit()
