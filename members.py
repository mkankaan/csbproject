import db


def add_member(user_id, room_id):
    sql = f"SELECT * FROM members WHERE user_id = {user_id} AND room_id = {room_id}"
    result = db.query(sql)


    """
    FLAW 2 FIX:
    sql = "SELECT * FROM members WHERE user_id = ? AND room_id = ?"
    result = db.query(sql, [user_id, room_id])
    """

    already_member = True if result else False

    if not already_member:
        sql = f"INSERT INTO members (user_id, room_id) VALUES ('{user_id}', '{room_id}')"
        db.execute(sql)

        """
        FLAW 2 FIX:
        sql = f"INSERT INTO members (user_id, room_id) VALUES (?, ?)"
        db.execute(sql, [user_id, room_id])
        """


def get_by_room(room_id):
    sql = """SELECT members.user_id, users.username
            FROM members
            LEFT JOIN users ON users.id = members.user_id
            WHERE room_id = ?"""
    return db.query(sql, [room_id])


def remove_member(user_id, room_id):
    sql = f"DELETE FROM members WHERE user_id = {user_id} AND room_id = {room_id}"
    db.execute(sql)

    """
    FLAW 2 FIX:
    sql = "DELETE FROM members WHERE user_id = ? AND room_id = ?"
    db.execute(sql, [user_id, room_id])
    """


def delete_by_room(room_id):
    sql = f"DELETE FROM members WHERE room_id = '{room_id}'"
    db.execute(sql)

    """
    FLAW 2 FIX:
    sql = "DELETE FROM members WHERE room_id = ?"
    db.execute(sql, [room_id])
    """
