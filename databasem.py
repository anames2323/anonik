import sqlite3


class Databasem:
    def __init__(self):
        self.connection = sqlite3.connect("databasem.db")
        self.cursor = self.connection.cursor()


    def add_queue_male(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `queue_male` (user_id) VALUES (?)", (user_id,))

    def delete_queue_male(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `queue_male` WHERE user_id = ?", (user_id,))

    def get_queue_male(self):
        with self.connection:
            queue = self.cursor.execute("SELECT * FROM `queue_male`").fetchmany(1)

            if bool(len(queue)):
                for row in queue:
                    return row[1]
            else:
                return False


    def create_chat_male(self, user_id, partner_id):
        if partner_id != 0:
            with self.connection:
                self.cursor.execute("INSERT INTO `chats_male` (user, partner) VALUES (?, ?)", (user_id, partner_id))
                return True

        return False

    def get_chat_male(self, user_id):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `chats_male` WHERE user = ? OR partner = ?", (user_id, user_id))

            for i in chat:
                return [i[0], i[1] if i[1] != user_id else i[2]]

            return False
    def delete_chat_male(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `chats_male` WHERE user = ? OR partner = ?", (user_id, user_id))

