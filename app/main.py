import os
import datetime
import secrets
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_session import Session
from flask_pywebpush import WebPush, WebPushException
import redis
import bcrypt

# Beginning Of Helper Functions


def hash_password(password):
    salt = bcrypt.gensalt().decode('utf-8')
    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'), salt.encode('utf-8'))

    return hashed_password.decode('utf-8')


def verify_hashed_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_current_timestamp():
    # Returning a UTC timestamp
    return datetime.datetime.utcnow().timestamp()


def send_email(email, email_type):
    return True


def verify_recaptcha(recaptcha_token):
    return True

# End Of Helper Functions


load_dotenv()

app = Flask(__name__)

push = WebPush(private_key=os.environ.get("VAPID_PRIVATE_KEY"),
               sender_info='mailto:contact@projectrexa.dedyn.io')

app.config["WEBPUSH_VAPID_PRIVATE_KEY"] = os.environ.get("VAPID_PRIVATE_KEY")
app.config["WEBPUSH_VAPID_CLAIMS"] = {
    "sub": "mailto:contact@projectrexa.dedyn.io"}


# Setting up secret key
app.secret_key = os.environ.get("SECRET_KEY")

# Connecting to MongoDB
MONGODB_URI = MongoClient(os.environ.get("MONGODB_URI"))
MONGODB_DB = MONGODB_URI["KRMU"]

# Setting up session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(
    f"redis://default:{os.getenv('REDIS_PASSWORD')}@redis-15560.c264.ap-south-1-1.ec2.cloud.redislabs.com:15560"
)
Session(app)

# Setting up rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "2000 per hour"],
    storage_uri="memory://"
)


@app.route("/")
@limiter.limit("10 per minute")
def index():
    """ This function handles the logic for the index page

    Returns:
        _type_: flask.redirect
    """
    if not session.get("logged_in"):
        return redirect(url_for("signin"))
    return redirect(url_for("dashboard"))


@app.route("/sign-up", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def signup():
    """ This function handles the logic for signing up a new user

    Returns:
        _type_: flask.render_template or flask.redirect or flask.jsonify
    """
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("index"))
        return render_template("signup.html")
    else:
        if session.get("logged_in"):
            return redirect(url_for("index"))
        data = request.get_json()

        user_email = data["email"].lower()
        user_password = data["password"]
        recaptcha_token = data["recaptcha_token"]

        if not user_email or not user_password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        if "@" not in user_email:
            return jsonify({"success": False, "message": "Invalid email address"}), 400
        try:
            if user_email.split("@")[1] != "krmu.edu.in":
                return jsonify({"success": False, "message": "Only K.R. Mangalam University email addresses are allowed"}), 400
        except IndexError:
            return jsonify({"success": False, "message": "Only K.R. Mangalam University email addresses are allowed"}), 400

        session["user_email"] = user_email

        if len(user_password) < 8:
            return jsonify({"success": False, "message": "Password must be at least 8 characters long"}), 400

        if not verify_recaptcha(recaptcha_token):
            return jsonify({"success": False, "message": "Suspicious activity detected, try again later or contact support"}), 400

        if MONGODB_DB["student_info"].find_one({"email": user_email}) is None:
            return jsonify({"success": False, "message": "This email is not registered with KRMU"}), 400

        if MONGODB_DB["users"].find_one({"user_email": user_email}):
            return jsonify({"success": False, "message": "This email address is already registered with us, try logging in"}), 400

        hashed_password = hash_password(user_password)

        if not send_email(user_email, "verify_new_user"):
            return jsonify({"success": False, "message": "Unable to send verification email, try again later or contact support"}), 500

        MONGODB_DB["users"].insert_one({
            "user_email": user_email,
            "user_hashed_password": hashed_password,
            "email_verified": True,
            "user_created_at": get_current_timestamp(),
            "user_role": "student",
            "user_profile": {
                "user_name": MONGODB_DB["student_info"].find_one({"email": user_email})["name"] if MONGODB_DB["student_info"].find_one({"email": user_email}) else user_email.split("@")[0],
                "user_branch": MONGODB_DB["student_info"].find_one({"email": user_email})["branch"] if MONGODB_DB["student_info"].find_one({"email": user_email}) else "Not Available",
                "user_year": MONGODB_DB["student_info"].find_one({"email": user_email})["year"] if MONGODB_DB["student_info"].find_one({"email": user_email}) else "Not Available",
                "user_roll_no": MONGODB_DB["student_info"].find_one({"email": user_email})["roll_no"] if MONGODB_DB["student_info"].find_one({"email": user_email}) else "Not Available",
                "user_phone": MONGODB_DB["student_info"].find_one({"email": user_email})["phone"] if MONGODB_DB["student_info"].find_one({"email": user_email}) else "Not Available",
            },
            "user_notifications": [
                {
                    "notification_id": 1,
                    "notification_title": "Welcome to KRMU",
                    "notification_body": "Welcome to KRMU's official app. We hope you have a great experience.",
                    "notification_created_at": get_current_timestamp(),
                    "notification_read": False
                }
            ]
        })

        return jsonify({"success": True, "message": "User created successfully"}), 200


