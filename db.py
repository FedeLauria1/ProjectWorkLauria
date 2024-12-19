from flask import g
import sqlite3 as sq

DATABASE = "database.sql"

def get_db():
    if 'db' not in g:
        g.db = sq.connect(DATABASE)
        g.db.row_factory = sq.Row  # Facoltativo: per accedere ai risultati come dizionari
    return g.db