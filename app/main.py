import os
import functions
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_session import Session

load_dotenv()

app = Flask(__name__)

# Setting up secret key
app.secret_key = os.environ.get("SECRET_KEY")

# Connecting to MongoDB
MONGODB_URI = MongoClient(os.environ.get("MONGODB_URI"))
MONGODB_DB = MONGODB_URI["KRMU"]

# Setting up session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setting up rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "2000 per hour"],
    storage_uri="memory://"
)


@app.route("/sign-up", methods=["GET", "POST"])
@limiter.limit("20000000 per hour")
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

        if not functions.verify_recaptcha(recaptcha_token):
            return jsonify({"success": False, "message": "Suspicious activity detected, try again later or contact support"}), 400

        if MONGODB_DB["users"].find_one({"email": user_email}):
            return jsonify({"success": False, "message": "This email address is already registered with us"}), 400

        hashed_password = functions.hash_password(user_password)

        if not functions.send_email(user_email, "verify_new_user"):
            return jsonify({"success": False, "message": "Unable to send verification email, try again later or contact support"}), 500

        functions.send_notification(
            user_email, "Welcome to KRMU", "Welcome to KRMU's official app. We hope you have a great experience.")

        MONGODB_DB["users"].insert_one({
            "user_email": user_email,
            "user_hashed_password": hashed_password,
            "email_verified": True,
            "user_created_at": functions.get_current_timestamp(),
            "user_role": "student",
            "user_profile": {
                "user_name": MONGODB_DB["student_info"].find_one({"roll_no": user_email.split("@")[0]})["name"] if MONGODB_DB["student_info"].find_one({"roll_no": user_email.split("@")[0]}) else user_email.split("@")[0],
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
                    "notification_created_at": functions.get_current_timestamp(),
                    "notification_read": False
                }
            ]
        })

        return jsonify({"success": True, "message": "User created successfully"}), 201


if __name__ == "__main__":
    app.run(debug=True)
