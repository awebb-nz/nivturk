from flask import Blueprint, redirect, render_template, request, session, url_for
from .io import write_metadata
from .stages import next_stage_path, check_general_conditions, Redirect

# Initialize blueprint.
bp = Blueprint("data_protection", __name__)


@bp.route("/dataprotection")
def dataprotection():
    redir = check_general_conditions(session)
    if redir is not None:
        redir_type = redir["type"]
        if redir_type is Redirect.Error:
            return redirect(url_for("error.error", errornum=redir["errno"]))
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))

    # Case 2: first visit.
    elif not "data-protection" in session:

        # Present consent form.
        return render_template("data_protection.html")

    # Case 4: repeat visit, previous non-data-protection.
    elif session["data-protection"] == False:

        # Redirect participant to error (decline data-protection).
        return redirect(url_for("error.error", errornum=1002))

    # Case 5: repeat visit, previous data-protection.
    else:
        redir =  next_stage_path(session, __name__)
        redir_type = redir["type"]
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))
        return redirect(url_for(redir["url"]))


@bp.route("/dataprotection", methods=["POST"])
def dataprotection_post():
    """Process participant repsonse to data-protection form."""

    # Retrieve participant response.
    subj_data_protection = int(request.form["subj_data-protection"])
    bot_check = request.form.get("future_contact", False)

    # Check for suspicious responding.
    if bot_check:

        # Update participant metadata.
        session["data-protection"] = False
        session["is_bot"] = True
        session["complete"] = "error"
        write_metadata(session, ["data-protection", "complete"], "a")

        # Redirect participant to error (unusual activity).
        return redirect(url_for("error.error", errornum=1005))

    # Check participant response.
    elif subj_data_protection:

        # Update participant metadata.
        session["data-protection"] = True
        write_metadata(session, ["data-protection"], "a")

        redir =  next_stage_path(session, __name__)
        redir_type = redir["type"]
        if redir_type is Redirect.Complete:
            return redirect(url_for("complete.complete"))
        return redirect(url_for(redir["url"]))

    else:

        # Update participant metadata.
        session["data-protection"] = False
        session["complete"] = "error"
        write_metadata(session, ["data-protection"], "a")

        # Redirect participant to error (decline data-protection).
        return redirect(url_for("error.error", errornum=1002))
