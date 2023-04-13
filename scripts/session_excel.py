import os
import sqlite3

import xlsxwriter

BASE_PATH = os.path.join("/home", "jim", "dev", "py4web", "apps", "wmcpa")
OUTPUT_FILE = os.path.join(BASE_PATH, "scripts", "sessions.xlsx")
DATABASE_NAME = os.path.join(BASE_PATH, "databases", "storage.db")


def sessions_to_excel():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    workbook = xlsxwriter.Workbook(OUTPUT_FILE)
    sheet = workbook.add_worksheet()

    sql = """
    SELECT sess.start_time, sess.name, sess.description, spk.first_name, spk.last_name, r.name 
    FROM session sess
    LEFT OUTER JOIN speaker spk ON sess.speaker = spk.id
    LEFT OUTER JOIN room r ON sess.room = r.id
    ORDER BY sess.start_time, r.name
    """
    c.execute(sql)

    i = 1
    sheet.write_row(f"A{i}", ["Start Time", "Name", "Description", "Speaker", "Room"])
    for (
        start_time,
        session_name,
        session_description,
        speaker_first,
        speaker_last,
        room,
    ) in c.fetchall():
        i += 1
        sheet.write_row(
            f"A{i}",
            [
                start_time,
                session_name,
                session_description,
                f"{speaker_first} {speaker_last}",
                room,
            ],
        )

    sheet.set_column("A:A", 20)
    sheet.set_column("B:B", 40)
    sheet.set_column("C:C", 40)
    sheet.set_column("D:D", 25)
    sheet.set_column("E:E", 15)

    workbook.close()

    c.close()
    conn.close()


if __name__ == "__main__":
    sessions_to_excel()
