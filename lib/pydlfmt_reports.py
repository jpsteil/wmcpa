from dataclasses import dataclass
from pydlfmt import DataFormatter, Column
import datetime
from ..common import db
import os


class SessionList(DataFormatter):
    def __init__(self):
        super().__init__(self)

        self.data = []
        self.get_data()

        self.columns = [
            Column("start_time", datatype="datetime"),
            Column("name"),
            Column("speaker"),
            Column("room"),
        ]

        self.title = "WMCPA Session Grid"
        self.to_excel(
            filename=os.path.join("/home", "jim", "sessions.xlsx"), format_table=True
        )

        self.to_pdf(
            orientation="landscape",
            filename=os.path.join("/home", "jim", "sessions.pdf"),
        )

    def get_data(self):
        left = [
            db.speaker.on(db.session.speaker == db.speaker.id),
            db.room.on(db.session.room == db.room.id),
        ]
        for row in db(db.session.id > 0).select(
            db.session.ALL,
            db.speaker.ALL,
            db.room.ALL,
            orderby=[db.session.start_time, db.room.name],
            left=left,
        ):
            self.data.append(
                ReportRow(
                    row.session.start_time,
                    row.session.name,
                    f"{row.speaker.first_name} {row.speaker.last_name}",
                    row.room.name,
                )
            )


@dataclass
class ReportRow:
    start_time: datetime.datetime
    name: str
    speaker: str
    room: str


def run():
    SessionList()
