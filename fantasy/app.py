from flask import Flask, render_template, request, redirect, url_for, flash

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user_model import User

import db_dao
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "Key for the Grand Line Adventurers Guild"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# constants

# Simulated current day and time inside the fictional week , 1 = Monday ... 7 = Sunday
SIM_DAY = 3
SIM_TIME = "17:30"

DAY_NAMES = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
             5: "Friday", 6: "Saturday", 7: "Sunday"}

ROLE_CAPACITY = {"Warrior": 4, "Mage": 3, "Healer": 2}

LOCATIONS = ["Elbaf", "Wano Country", "Egghead Island"]

QUEST_TYPES = ["combat", "exploration", "puzzle", "stealth", "magic", "survival"]

DIFFICULTIES = ["easy", "medium", "hard", "legendary"]

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "avif"]

MODIFY_DEADLINE_MINUTES = 8 * 60

MAX_SESSIONS_PER_ADVENTURER = 3

MAX_DESCRIPTION_CHARS = 300

MAX_NAME_CHARS = 25


# time helpers

def time_to_minutes(p_time):
    parts = p_time.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def week_minutes(p_day, p_time):
    # absolute minute start (Monday 00:00 = 0)
    return (p_day - 1) * 24 * 60 + time_to_minutes(p_time)


def sim_now_minutes():
    return week_minutes(SIM_DAY, SIM_TIME)


def is_valid_time(p_time):
    parts = p_time.split(":")
    if len(parts) != 2:
        return False
    if not parts[0].isdigit() or not parts[1].isdigit():
        return False
    hours = int(parts[0])
    minutes = int(parts[1])
    return 0 <= hours <= 23 and 0 <= minutes <= 59


def intervals_overlap(p_start_a, p_end_a, p_start_b, p_end_b):
    return p_start_a < p_end_b and p_start_b < p_end_a


def session_is_modifiable(p_session):
    start = week_minutes(p_session["day"], p_session["start_time"])
    return start - sim_now_minutes() > MODIFY_DEADLINE_MINUTES


# view helpers

def build_session_view(p_session):

    view = dict(p_session)

    taken = {"Warrior": 0, "Mage": 0, "Healer": 0}
    for row in db_dao.get_places_taken_by_session(p_session["id"]):
        taken[row["role_category"]] = row["taken"]

    view["taken"] = taken
    view["remaining"] = {}
    for role in ROLE_CAPACITY:
        view["remaining"][role] = ROLE_CAPACITY[role] - taken[role]

    view["reserved_total"] = taken["Warrior"] + taken["Mage"] + taken["Healer"]

    return view


@app.context_processor
def inject_globals():
    return {
        "DAY_NAMES": DAY_NAMES,
        "ROLE_CAPACITY": ROLE_CAPACITY,
        "LOCATIONS": LOCATIONS,
        "QUEST_TYPES": QUEST_TYPES,
        "DIFFICULTIES": DIFFICULTIES,
        "MAX_DESCRIPTION_CHARS": MAX_DESCRIPTION_CHARS,
    }


@app.route("/")
def home():
    
    f_days = request.args.getlist("f_day")
    f_types = request.args.getlist("f_type")
    f_difficulties = request.args.getlist("f_difficulty")
    f_roles = request.args.getlist("f_role")

    sessions = [build_session_view(s) for s in db_dao.get_sessions()]

    filtered = []
    for session in sessions:
        if f_days and str(session["day"]) not in f_days:
            continue
        if f_types and session["type"] not in f_types:
            continue
        if f_difficulties and session["difficulty"] not in f_difficulties:
            continue
        if f_roles and not any(session["remaining"][role] > 0 for role in f_roles):
            continue
        filtered.append(session)

    days = []
    for day_number in range(1, 8):
        day_sessions = [s for s in filtered if s["day"] == day_number]
        if day_sessions:
            days.append({"number": day_number, "name": DAY_NAMES[day_number], "sessions": day_sessions})

    return render_template("index.html", pdays=days,
                           f_days=f_days, f_types=f_types,
                           f_difficulties=f_difficulties, f_roles=f_roles)


