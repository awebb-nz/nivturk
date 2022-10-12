import os
import re
import warnings
from flask import Flask, redirect, request, session, url_for
from app import consent, data_protection, alert, experiment, complete, error
from .io import write_metadata
from .utils import gen_code

import state
from state import State


__version__ = "1.2"

# Define root directory.
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

State.ensure_directories(ROOT_DIR)

# Check Flask mode; if debug mode, clear session variable.
if State.flask_settings["DEBUG"]:
    warnings.warn(
        "WARNING: Flask currently in debug mode. " +
        "This should be changed prior to production."
    )

# Check Flask password.
if State.flask_settings["SECRET_KEY"] == "PLEASE_CHANGE_THIS":
    warnings.warn(
        "WARNING: Flask password is currently default. " +
        "This should be changed prior to production."
    )

# Check restart mode; if true, participants can restart experiment.
allow_restart = State.flask_settings["ALLOW_RESTART"]

# Initialize Flask application.
app = Flask(__name__)
app.secret_key = State.flask_settings["SECRET_KEY"]

# Apply blueprints to the application.
app.register_blueprint(consent.bp)
app.register_blueprint(data_protection.bp)
app.register_blueprint(alert.bp)
app.register_blueprint(experiment.bp)
app.register_blueprint(complete.bp)
app.register_blueprint(error.bp)


# Define root node.
@app.route("/")
def index():
    # Debug mode: clear session.
    if State.flask_settings["DEBUG"]:
        session.clear()

    # Record incoming metadata.
    info = dict(
        workerId=request.args.get("PROLIFIC_PID"),  # Prolific metadata
        assignmentId=request.args.get("SESSION_ID"),  # Prolific metadata
        hitId=request.args.get("STUDY_ID"),  # Prolific metadata
        subId=gen_code(24),  # NivTurk metadata
        address=request.remote_addr,  # NivTurk metadata
        browser=request.user_agent.browser,  # User metadata
        platform=request.user_agent.platform,  # User metadata
        version=request.user_agent.version,  # User metadata
        #code_success=cfg["prolific"].get("CODE_SUCCESS", gen_code(8).upper()),
        #code_reject=cfg["prolific"].get("CODE_REJECT", gen_code(8).upper()),
    )

    # Case 1: workerId absent form URL.
    if info["workerId"] is None:

        # Redirect participant to error (missing workerId).
        return redirect(url_for("error.error", errornum=1000))

    # Case 2: mobile / tablet user.
    elif info["platform"] in ["android", "iphone", "ipad", "wii"]:

        # Redirect participant to error (platform error).
        return redirect(url_for("error.error", errornum=1001))

    # Case 3: previous complete.
    elif "complete" in session:

        # Redirect participant to complete page.
        return redirect(url_for("complete.complete"))

    # Case 4: repeat visit, manually changed workerId.
    elif "workerId" in session and session["workerId"] != info["workerId"]:

        # Update metadata.
        session["ERROR"] = "1005: workerId tampering detected."
        session["complete"] = "error"
        write_metadata(session, ["ERROR", "complete"], "a")

        # Redirect participant to error (unusual activity).
        return redirect(url_for("error.error", errornum=1005))

    # Case 5: repeat visit, preexisting activity.
    elif "workerId" in session:

        path_next = next_stage_path(session)
        return redirect(url_for(path_next))

    # Case 6: repeat visit, preexisting log but no session data.
    elif "workerId" not in session and \
            info["workerId"] in os.listdir(State.directory_settings["METADATA"]):

        # Parse log file.
        with open(os.path.join(session["metadata"], info["workerId"]), "r") as f:
            logs = f.read()


        # Extract subject ID.
        info["subId"] = re.search("subId\t(.*)\n", logs).group(1)

        # Check for previous consent.
        consent = re.search("consent\t(.*)\n", logs)
        if consent and consent.group(1) == "True":
            info["consent"] = True  # consent = true
        elif consent and consent.group(1) == "False":
            info["consent"] = False  # consent = false
        elif consent:
            info["consent"] = consent.group(1)  # consent = bot

        # Check for previous experiment.
        experiment = re.search("experiment\t(.*)\n", logs)
        if experiment:
            info["experiment"] = experiment.group(1)

        # Check for previous complete.
        complete = re.search("complete\t(.*)\n", logs)
        if complete:
            info["complete"] = complete.group(1)

        # Update metadata.
        for k, v in info.items():
            session[k] = v

        # Redirect participant as appropriate.
        if "complete" in session:
            return redirect(url_for("complete.complete"))
        elif "experiment" in session:
            return redirect(url_for("experiment.experiment"))
        else:
            return redirect(url_for("consent.consent"))

    # Case 7: first visit, workerId present.
    else:

        # Update metadata.
        for k, v in info.items():
            session[k] = v
        write_metadata(
            session,
            [
                "workerId",
                "hitId",
                "assignmentId",
                "subId",
                "address",
                "browser",
                "platform",
                "version",
            ],
            "w",
        )

        # Redirect participant to consent form.
        return redirect(url_for("consent.consent"))
