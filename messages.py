import db


def create_message(user_id, room_id, content):
    sql = f"""
        INSERT INTO messages (user_id, room_id, content, time)
        VALUES ('{user_id}', '{room_id}','{content}', datetime('now'))
        """
    db.execute(sql)


def get_messages_by_room(room_id):
    sql = """SELECT users.username, messages.user_id, messages.content, messages.time
            FROM messages
            LEFT JOIN users on users.id = messages.user_id
            """
    return db.query(sql)