@app.route("/session/<int:id_session>")
def session_detail(id_session):
    db_session = db_dao.get_session_by_id(id_session)

    if not db_session:
        flash("This quest session does not exist", "danger")
        return redirect(url_for("home"))

    session = build_session_view(db_session)
    participants = db_dao.get_active_participations_by_session(id_session)

    my_participation = None
    if current_user.is_authenticated and current_user.is_adventurer():
        my_participation = db_dao.get_participation_by_session_and_user(id_session, current_user.id)

    return render_template("session_detail.html", psession=session,
                           pparticipation=my_participation, pparticipants=participants)


# authentication

@app.route("/signup")
def signup():
    return render_template("registration.html")


@app.route("/register", methods=["POST"])
def register():
    display_name = request.form.get("txt_display_name", "").strip()
    email = request.form.get("txt_email", "").strip().lower()
    password = request.form.get("txt_password", "")
    confirm_password = request.form.get("txt_confirm_password", "")

    if display_name == "":
        flash("The adventurer name cannot be empty", "danger")
        return redirect(url_for("signup"))
    elif len(display_name) > MAX_NAME_CHARS:
        flash("The adventurer name must be at most " + str(MAX_NAME_CHARS) + " characters", "danger")
        return redirect(url_for("signup"))
    elif email == "" or "@" not in email or "." not in email:
        flash("Please insert a valid email address", "danger")
        return redirect(url_for("signup"))
    elif len(password) < 8:
        flash("The password must be at least 8 characters long", "danger")
        return redirect(url_for("signup"))
    elif password != confirm_password:
        flash("The two passwords do not match", "danger")
        return redirect(url_for("signup"))

    if db_dao.get_adventurer_by_display_name(display_name):
        flash("The adventurer name \"" + display_name + "\" is already taken, please choose another one", "danger")
        return redirect(url_for("signup"))

    existing = db_dao.get_user_by_email_and_role(email, "adventurer")
    if existing:
        flash("An adventurer with this email is already registered", "danger")
        return redirect(url_for("signup"))

    password_hash = generate_password_hash(password, method="scrypt")
    db_dao.new_user(email, display_name, password_hash, "adventurer")

    flash("Welcome aboard, " + display_name + "! You can now log in", "success")
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    email = request.form.get("txt_email", "").strip().lower()
    password = request.form.get("txt_password", "")
    role = request.form.get("role", "")

    if role not in ["adventurer", "guild_master", "council"]:
        flash("Please select a valid profile", "danger")
        return redirect(url_for("login"))

    db_user = db_dao.get_user_by_email_and_role(email, role)

    if not db_user:
        flash("No " + role.replace("_", " ") + " account exists with this email", "danger")
        return redirect(url_for("login"))
    elif not check_password_hash(db_user["password"], password):
        flash("The password is wrong", "danger")
        return redirect(url_for("login"))
    else:
        new = User(
            id=db_user["id"],
            email=db_user["email"],
            display_name=db_user["display_name"],
            password=db_user["password"],
            role=db_user["role"],
        )

        login_user(new)
        flash("Welcome back, " + db_user["display_name"] + "!", "success")

    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    db_user = db_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(
            id=db_user["id"],
            email=db_user["email"],
            display_name=db_user["display_name"],
            password=db_user["password"],
            role=db_user["role"],
        )
    else:
        user = None

    return user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out. Fair winds!", "success")
    return redirect(url_for("home"))


# adventurer area

@app.route("/profile")
@login_required
def profile():
    if current_user.is_guild_master():
        return redirect(url_for("master"))
    elif current_user.is_council():
        return redirect(url_for("council"))

    participations = db_dao.get_participations_by_user(current_user.id)

    participated = []
    cancelled = []

    for row in participations:
        item = dict(row)
        item["modifiable"] = session_is_modifiable(row)
        if row["status"] == "cancelled":
            cancelled.append(item)
        else:
            participated.append(item)

    return render_template("profile.html", pparticipated=participated,
                           pcancelled=cancelled)


