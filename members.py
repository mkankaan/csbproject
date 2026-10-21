import db


def add_member(user_id, room_id):
    sql = f"INSERT INTO members (user_id, room_id) VALUES ('{user_id}', '{room_id}')"
    db.execute(sql)


def get_by_room(room_id):
    sql = """SELECT members.user_id, users.username
            FROM members
            LEFT JOIN users ON users.id = members.user_id
            WHERE room_id = ?"""
    return db.query(sql, [room_id])


def remove_member(user_id, room_id):
    sql = f"DELETE FROM members WHERE user_id = {user_id} AND room_id = {room_id}"
    db.execute(sql)


def delete_by_room(room_id):
    sql = f"DELETE FROM members WHERE room_id = '{room_id}'"
    db.execute(sql)
