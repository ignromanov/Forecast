import config
import sqlite3

class SQLiter:

    def __init__(self):
        self.conn = sqlite3.connect(config.MAIN_DB_NAME)
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

    def save_location(self, tg_id, latitude, longitude):
        self.c.execute("REPLACE INTO users_position VALUES ((SELECT user_id FROM Users WHERE tg_id = ?), ?, ?)",
                  (tg_id, latitude, longitude))
        self.conn.commit()

    def find_user(self, from_user):
        self.c.execute('SELECT user_id AS id, first_name, last_name FROM Users WHERE tg_id = ?', (from_user.id,))
        row = self.c.fetchone()
        if row is None:
            self.c.execute(
                'INSERT INTO Users (name, first_name, last_name, username, tg_id) VALUES (?, ?, ?, ?, ?)',
                (from_user.name, from_user.first_name, from_user.last_name,
                 from_user.username, from_user.id))
            result_dic = {'first_name': from_user.first_name, 'last_name': from_user.last_name}
            self.conn.commit()
        else:
            result_dic = {'first_name': row[1], 'last_name': row[2]}

        return result_dic

    def subscribe(self, tg_id):
        self.c.execute("REPLACE INTO subscribed VALUES ((SELECT user_id FROM Users WHERE tg_id = ?), ?)",
                  (tg_id, True))
        self.conn.commit()