@app.route("/join/<int:id_session>", methods=["POST"])
@login_required
def join_session(id_session):
    if not current_user.is_adventurer():
        flash("Only adventurers can join quest sessions", "danger")
        return redirect(url_for("session_detail", id_session=id_session))

    db_session = db_dao.get_session_by_id(id_session)
    if not db_session:
        flash("This quest session does not exist", "danger")
        return redirect(url_for("home"))

    role = request.form.get("role_category", "")
    places_raw = request.form.get("places", "")

    if role not in ROLE_CAPACITY:
        flash("Please select a valid party role", "danger")
        return redirect(url_for("session_detail", id_session=id_session))
    elif places_raw not in ["1", "2"]:
        flash("You can reserve 1 or 2 places", "danger")
        return redirect(url_for("session_detail", id_session=id_session))

    places = int(places_raw)

    existing = db_dao.get_participation_by_session_and_user(id_session, current_user.id)
    if existing and existing["status"] == "active":
        flash("You already joined this session. Manage it from your profile", "warning")
        return redirect(url_for("profile"))

    # capacity of the chosen role (companion rule ,  2 places are refused when only 1 place is left)
    taken = 0
    for row in db_dao.get_places_taken_by_session(id_session):
        if row["role_category"] == role:
            taken = row["taken"]
    remaining = ROLE_CAPACITY[role] - taken

    if remaining <= 0:
        flash("All " + role + " places are already taken for this session", "danger")
        return redirect(url_for("session_detail", id_session=id_session))
    elif places > remaining:
        flash("Only " + str(remaining) + " " + role + " place is left, you cannot bring a companion", "danger")
        return redirect(url_for("session_detail", id_session=id_session))

    # at most 3 quest sessions per week
    if db_dao.count_active_participations_by_user(current_user.id) >= MAX_SESSIONS_PER_ADVENTURER:
        flash("You already joined " + str(MAX_SESSIONS_PER_ADVENTURER) + " quest sessions this week", "danger")
        return redirect(url_for("session_detail", id_session=id_session))

    # no overlapping sessions for the same adventurer
    new_start = week_minutes(db_session["day"], db_session["start_time"])
    new_end = new_start + db_session["duration_minutes"]

    for row in db_dao.get_participations_by_user(current_user.id):
        if row["status"] != "active":
            continue
        other_start = week_minutes(row["day"], row["start_time"])
        other_end = other_start + row["duration_minutes"]
        if intervals_overlap(new_start, new_end, other_start, other_end):
            flash("This session overlaps with \"" + row["title"] + "\" that you already joined", "danger")
            return redirect(url_for("session_detail", id_session=id_session))

    if existing:
        # the adventurer cancelled this session before: reactivate the row
        db_dao.update_participation(existing["id"], role, places, "active")
    else:
        db_dao.new_participation(id_session, current_user.id, role, places)

    flash("You joined \"" + db_session["title"] + "\" as " + role + " with " + str(places) + " place(s)!", "success")
    return redirect(url_for("profile"))


@app.route("/edit_participation/<int:id_participation>", methods=["POST"])
@login_required
def edit_participation(id_participation):
    participation = db_dao.get_participation_by_id(id_participation)

    if not participation or participation["id_user"] != current_user.id:
        flash("This participation does not exist", "danger")
        return redirect(url_for("profile"))
    elif participation["status"] != "active":
        flash("This participation is cancelled", "danger")
        return redirect(url_for("profile"))

    db_session = db_dao.get_session_by_id(participation["id_session"])

    if not session_is_modifiable(db_session):
        flash("The session starts in less than 8 hours: the participation is locked", "danger")
        return redirect(url_for("profile"))

    role = request.form.get("role_category", "")
    places_raw = request.form.get("places", "")

    if role not in ROLE_CAPACITY:
        flash("Please select a valid party role", "danger")
        return redirect(url_for("profile"))
    elif places_raw not in ["1", "2"]:
        flash("You can reserve 1 or 2 places", "danger")
        return redirect(url_for("profile"))

    places = int(places_raw)

    # capacity check for the requested role, ignoring the places already held by this same participation
    taken = 0
    for row in db_dao.get_places_taken_by_session(participation["id_session"]):
        if row["role_category"] == role:
            taken = row["taken"]
    if role == participation["role_category"]:
        taken = taken - participation["places"]

    if places > ROLE_CAPACITY[role] - taken:
        flash("Not enough free " + role + " places for this change", "danger")
        return redirect(url_for("profile"))

    db_dao.update_participation(id_participation, role, places, "active")
    flash("Participation updated: " + role + " with " + str(places) + " place(s)", "success")
    return redirect(url_for("profile"))


