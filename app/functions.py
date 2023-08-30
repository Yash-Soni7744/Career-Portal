import bcrypt
import datetime


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

def send_notification(email, notification_title, notification_body):
    pass

def verify_recaptcha(recaptcha_token):
    return True
