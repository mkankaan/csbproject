import db
import members


def create_room(room_name, user_id):
    sql = f"INSERT INTO rooms (name, owner) VALUES ('{room_name}', '{user_id}')"
    db.execute(sql)

    new_room_id = last_room_by_user(user_id)
    members.add_member(user_id, new_room_id)


def get_user_rooms(user_id):
    sql = """SELECT rooms.id, rooms.owner, rooms.name, members.joined as joined
            FROM rooms
            LEFT JOIN users ON rooms.owner = users.id
            LEFT JOIN members ON rooms.id = members.room_id
            WHERE members.user_id = ?"""
    return db.query(sql, [user_id])


def get_room(room_id):
    sql = "SELECT id, name, owner FROM rooms WHERE id = ?"
    result = db.query(sql, [room_id])
    return result[0] if result else None


# workaround for lastrowid which didn't seem to work with executescript
def last_room_by_user(user_id):
    sql = """SELECT id
             FROM rooms
             WHERE owner = ?
             ORDER BY id DESC
             LIMIT 1"""
    result = db.query(sql, [user_id])
    return result[0][0] if result else None