@app.route("/cancel_participation/<int:id_participation>", methods=["POST"])
@login_required
def cancel_participation(id_participation):
    participation = db_dao.get_participation_by_id(id_participation)

    if not participation or participation["id_user"] != current_user.id:
        flash("This participation does not exist", "danger")
        return redirect(url_for("profile"))
    elif participation["status"] != "active":
        flash("This participation is already cancelled", "danger")
        return redirect(url_for("profile"))

    db_session = db_dao.get_session_by_id(participation["id_session"])

    if not session_is_modifiable(db_session):
        flash("The session starts in less than 8 hours: the participation is locked", "danger")
        return redirect(url_for("profile"))

    db_dao.update_participation(id_participation,
                                participation["role_category"],
                                participation["places"], "cancelled")
    flash("Participation cancelled", "success")
    return redirect(url_for("profile"))


# guild master area

@app.route("/master")
@login_required
def master():
    if not current_user.is_guild_master():
        flash("Only the Guild Master can access this page", "danger")
        return redirect(url_for("home"))

    quests = db_dao.get_quests()
    sessions = [build_session_view(s) for s in db_dao.get_sessions()]

    quest_views = []
    for quest in quests:
        quest_view = dict(quest)
        quest_view["sessions"] = []
        for session in sessions:
            if session["id_quest"] == quest["id"]:
                # most requested role(s) of the session
                best = 0
                for role in session["taken"]:
                    if session["taken"][role] > best:
                        best = session["taken"][role]
                most_requested = []
                if best > 0:
                    for role in session["taken"]:
                        if session["taken"][role] == best:
                            most_requested.append(role)
                session["most_requested"] = most_requested
                session["has_participants"] = session["reserved_total"] > 0
                quest_view["sessions"].append(session)
        quest_views.append(quest_view)

    return render_template("master.html", pquests=quest_views)


@app.route("/new_quest")
@login_required
def new_quest():
    if not current_user.is_guild_master():
        flash("Only the Guild Master can create quests", "danger")
        return redirect(url_for("home"))

    return render_template("new_quest.html")


