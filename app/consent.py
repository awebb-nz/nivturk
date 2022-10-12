from flask import Blueprint, redirect, render_template, request, session, url_for
from .io import write_metadata
from .stages import Redirect, check_repeat_visit, check_general_conditions
from .state import State

# Initialize blueprint.
bp = Blueprint("consent", __name__)


@bp.route("/consent")
def consent():
    current_stage = State.get_stage(__name__)
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
        redir = State.get_next_stage(current_stage)
        redir_type = redir["type"]
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))
        return redirect(url_for(redir["url"]))

    return render_template("consent.html")


@bp.route("/consent", methods=["POST"])
def consent_post():
    """Process participant repsonse to consent form."""

    # Retrieve participant response.
    subj_consent = int(request.form["subj_consent"])
    bot_check = request.form.get("future_contact", False)

    # Check for suspicious responding.
    if bot_check:

        # Update participant metadata.
        session["consent"] = False
        session["is_bot"] = True
        session["complete"] = "error"
        write_metadata(session, ["consent", "complete"], "a")

        # Redirect participant to error (unusual activity).
        return redirect(url_for("error.error", errornum=1005))

    # Check participant response.
    elif subj_consent:

        # Update participant metadata.
        session["consent"] = True
        write_metadata(session, ["consent"], "a")

        redir = next_stage_path(session, __name__)
        redir_type = redir["type"]
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))
        return redirect(url_for(redir["url"]))

    else:

        # Update participant metadata.
        session["consent"] = False
        session["complete"] = "error"
        write_metadata(session, ["consent"], "a")

        # Redirect participant to error (decline consent).
        return redirect(url_for("error.error", errornum=1002))
