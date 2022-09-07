from flask import Blueprint, redirect, render_template, request, session, url_for
from .io import write_metadata
from .stages import next_stage_path

# Initialize blueprint.
bp = Blueprint("data_protection", __name__)


@bp.route("/dataprotection")
def dataprotection():
    """Present consent form to participant."""

    # Error-catching: screen for missing session.
    if not "workerId" in session:

        # Redirect participant to error (missing workerId).
        return redirect(url_for("error.error", errornum=1000))

    # Case 1: previously completed experiment.
    elif "complete" in session:

        # Redirect participant to complete page.
        return redirect(url_for("complete.complete"))

    # Case 2: first visit.
    elif not "data-protection" in session:

        # Present consent form.
        return render_template("data_protection.html")

    # Case 3: repeat visit, previous bot-detection.
    elif session["data-protection"] == "BOT":

        # Redirect participant to error (unusual activity).
        return redirect(url_for("error.error", errornum=1005))

    # Case 4: repeat visit, previous non-data-protection.
    elif session["data-protection"] == False:

        # Redirect participant to error (decline data-protection).
        return redirect(url_for("error.error", errornum=1002))

    # Case 5: repeat visit, previous data-protection.
    else:

        path_next = next_stage_path(session, __name__)
        return redirect(url_for(path_next))


@bp.route("/dataprotection", methods=["POST"])
def dataprotection_post():
    """Process participant repsonse to data-protection form."""

    # Retrieve participant response.
    subj_data_protection = int(request.form["subj_data-protection"])
    bot_check = request.form.get("future_contact", False)

    # Check for suspicious responding.
    if bot_check:

        # Update participant metadata.
        session["data-protection"] = "BOT"
        session["complete"] = "error"
        write_metadata(session, ["data-protection", "complete"], "a")

        # Redirect participant to error (unusual activity).
        return redirect(url_for("error.error", errornum=1005))

    # Check participant response.
    elif subj_data_protection:

        # Update participant metadata.
        session["data-protection"] = True
        write_metadata(session, ["data-protection"], "a")

        # Redirect participant to alert page.
        path_next = next_stage_path(session, __name__)
        return redirect(url_for(path_next))

    else:

        # Update participant metadata.
        session["data-protection"] = False
        session["complete"] = "error"
        write_metadata(session, ["data-protection"], "a")

        # Redirect participant to error (decline data-protection).
        return redirect(url_for("error.error", errornum=1002))
