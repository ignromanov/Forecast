import sqlite3


def find_sender_user(update):
    conn = sqlite3.connect("local.db")
    c = conn.cursor()
    c.execute('SELECT user_id AS id, first_name, last_name FROM Users WHERE tg_id = ?', (update.message.from_user.id,))
    row = c.fetchone()
    if row is None:
        with update.message.from_user as u:
            c.execute(
                'INSERT INTO Users (name, first_name, last_name, username, tg_id) VALUES (?, ?, ?, ?, ?)',
                (u.name, update.message.from_user.first_name, update.message.from_user.last_name,
                 update.message.from_user.username, update.message.from_user.id))
            result_dic = {'first_name': u.first_name, 'last_name': u.last_name}
        conn.commit()
    else:
        result_dic = {'first_name': row[1], 'last_name': row[2]}

    conn.close()

    return result_dic