@app.route("/login", methods=["GET", "POST"])
@app.route("/sign-in", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def signin():
    """ This function handles the logic for logging in a user

    Returns:
        _type_: flask.render_template or flask.redirect or flask.jsonify
    """
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("index"))
        return render_template("signin.html")
    else:
        if session.get("logged_in"):
            return redirect(url_for("index"))
        data = request.get_json()

        user_email = data["email"].lower()
        user_password = data["password"]
        recaptcha_token = data["recaptcha_token"]

        if not user_email or not user_password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        if "@" not in user_email:
            return jsonify({"success": False, "message": "Invalid email address"}), 400
        try:
            if user_email.split("@")[1] != "krmu.edu.in":
                return jsonify({"success": False, "message": "Only K.R. Mangalam University email addresses are allowed"}), 400
        except IndexError:
            return jsonify({"success": False, "message": "Only K.R. Mangalam University email addresses are allowed"}), 400

        session["user_email"] = user_email

        if not verify_recaptcha(recaptcha_token):
            return jsonify({"success": False, "message": "Suspicious activity detected, try again later or contact support"}), 400

        if MONGODB_DB["users"].find_one({"user_email": user_email}) is None:
            return jsonify({"success": False, "message": "This email address is not registered with us, try signing up"}), 400

        if not verify_hashed_password(user_password, MONGODB_DB["users"].find_one({"user_email": user_email})["user_hashed_password"]):
            return jsonify({"success": False, "message": "Incorrect email address or password combination"}), 400

        if not MONGODB_DB["users"].find_one({"user_email": user_email})["email_verified"]:
            return jsonify({"success": False, "message": "Email not verified, check your inbox for verification email"}), 400

        session["logged_in"] = True
        session["user_role"] = MONGODB_DB["users"].find_one(
            {"user_email": user_email})["user_role"]
        session["user_email"] = user_email
        session["user_name"] = MONGODB_DB["users"].find_one({"user_email": user_email})[
            "user_profile"]["user_name"]
        session["user_branch"] = MONGODB_DB["users"].find_one(
            {"user_email": user_email})["user_profile"]["user_branch"]
        session["user_year"] = MONGODB_DB["users"].find_one({"user_email": user_email})[
            "user_profile"]["user_year"]

        return jsonify({"success": True, "message": "User logged in successfully"}), 200


@app.route("/dashboard")
@limiter.limit("10 per minute")
def dashboard():
    """ This function handles the logic for the dashboard page

    Returns:
        _type_: flask.render_template or flask.redirect
    """
    if not session.get("logged_in"):
        return redirect(url_for("signin"))
    return render_template("dashboard.html")


