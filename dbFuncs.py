import hashlib
import sqlite3

def checkPassword(hashedPassword, userPassword):
    return hashedPassword == hashlib.md5(userPassword.encode()).hexdigest()

def validate(username, password):
    conn = sqlite3.connect('static/user.db')
    completion = False
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users")
        rows = cur.fetchall()
        for row in rows:
            dbUser = row[0]
            dbPass = row[1]
            if dbUser == username:
                completion = checkPassword(dbPass, password)
    return completion

def isNewUsername(username):
    conn = sqlite3.connect('static/user.db')
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT username FROM Users")
        dbUsernames = map(lambda x: x[0], cur.fetchall())
        isNewUsername = username not in dbUsernames
    return isNewUsername

def addNewUser(username, password):
    conn = sqlite3.connect('static/user.db')
    with conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Users VALUES (?, ?)", (username, hashlib.md5(password.encode()).hexdigest()))

def changeUsername(oldUsername, newUsername):
    conn = sqlite3.connect('static/user.db')
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=?", (oldUsername,))
        hashedPassword = cur.fetchall()[0][1]
        cur.execute("DELETE FROM Users WHERE username=?", (oldUsername,))
        cur.execute("INSERT INTO Users VALUES (?, ?)", (newUsername, hashedPassword))