@app.route("/create_quest", methods=["POST"])
@login_required
def create_quest():
    if not current_user.is_guild_master():
        flash("Only the Guild Master can create quests", "danger")
        return redirect(url_for("home"))

    title = request.form.get("txt_title", "").strip()
    duration_raw = request.form.get("txt_duration", "")
    quest_type = request.form.get("type", "")
    difficulty = request.form.get("difficulty", "")
    description = request.form.get("txt_description", "").strip()

    if title == "":
        flash("The quest title cannot be empty", "danger")
        return redirect(url_for("new_quest"))
    elif not duration_raw.isdigit() or int(duration_raw) <= 0:
        flash("The duration must be a positive number of minutes", "danger")
        return redirect(url_for("new_quest"))
    elif quest_type not in QUEST_TYPES:
        flash("Please select a valid quest type", "danger")
        return redirect(url_for("new_quest"))
    elif difficulty not in DIFFICULTIES:
        flash("Please select a valid difficulty level", "danger")
        return redirect(url_for("new_quest"))
    elif description == "":
        flash("The quest description cannot be empty", "danger")
        return redirect(url_for("new_quest"))
    elif len(description) > MAX_DESCRIPTION_CHARS:
        flash("The description must be at most " + str(MAX_DESCRIPTION_CHARS) + " characters", "danger")
        return redirect(url_for("new_quest"))

    quest_img = request.files.get("quest_img")
    if not quest_img or quest_img.filename == "":
        flash("A promotional image is mandatory for the quest", "danger")
        return redirect(url_for("new_quest"))

    extension = quest_img.filename.split(".")[-1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        flash("The image must be a jpg, png, webp or avif file", "danger")
        return redirect(url_for("new_quest"))

    secs = int(datetime.now().timestamp())
    img_name = str(secs) + "_" + secure_filename(quest_img.filename)
    quest_img.save("static/images/quests/" + img_name)

    db_dao.new_quest(title, int(duration_raw), quest_type, difficulty, description, img_name)

    flash("Quest \"" + title + "\" created! Now schedule its sessions", "success")
    return redirect(url_for("master"))


def validate_session_form(p_id_quest_raw, p_day_raw, p_start_time, p_location):
    # shared server-side validation for create/update session, returns an error message or None
    if not p_id_quest_raw.isdigit() or not db_dao.get_quest_by_id(int(p_id_quest_raw)):
        return "Please select a valid quest"
    elif p_day_raw not in ["1", "2", "3", "4", "5", "6", "7"]:
        return "Please select a valid day of the week"
    elif not is_valid_time(p_start_time):
        return "The starting time must be in HH:MM format"
    elif p_location not in LOCATIONS:
        return "Please select a valid location"

    return None


def find_location_conflict(p_id_quest, p_day, p_start_time, p_location, p_id_session_excluded):
    # each location hosts only one quest session at a time , check [start, end) against the other sessions of that day+location
    quest = db_dao.get_quest_by_id(p_id_quest)
    new_start = week_minutes(p_day, p_start_time)
    new_end = new_start + quest["duration_minutes"]

    for row in db_dao.get_sessions_by_day_and_location(p_day, p_location):
        if row["id"] == p_id_session_excluded:
            continue
        other_start = week_minutes(row["day"], row["start_time"])
        other_end = other_start + row["duration_minutes"]
        if intervals_overlap(new_start, new_end, other_start, other_end):
            return row

    return None


@app.route("/new_session")
@login_required
def new_session():
    if not current_user.is_guild_master():
        flash("Only the Guild Master can schedule sessions", "danger")
        return redirect(url_for("home"))

    quests = db_dao.get_quests()
    if not quests:
        flash("Create a quest first, then schedule its sessions", "warning")
        return redirect(url_for("new_quest"))

    return render_template("new_session.html", pquests=quests)


@app.route("/create_session", methods=["POST"])
@login_required
def create_session():
    if not current_user.is_guild_master():
        flash("Only the Guild Master can schedule sessions", "danger")
        return redirect(url_for("home"))

    id_quest_raw = request.form.get("id_quest", "")
    day_raw = request.form.get("day", "")
    start_time = request.form.get("txt_start_time", "").strip()
    location = request.form.get("location", "")

    error = validate_session_form(id_quest_raw, day_raw, start_time, location)
    if error:
        flash(error, "danger")
        return redirect(url_for("new_session"))

    conflict = find_location_conflict(int(id_quest_raw), int(day_raw), start_time, location, -1)
    if conflict:
        flash(location + " is already hosting \"" + conflict["title"] + "\" at that time on "
              + DAY_NAMES[int(day_raw)], "danger")
        return redirect(url_for("new_session"))

    db_dao.new_session(int(id_quest_raw), int(day_raw), start_time, location)

    flash("Quest session scheduled on " + DAY_NAMES[int(day_raw)] + " at " + start_time
          + " in " + location, "success")
    return redirect(url_for("master"))


@app.route("/edit_session/<int:id_session>")
@login_required
def edit_session(id_session):
    if not current_user.is_guild_master():
        flash("Only the Guild Master can modify sessions", "danger")
        return redirect(url_for("home"))

    db_session = db_dao.get_session_by_id(id_session)
    if not db_session:
        flash("This quest session does not exist", "danger")
        return redirect(url_for("master"))

    if db_dao.count_active_participations_by_session(id_session) > 0:
        flash("Adventurers already joined this session: it cannot be modified", "danger")
        return redirect(url_for("master"))

    return render_template("edit_session.html", psession=db_session)


@app.route("/update_session/<int:id_session>", methods=["POST"])
@login_required
def update_session(id_session):
    if not current_user.is_guild_master():
        flash("Only the Guild Master can modify sessions", "danger")
        return redirect(url_for("home"))

    db_session = db_dao.get_session_by_id(id_session)
    if not db_session:
        flash("This quest session does not exist", "danger")
        return redirect(url_for("master"))

    if db_dao.count_active_participations_by_session(id_session) > 0:
        flash("Adventurers already joined this session: it cannot be modified", "danger")
        return redirect(url_for("master"))

    day_raw = request.form.get("day", "")
    start_time = request.form.get("txt_start_time", "").strip()
    location = request.form.get("location", "")

    error = validate_session_form(str(db_session["id_quest"]), day_raw, start_time, location)
    if error:
        flash(error, "danger")
        return redirect(url_for("edit_session", id_session=id_session))

    conflict = find_location_conflict(db_session["id_quest"], int(day_raw), start_time,location, id_session)
    if conflict:
        flash(location + " is already hosting \"" + conflict["title"] + "\" at that time on "
              + DAY_NAMES[int(day_raw)], "danger")
        return redirect(url_for("edit_session", id_session=id_session))

    db_dao.update_session(id_session, int(day_raw), start_time, location)

    flash("Quest session updated", "success")
    return redirect(url_for("master"))


@app.route("/delete_session/<int:id_session>", methods=["POST"])
@login_required
def delete_session(id_session):
    if not current_user.is_guild_master():
        flash("Only the Guild Master can cancel sessions", "danger")
        return redirect(url_for("home"))

    db_session = db_dao.get_session_by_id(id_session)
    if not db_session:
        flash("This quest session does not exist", "danger")
        return redirect(url_for("master"))

    if db_dao.count_active_participations_by_session(id_session) > 0:
        flash("Adventurers already joined this session: it cannot be cancelled", "danger")
        return redirect(url_for("master"))

    db_dao.delete_participations_by_session(id_session) #children deletion first , there can be cancelled ones 
    db_dao.delete_session(id_session) #then the parent 

    flash("Quest session cancelled", "success")
    return redirect(url_for("master"))


# guild council area

@app.route("/council")
@login_required
def council():
    if not current_user.is_council():
        flash("Only the Guild Council can access this page", "danger")
        return redirect(url_for("home"))

    adventurers = db_dao.get_adventurers()
    quests = db_dao.get_quests()
    sessions = [build_session_view(s) for s in db_dao.get_sessions()]
    active = db_dao.get_active_participations()

    # participations per adventurer
    counts = {}
    for row in active:
        counts[row["id_user"]] = counts.get(row["id_user"], 0) + 1

    adventurer_views = []
    for adventurer in adventurers:
        adventurer_views.append({
            "display_name": adventurer["display_name"],
            "email": adventurer["email"],
            "participations": counts.get(adventurer["id"], 0),
        })

    # global statistics
    places_per_role = {"Warrior": 0, "Mage": 0, "Healer": 0}
    places_per_type = {}
    for row in active:
        places_per_role[row["role_category"]] += row["places"]
        places_per_type[row["type"]] = places_per_type.get(row["type"], 0) + row["places"]

    popular_type = ""
    best = 0
    for quest_type in places_per_type:
        if places_per_type[quest_type] > best:
            best = places_per_type[quest_type]
            popular_type = quest_type

    busiest_session = None
    best = 0
    for session in sessions:
        if session["reserved_total"] > best:
            best = session["reserved_total"]
            busiest_session = session

    # participants of every session, for the detail tables
    participants = {}
    for session in sessions:
        participants[session["id"]] = db_dao.get_active_participations_by_session(session["id"])

    stats = {
        "total_adventurers": len(adventurers),
        "total_quests": len(quests),
        "total_sessions": len(sessions),
        "total_participations": len(active),
        "places_per_role": places_per_role,
        "popular_type": popular_type,
        "busiest_session": busiest_session,
    }

    quest_views = []
    for quest in quests:
        quest_view = dict(quest)
        quest_view["sessions"] = [s for s in sessions if s["id_quest"] == quest["id"]]
        quest_views.append(quest_view)

    return render_template("council.html", pstats=stats,
                           padventurers=adventurer_views,
                           pquests=quest_views, pparticipants=participants)
