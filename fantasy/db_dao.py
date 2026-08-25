import sqlite3

DB_NAME = "fantasy.db"


# users

def new_user(p_email, p_display_name, p_password, p_role):

    query = "INSERT INTO users (email, display_name, password, role) VALUES (?,?,?,?)"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_email, p_display_name, p_password, p_role))

    conn.commit()
    cursor.close()
    conn.close()


def get_user_by_email_and_role(p_email, p_role):

    query = "SELECT * FROM users WHERE users.email = ? AND users.role = ?"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_email, p_role))

    db_user = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_user


def get_user_by_id(p_id):

    query = "SELECT * FROM users WHERE users.id = ?"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    db_user = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_user


def get_adventurer_by_display_name(p_display_name):

    query = "SELECT * FROM users WHERE users.display_name = ? COLLATE NOCASE AND users.role = 'adventurer'"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_display_name,))

    db_user = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_user


def get_adventurers():

    query = "SELECT * FROM users WHERE users.role = 'adventurer' ORDER BY users.display_name"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)

    db_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_users


# quests

def new_quest(p_title, p_duration_minutes, p_type, p_difficulty, p_description, p_image):

    query = "INSERT INTO quests (title, duration_minutes, type, difficulty, description, image) VALUES (?,?,?,?,?,?)"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_title, p_duration_minutes, p_type, p_difficulty, p_description, p_image))

    conn.commit()
    cursor.close()
    conn.close()


def get_quests():

    query = "SELECT * FROM quests ORDER BY quests.title"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)

    db_quests = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_quests


def get_quest_by_id(p_id):

    query = "SELECT * FROM quests WHERE quests.id = ?"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    db_quest = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_quest


# quest sessions

def new_session(p_id_quest, p_day, p_start_time, p_location):

    query = "INSERT INTO quest_sessions (id_quest, day, start_time, location) VALUES (?,?,?,?)"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id_quest, p_day, p_start_time, p_location))

    conn.commit()
    cursor.close()
    conn.close()


def get_sessions():

    query = """SELECT quest_sessions.id, quest_sessions.id_quest, quest_sessions.day,
                      quest_sessions.start_time, quest_sessions.location,
                      quests.title, quests.duration_minutes, quests.type,
                      quests.difficulty, quests.image
               FROM quest_sessions, quests
               WHERE quest_sessions.id_quest = quests.id
               ORDER BY quest_sessions.day, quest_sessions.start_time"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)

    db_sessions = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_sessions


def get_session_by_id(p_id):

    query = """SELECT quest_sessions.id, quest_sessions.id_quest, quest_sessions.day,
                      quest_sessions.start_time, quest_sessions.location,
                      quests.title, quests.duration_minutes, quests.type,
                      quests.difficulty, quests.image, quests.description
               FROM quest_sessions, quests
               WHERE quest_sessions.id_quest = quests.id AND quest_sessions.id = ?"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    db_session = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_session


def get_sessions_by_day_and_location(p_day, p_location):

    query = """SELECT quest_sessions.id, quest_sessions.day, quest_sessions.start_time,
                      quest_sessions.location, quests.duration_minutes, quests.title
               FROM quest_sessions, quests
               WHERE quest_sessions.id_quest = quests.id
                 AND quest_sessions.day = ? AND quest_sessions.location = ?"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_day, p_location))

    db_sessions = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_sessions


def update_session(p_id, p_day, p_start_time, p_location):

    query = "UPDATE quest_sessions SET day = ?, start_time = ?, location = ? WHERE id = ?"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_day, p_start_time, p_location, p_id))

    conn.commit()
    cursor.close()
    conn.close()


def delete_session(p_id):

    query = "DELETE FROM quest_sessions WHERE id = ?"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    conn.commit()
    cursor.close()
    conn.close()


#  participations

def new_participation(p_id_session, p_id_user, p_role_category, p_places):

    query = "INSERT INTO participations (id_session, id_user, role_category, places, status) VALUES (?,?,?,?,'active')"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session, p_id_user, p_role_category, p_places))

    conn.commit()
    cursor.close()
    conn.close()


def get_participation_by_id(p_id):

    query = "SELECT * FROM participations WHERE participations.id = ?"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id,))

    db_participation = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_participation


def get_participation_by_session_and_user(p_id_session, p_id_user):

    query = "SELECT * FROM participations WHERE participations.id_session = ? AND participations.id_user = ?"

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session, p_id_user))

    db_participation = cursor.fetchone()

    cursor.close()
    conn.close()

    return db_participation


def get_participations_by_user(p_id_user):

    query = """SELECT participations.id, participations.id_session, participations.role_category,
                      participations.places, participations.status,
                      quest_sessions.day, quest_sessions.start_time, quest_sessions.location,
                      quests.title, quests.duration_minutes
               FROM participations, quest_sessions, quests
               WHERE participations.id_session = quest_sessions.id
                 AND quest_sessions.id_quest = quests.id
                 AND participations.id_user = ?
               ORDER BY quest_sessions.day, quest_sessions.start_time"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id_user,))

    db_participations = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_participations


def get_active_participations_by_session(p_id_session):

    query = """SELECT participations.id, participations.role_category, participations.places,
                      users.display_name, users.email
               FROM participations, users
               WHERE participations.id_user = users.id
                 AND participations.id_session = ?
                 AND participations.status = 'active'
               ORDER BY participations.role_category, users.display_name"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session,))

    db_participations = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_participations


def get_places_taken_by_session(p_id_session):

    query = """SELECT role_category, SUM(places) AS taken
               FROM participations
               WHERE id_session = ? AND status = 'active'
               GROUP BY role_category"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session,))

    db_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_rows


def count_active_participations_by_session(p_id_session):

    query = "SELECT COUNT(*) FROM participations WHERE id_session = ? AND status = 'active'"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session,))

    number = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return number


def count_active_participations_by_user(p_id_user):

    query = "SELECT COUNT(*) FROM participations WHERE id_user = ? AND status = 'active'"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id_user,))

    number = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return number


def update_participation(p_id, p_role_category, p_places, p_status):

    query = "UPDATE participations SET role_category = ?, places = ?, status = ? WHERE id = ?"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_role_category, p_places, p_status, p_id))

    conn.commit()
    cursor.close()
    conn.close()


def delete_participations_by_session(p_id_session):

    query = "DELETE FROM participations WHERE id_session = ?"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query, (p_id_session,))

    conn.commit()
    cursor.close()
    conn.close()


def get_active_participations():

    query = """SELECT participations.id, participations.id_session, participations.id_user,
                      participations.role_category, participations.places,
                      quest_sessions.day, quest_sessions.start_time, quest_sessions.location,
                      quests.title, quests.type
               FROM participations, quest_sessions, quests
               WHERE participations.id_session = quest_sessions.id
                 AND quest_sessions.id_quest = quests.id
                 AND participations.status = 'active'"""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)

    db_participations = cursor.fetchall()

    cursor.close()
    conn.close()

    return db_participations
