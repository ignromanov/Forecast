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

    def get_user_location(self, tg_id):
        self.c.execute("SELECT latitude, longitude FROM users_position WHERE user_id in (SELECT user_id FROM Users WHERE tg_id = ?)",
                  (tg_id, ))
        row = self.c.fetchone()
        if row is None:
            print('Отсутсвует местоположение пользователя')
        else:
            return {'lat': row[0], 'lng': row[1]}

    def get_current_subscriptions(self, time, time_delta):
        self.c.execute('''SELECT tg_id, latitude, longitude 
                        from Users u 
                          LEFT JOIN users_position up 
                            on u.user_id = up.user_id 
                        where u.user_id in (select user_id 
                                          from subscribed 
                                          where subscribed and send_time BETWEEN time(?)-time(?) and time(?))''', (time, time_delta, time))
        result = []
        row = self.c.fetchone()
        while row != None:
            result.append(row)
            row = self.c.fetchone()

        return result

