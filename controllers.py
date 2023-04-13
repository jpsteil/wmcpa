import ombott
from apps.wmcpa.lib.grid_helpers import GridSearch, GridSearchQuery, enable_htmx_grid, get_htmx_form_attrs
from py4web import action
from py4web.core import URL, redirect
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Column, Grid, GridClassStyleBulma, get_parent
from yatl.helpers import A, XML, I, TAG
from pydal.validators import IS_NULL_OR, IS_IN_DB
from .common import (
    db,
    session,
    T,
    auth,
)

DETAIL_FIELDS = [
    "first_name",
    "last_name",
    "company",
    "title",
    "bio",
]

BUTTON = TAG.button


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)


@action("speakers", method=["GET", "POST"])
@action("speakers/<path:path>", method=["GET", "POST"])
@action.uses("speakers.html", auth, db, session)
def speakers(path=None):
    columns = [
        Column(
            "name",
            lambda r: XML(
                f'{r.first_name} {r.last_name}<br /><span style="font-size: smaller">{r.company}</span>'
            ),
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
        search_queries=[['Company', lambda value: db.speaker.company.contains(value)],
                        ['Title', lambda value: db.speaker.title.contains(value)]],
        orderby=[db.speaker.last_name, db.speaker.first_name],
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        editable=False,
        rows_per_page=10,
    )

    speaker = None
    parent_id = None
    if grid.action in ["details", "edit"]:
        parent_id = grid.record_id
        speaker = db.speaker(parent_id)

    return dict(heading="Speakers", grid=grid, parent_id=parent_id, speaker=speaker)


@action("speaker/detail/<speaker_id>", method=["GET", "POST"])
@action.uses(
    "form_htmx.html", session, db, auth)
def detail(speaker_id=None):
    speaker = db.speaker(speaker_id)
    if not speaker:
        ombott.abort(
            code=401,
            text="Could not retrieve speaker.  Please contact support.",
        )

    for field in db.speaker.fields:
        if field not in DETAIL_FIELDS:
            db.speaker[field].readable = False

    attrs = {
        "_hx-get": URL("speaker", "detail_edit/%s" % speaker_id),
        "_hx-target": "#detail-target",
    }

    form = Form(
        db.speaker,
        record=speaker,
        readonly=True,
        deletable=False,
        formstyle=FormStyleBulma,
        dbio=False,
        submit_value="Edit",
        **attrs,
    )

    edit_button = BUTTON(
        I(_class="fa fa-edit"), _class="button submit-edit box-shadow-y", **attrs
    )

    return dict(form=form, form_fields=DETAIL_FIELDS, edit_button=edit_button)


@action("speaker/detail_edit/<speaker_id>", method=["GET", "POST"])
@action.uses("form_htmx.html", session, db, auth)
def detail_edit(speaker_id=None):
    speaker = db.speaker(speaker_id)
    if not speaker:
        ombott.abort(
            code=401,
            text="Could not retrieve speaker.  Please contact support.",
        )

    for field in db.speaker.fields:
        if field not in DETAIL_FIELDS:
            db.speaker[field].readable = False
            db.speaker[field].writable = False

    form = Form(
        db.speaker,
        record=speaker,
        formstyle=FormStyleBulma,
        **get_htmx_form_attrs(
            URL("speaker", "detail_edit/%s" % speaker_id), "#detail-target"
        ),
    )

    attrs = {
        "_hx-get": URL("speaker", "detail/%s" % speaker_id),
        "_class": "button is-default",
    }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))

    if form.accepted:
        redirect(URL("speaker/detail/%s" % speaker_id))

    return dict(form=form, form_fields=DETAIL_FIELDS)


@action("speaker/sessions", method=["POST", "GET"])
@action("speaker/sessions/<path:path>", method=["POST", "GET"])
@action.uses(
    "grid_htmx.html",
    session,
    db,
    auth)
def speaker_sessions(path=None):
    #  set the default
    speaker_id = get_parent(
        path,
        parent_field=db.speaker.id,
    )
    db.session.speaker.default = speaker_id

    if path and path.split("/")[0] in ["new", "details", "edit"]:
        db.session.speaker.readable = False
        db.session.speaker.writable = False

    query = db.session.speaker == speaker_id

    grid = Grid(
        path,
        query=query,
        fields=[db.session.start_time, db.session.name],
        field_id=db.session.id,
        orderby=[db.session.start_time],
        auto_process=False,
        details=False,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        rows_per_page=10,
        include_action_button_text=False,
    )

    grid.formatters_by_type["datetime"] = (
        lambda value: value.strftime("%m/%d/%Y %I:%M%p") if value else ""
    )

    enable_htmx_grid(
        grid, "#sessions-target", URL("speaker", "sessions", vars=dict(parent_id=speaker_id))
    )

    return dict(grid=grid)


@action("rooms", method=["GET", "POST"])
@action("rooms/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def rooms(path=None):
    grid = Grid(
        path,
        db.room,
        orderby=[db.room.name],
        search_queries=[['Name', lambda value: db.room.name.contains(value)]],
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        details=False,
        rows_per_page=10,
    )
    return dict(heading="Rooms", grid=grid)


@action("sessions", method=["GET", "POST"])
@action("sessions/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def sessions(path=None):
    search_queries = [
        GridSearchQuery(
            "room",
            lambda value: db.session.room == value,
            requires=IS_NULL_OR(IS_IN_DB(db, "room.id", "%(name)s", zero="..")),
        ),
        GridSearchQuery(
            "speaker",
            lambda value: db.session.speaker == value,
            requires=IS_NULL_OR(
                IS_IN_DB(db, "speaker.id", "%(first_name)s %(last_name)s", zero="..")
            ),
        ),
        GridSearchQuery(
            "filter text",
            lambda value: db.session.name.contains(value)
                          | db.session.description.contains(value),
        ),
    ]

    grid_search = GridSearch(
        search_queries=search_queries,
        queries=[db.session.id > 0],
        formstyle=FormStyleBulma,
    )

    columns = [
        db.session.start_time,
        db.session.name,
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
    left = [
        db.speaker.on(db.session.speaker == db.speaker.id),
        db.room.on(db.session.room == db.room.id),
    ]

    grid = Grid(
        path,
        grid_search.query,
        columns=columns,
        field_id=db.session.id,
        search_form=grid_search.search_form,
        grid_class_style=GridClassStyleBulma,
        orderby=[db.session.start_time, db.room.name],
        formstyle=FormStyleBulma,
        left=left,
        details=False,
        rows_per_page=10,
    )
    return dict(heading="Sessions", grid=grid)
