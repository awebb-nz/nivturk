from flask import Blueprint, redirect, render_template, request, session, url_for
from .io import write_metadata
from .stages import next_stage_path, check_general_conditions
from .stages import Redirect, check_repeat_visit

## Initialize blueprint.
bp = Blueprint("alert", __name__)


@bp.route("/alert")
def alert():
    """Present alert to participant."""

    redir = check_general_conditions(session)
    if redir is not None:
        redir_type = redir["type"]
        if redir_type is Redirect.Error:
            return redirect(url_for("error.error", errornum=redir["errno"]))
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))

    previous = check_repeat_visit(session, __name__)
    if previous is not None:
        if not previous:
            return redirect(url_for("error.error", errornum=1002))
        redir = next_stage_path(session, __name__)
        redir_type = redir["type"]
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))
        return redirect(url_for(redir["url"]))

    return render_template("alert.html")


@bp.route("/alert", methods=["POST"])
def alert_post():
    """Process participant repsonse to alert page."""
    session["alert"] = True
    write_metadata(session, ["alert"], "a")

    redir = next_stage_path(session, __name__)
    redir_type = redir["type"]
    if redir_type is Redirect.Complete:
        return redirect(url_for("complete.complete"))
    return redirect(url_for(redir["url"]))