@app.route("/send-notification", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def send_notification():
    """ This function handles the logic for sending a notification to all users

    Returns:
        _type_: flask.jsonify
    """

    if not session.get("logged_in"):
        return redirect(url_for("signin"))
    title = request.args.get("title")
    body = request.args.get("body")
    link = request.args.get("link")

    notification = {
        "notification_id": get_current_timestamp(),
        "notification_title": title,
        "notification_body": body,
        "notification_link": link,
        "notification_created_at": get_current_timestamp(),
        "id": secrets.token_hex(16),
        "ttl": 86400,
    }

    if not title or not body:
        return jsonify({"success": False, "message": "Title and body are required"}), 400
    users = MONGODB_DB["users"].find()
    for user in users:
        if user["user_push_subscription"] is not None:
            for subscription in user["user_push_subscription"]:
                try:
                    push.send(subscription['subscription'], notification)
                except WebPushException:
                    MONGODB_DB["users"].update_one({"user_email": user["user_email"]}, {"$pull": {
                        "user_push_subscription": {"notification-identifier": subscription["notification-identifier"]}}})
    return jsonify({"success": True, "message": "Notification sent successfully"}), 200


@app.route("/logout")
@app.route("/sign-out")
@limiter.limit("10 per minute")
def logout():
    """ This function handles the logic for logging out a user

    Returns:
        _type_: flask.redirect
    """
    if not session.get("logged_in"):
        return redirect(url_for("signin"))
    session.clear()
    return redirect(url_for("signin"))

# API Routes


@app.route("/api/push-notification/subscribe", methods=["POST"])
@limiter.limit("10 per minute")
def push_notification_subscribe():
    """ This function handles the logic for subscribing a user to push notifications

    Returns:
        _type_: flask.jsonify
    """
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "User not logged in"}), 400
    data = request.get_json()
    if data is None:
        return jsonify({"success": False, "message": "Invalid subscription data"}), 400
    if data['subscription'] is None:
        return jsonify({"success": False, "message": "Invalid subscription data"}), 400
    if not data['subscription']["endpoint"] or not data['subscription']["keys"]["auth"] or not data['subscription']["keys"]["p256dh"]:
        return jsonify({"success": False, "message": "Invalid subscription data"}), 400
    if MONGODB_DB["users"].find_one({"user_email": session["user_email"]}) is None:
        return jsonify({"success": False, "message": "User not found"}), 400
    for subscription in MONGODB_DB["users"].find_one({"user_email": session["user_email"]})["user_push_subscription"]:
        if subscription["notification-identifier"] == data["notification-identifier"]:
            MONGODB_DB["users"].update_one({"user_email": session["user_email"]}, {"$pull": {
                                           "user_push_subscription": {"notification-identifier": data["notification-identifier"]}}})
    MONGODB_DB["users"].update_one({"user_email": session["user_email"]}, {
                                   "$push": {"user_push_subscription": data}})

    return jsonify({"success": True, "message": "User subscribed to push notifications successfully"}), 200


@app.route("/create-job-posting", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def create_job_posting():
    """ This function handles the logic for creating a new job posting

      Returns:
          _type_: flask.render_template or flask.redirect or flask.jsonify
    """
    if request.method == "GET":
        return render_template("create_job_posting.html")
    else:
        data = request.get_json()
        if data is None:
            return jsonify({"success": False, "message": "Invalid job posting data"}), 400
        if not data["job_title"] or not data["job_description"] or not data["job_location"] or not data["job_salary"] or not data["job_company"] or not data["job_link"]:
            return jsonify({"success": False, "message": "Invalid job posting data"}), 400
        MONGODB_DB["job_postings"].insert_one({
            "job_title": data["job_title"],
            "job_description": data["job_description"],
            "job_location": data["job_location"],
            "job_salary": data["job_salary"],
            "job_company": data["job_company"],
            "job_link": data["job_link"],
            "job_created_at": get_current_timestamp(),
            'verified': False,
            'public': False,
        })
        return jsonify({"success": True, "message": "Job posting created successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
