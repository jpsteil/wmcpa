import csv
import os
import sqlite3
from dateutil.parser import parse

BASE_PATH = os.path.join("/home", "jim", "dev", "py4web", "apps", "wmcpa")
INPUT_FILENAME = os.path.join(BASE_PATH, "scripts", "sessions.csv")
DATABASE_NAME = os.path.join(BASE_PATH, "databases", "wmcpa_live.db")


def drop_tables(c):
    for table in ["session", "room", "speaker"]:
        c.execute(f"DROP TABLE IF EXISTS {table}")


def create_tables(c):
    c.execute(
        """
    CREATE TABLE speaker 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
    first_name CHAR(20), 
    last_name CHAR(20), 
    bio TEXT, 
    title CHAR(100), 
    company CHAR(100))
    """
    )

    c.execute(
        """
    CREATE TABLE room 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name CHAR(100))
    """
    )

    c.execute(
        """
    CREATE TABLE session 
    ("id" INTEGER PRIMARY KEY AUTOINCREMENT, 
    "start_time" TIMESTAMP, 
    "name" CHAR(100), 
    "description" TEXT, 
    "speaker" INTEGER REFERENCES speaker (id) ON DELETE CASCADE ON UPDATE CASCADE, 
    "room" INTEGER REFERENCES room (id) ON DELETE CASCADE ON UPDATE CASCADE)
    """
    )


def import_data():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    drop_tables(c)
    create_tables(c)

    conn.commit()

    with open(INPUT_FILENAME, "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')

        rooms = dict()
        speakers = dict()
        for row in csv_reader:
            start_time = row[0]
            session_name = row[1]
            session_description = row[2]
            speaker_first = row[3]
            speaker_last = row[4]
            speaker_company = row[5]
            speaker_title = row[6]
            speaker_bio = row[7]
            room = row[8]

            room_id = rooms.get(room)
            if not room_id:
                c.execute("INSERT INTO room (name) VALUES (?)", [room])
                room_id = c.lastrowid
                rooms[room] = room_id

            speaker_id = speakers.get(f"{speaker_first} {speaker_last}")
            if not speaker_id:
                c.execute(
                    "INSERT INTO speaker (first_name, last_name, company, title, bio) VALUES (?, ?, ?, ?, ?)",
                    [
                        speaker_first,
                        speaker_last,
                        speaker_company,
                        speaker_title,
                        speaker_bio,
                    ],
                )
                speaker_id = c.lastrowid
                speakers[f"{speaker_first} {speaker_last}"] = speaker_id

            c.execute(
                "INSERT INTO session (start_time, name, description, speaker, room) VALUES (?, ?, ?, ?, ?)",
                [start_time, session_name, session_description, speaker_id, room_id],
            )
        conn.commit()

    c.close()
    conn.close()


if __name__ == "__main__":
    import_data()
