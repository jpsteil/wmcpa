import csv
import os
import sqlite3
from dateutil.parser import parse

"""
read the input file
parse the records
insert into database
"""

BASE_PATH = os.path.join("/home", "jim", "dev", "py4web", "apps", "wmcpa")
INPUT_FILENAME = os.path.join(BASE_PATH, "scripts", "sessions.csv")
DATABASE_NAME = os.path.join(BASE_PATH, "databases", "storage.db")


def drop_tables(c):
    """
    Drop the listed tables

    Args:
        c (cursor): the cursor to use for database operations
    """
    for table in ["session", "room", "speaker"]:
        c.execute(f"DROP TABLE IF EXISTS {table}")


def create_tables(c):
    """
    Create the speaker, room and session tables

    Args:
        c (cursor): the cursor to use for database operations
    """
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
    """
    delete and recreate the tables
    read through the input file and repopulate the tables
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    drop_tables(c)
    create_tables(c)

    conn.commit()

    #  read through input file
    with open(os.path.join(INPUT_FILENAME), "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')

        for row in csv_reader:
            #  'row' is a list of the csv fields in the current
            start_time = row[0]
            session_name = row[1]
            session_description = row[2]
            speaker_first = row[3]
            speaker_last = row[4]
            speaker_company = row[5]
            speaker_title = row[6]
            speaker_bio = row[7]
            room = row[8]

            #  check for room
            room_id = None
            c.execute("SELECT id FROM room WHERE name = ?", [room])
            for room_id in c.fetchall():
                room_id = room_id[0]

            if not room_id:
                #  insert into the room table and get the new id
                c.execute("INSERT INTO room (name) VALUES(?)", [room])
                room_id = c.lastrowid

            #  check for speaker
            speaker_id = None
            c.execute(
                "SELECT id FROM speaker where first_name = ? and last_name = ?",
                [speaker_first, speaker_last],
            )
            for speaker_id in c.fetchall():
                speaker_id = speaker_id[0]

            if not speaker_id:
                #  insert into the speaker table and get the new id
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

            #  insert to the session table
            c.execute(
                'INSERT INTO session ("start_time", name, description, speaker, room) VALUES (?, ?, ?, ?, ?)',
                [
                    parse(start_time).strftime("%Y-%m-%d %H:%M:00"),
                    session_name,
                    session_description,
                    speaker_id,
                    room_id,
                ],
            )
    conn.commit()

    c.close()
    conn.close()


if __name__ == "__main__":
    import_data()
