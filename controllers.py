from apps.wmcpa.lib.grid_helpers import GridSearch, GridSearchQuery
from py4web import action, request, abort, redirect, URL
from py4web.utils.form import FormStyleBulma
from py4web.utils.grid import Column, Grid, GridClassStyleBulma
from yatl.helpers import A, XML
from pydal.validators import IS_NULL_OR, IS_IN_DB
from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    flash,
)


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)


@action("speakers", method=["GET", "POST"])
@action("speakers/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def speakers(path=None):
    columns = [
        Column(
            "name",
            lambda r: XML(f'{r.first_name} {r.last_name}<br /><span style="font-size: smaller">{r.company}</span>'),
            required_fields=[db.speaker.first_name, db.speaker.last_name],
            orderby=db.speaker.last_name,
        ),
        Column(
            "bio", lambda r: f"{r.bio[:75]}..." if r.bio and len(r.bio) > 75 else r.bio
        ),
    ]
    grid = Grid(
        path,
        db.speaker,
        columns=columns,
        orderby=[db.speaker.last_name, db.speaker.first_name],
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        details=False,
        rows_per_page=10
    )
    return dict(heading="Speakers", grid=grid)

@action("rooms", method=["GET", "POST"])
@action("rooms/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def rooms(path=None):
    grid = Grid(
        path,
        db.room,
        columns=[db.room.name],
        orderby=[db.room.name],
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        details=False,
        rows_per_page=10
    )
    return dict(heading="Rooms", grid=grid)


@action("sessions", method=["GET", "POST"])
@action("sessions/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def sessions(path=None):
    search_queries = [GridSearchQuery('room',
                                      lambda value: db.session.room == value,
                                      requires=IS_NULL_OR(IS_IN_DB(db, 'room.id', '%(name)s', zero='..'))),
                      GridSearchQuery('speaker',
                                      lambda value: db.session.speaker == value,
                                      requires=IS_NULL_OR(IS_IN_DB(db, 'speaker.id', '%(first_name)s %(last_name)s', zero='..'))),
                                      GridSearchQuery('filter text',
                                                      lambda value: db.session.name.contains(value) | db.session.description.contains(value))]
    
    grid_search = GridSearch(search_queries=search_queries,
                             queries=[db.session.id > 0], 
                             formstyle=FormStyleBulma)
    
    columns = [db.session.when, db.session.name, 
        Column(
            "speaker",
            lambda r: f"{r.speaker.first_name} {r.speaker.last_name}",
            required_fields=[db.speaker.first_name, db.speaker.last_name],
            orderby=db.speaker.last_name,
        ),
        Column(
            "room",
            lambda r: f"{r.room.name}",
            required_fields=[db.room.name],
            orderby=db.room.name,
        ),
    ]
    left = [db.speaker.on(db.session.speaker==db.speaker.id),
            db.room.on(db.session.room==db.room.id)]


    grid = Grid(
        path,
        grid_search.query,
        columns=columns,
        field_id=db.session.id,
        search_form=grid_search.search_form,
        grid_class_style=GridClassStyleBulma,
        orderby=[db.session.when, db.room.name],
        formstyle=FormStyleBulma,
        left=left,
        details=False,
        rows_per_page=10
    )
    return dict(heading="Sessions", grid=grid)
