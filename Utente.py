import hashlib
from db import get_db

class Utente:
    def __init__(self, username, password, is_admin, email):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.email = email
        self.salva_su_database()

    def salva_su_database(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, password, is_admin, email) VALUES (?, ?, ?, ?)', 
                       (self.username, self.password, self.is_admin, self.email))
        db.commit()

    @staticmethod
    def get_dettagli_utenti(username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, is_admin, email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        return {"id": user[0], "is_admin": user[1], "email": user[2]}

    @staticmethod
    def estraiUtenti():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

    @staticmethod
    def estraiUtente(username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

    @staticmethod
    def check_password(username, password):
        print(username)
        print(password)
        user = Utente.estraiUtente(username)
        print("User 0")
        print(user[0])
        print(user)
        if user is None:
            return False
        
        return user[2] == password

    
