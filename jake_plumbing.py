from flask import Flask, render_template, request, redirect, flash, session, url_for
from datetime import datetime
from functools import wraps
import os
import sys

import requests
from dotenv import load_dotenv
from flask_talisman import Talisman
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import database as db
from notifications import send_booking_notification


# ENVIRONMENT / CONFIGURATION

load_dotenv()

FLASK_ENV = os.environ.get("FLASK_ENV", "production").lower()
IS_PRODUCTION = FLASK_ENV == "production"

# Required secrets 
SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

if not SECRET_KEY:
    sys.exit(
        "FATAL: SECRET_KEY is not set. Create a .env file (see .env.example) "
        "or set the SECRET_KEY environment variable before starting the app."
    )

if not ADMIN_PASSWORD:
    sys.exit(
        "FATAL: ADMIN_PASSWORD is not set. Create a .env file (see .env.example) "
        "or set the ADMIN_PASSWORD environment variable before starting the app."
    )

ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://www.example.com")

TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")


app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["DEBUG"] = (not IS_PRODUCTION) and (os.environ.get("FLASK_DEBUG", "0") == "1")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = IS_PRODUCTION


# SECURITY HEADERS (Flask-Talisman)

csp = {
    "default-src": "'self'",
    "script-src": [
        "'self'",
        "https://challenges.cloudflare.com",
    ],
    "style-src": [
        "'self'",
        "https://fonts.googleapis.com",
        # Templates currently use inline <style> blocks; remove this once
        # those are moved into style.css or given nonces.
        "'unsafe-inline'",
    ],
    "font-src": [
        "'self'",
        "https://fonts.gstatic.com",
    ],
    "img-src": ["'self'", "data:"],
    "frame-src": ["https://challenges.cloudflare.com"],
    "connect-src": ["'self'", "https://challenges.cloudflare.com"],
    "object-src": "'none'",
    "base-uri": "'self'",
    "frame-ancestors": "'self'",
}

Talisman(
    app,
    force_https=IS_PRODUCTION,       # don't force HTTPS on local http dev servers
    strict_transport_security=IS_PRODUCTION,
    session_cookie_secure=IS_PRODUCTION,
    content_security_policy=csp,
    frame_options="SAMEORIGIN",      # anti-clickjacking
    x_content_type_options=True,
    referrer_policy="strict-origin-when-cross-origin",
)


# CORS (locked to the production domain only)

CORS(
    app,
    resources={r"/book": {"origins": ALLOWED_ORIGIN}},
    supports_credentials=True,
    methods=["POST"],
)


# RATE LIMITING (Flask-Limiter)
# Default in-memory storage is fine for a single-process dev server. If you
# run multiple workers/processes in production, point storage_uri at a
# shared backend (e.g. Redis: "redis://localhost:6379") so limits are
# enforced consistently across all of them -- otherwise each worker keeps
# its own separate counter and the effective limit is (N * worker_count).
BOOKING_RATE_LIMIT = os.environ.get("BOOKING_RATE_LIMIT", "5 per minute")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    default_limits=[],  # no global default -- limits are applied per-route
)


ALL_TIME_SLOTS = [
    "8:00 AM - 11:00 AM",
    "11:00 AM - 2:00 PM",
    "2:00 PM - 5:00 PM",
]

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token, remote_ip=None):
    """
    Verify a Cloudflare Turnstile token server-side. The widget on its own
    only protects the UI -- anyone can bypass the browser entirely and POST
    straight to /book, so the token must be re-checked here before we
    trust the submission.
    """
    if not TURNSTILE_SECRET_KEY:
        # Fail closed: if the secret isn't configured, refuse bookings
        # rather than silently accepting unverified submissions.
        app.logger.error("TURNSTILE_SECRET_KEY is not configured; rejecting booking.")
        return False

    if not token:
        return False

    try:
        response = requests.post(
            TURNSTILE_VERIFY_URL,
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": remote_ip,
            },
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        return bool(result.get("success"))
    except (requests.RequestException, ValueError):
        # Network failure or malformed response -- treat as unverified.
        return False


# Create the database/table on startup if it doesn't exist yet
db.init_db()


# HOME

@app.route("/")
@app.route("/home.html")
@app.route("/index.html")
def home():
    booked_times = db.get_booked_times_for_today()
    return render_template(
        "index.html",
        booked_times=booked_times
    )


# STATIC PAGES


@app.route("/about.html")
@app.route("/about")
def about():

    return render_template(
        "about.html"
    )




@app.route("/services")
@app.route("/services.html")
def services():

    return render_template(
        "services.html"
    )





@app.route("/emergency-plumbing")
@app.route("/emergency plumbing")
def emergency():

    return render_template(
        "emergency-plumbing.html"
    )





@app.route("/drain-cleaning")
def drain():

    return render_template( "drain-cleaning.html" )





@app.route("/water-heater")
def water_heater():
    return render_template("water-heater.html")


@app.route("/leak-detection")
def leak_detection():

    return render_template("leak-detection.html")


@app.route("/service-areas")
def service_area():

    return render_template("service-areas.html")

@app.route("/reviews.html")
@app.route("/reviews")
@app.route("/Reviews")
def reviews():

    return render_template("reviews.html")


@app.route("/contact")
@app.route("/contact.html")
def contact():

    return render_template("contact.html")


# BOOKING SYSTEM


@app.route("/book", methods=["POST"])
@limiter.limit(BOOKING_RATE_LIMIT)
def book():

    # script.js submits this form as JSON. request.form is kept as a
    # fallback so the endpoint still works if JS is disabled/unavailable
    # and the browser falls back to a normal form-encoded POST.
    wants_json = request.is_json
    data = request.get_json(silent=True)
    if data is None:
        data = request.form

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    time = (data.get("time") or "").strip()
    service = (data.get("service") or "").strip()
    # Front end sends "address"; older form-encoded fallback used "Address".
    address = (data.get("address") or data.get("Address") or "").strip()
    turnstile_token = data.get("cf-turnstile-response", "")

    def reject(message, status_code):
        if wants_json:
            return {"message": message}, status_code
        flash(message)
        return redirect("/")

    #  Security checkpoint 1: rate limit 
    # Enforced by the @limiter.limit(...) decorator above; if the caller
    # is over the limit, Flask-Limiter raises before this function body
    # ever runs, so no field validation or DB access happens for
    # rate-limited requests. See the 429 error handler below.

    # --- Security checkpoint 2: input presence/shape 
    if not all([name, phone, time, service, address]):
        return reject("Please fill in all required fields.", 400)

    if time not in ALL_TIME_SLOTS:
        return reject("Please choose a valid time slot.", 400)

    # Security checkpoint 3: Turnstile verification 
    # This call happens before any SQLite query runs. If verification
    # fails, we return immediately and db.is_slot_taken/db.create_reservation
    # are never reached.
    if not verify_turnstile(turnstile_token, request.remote_addr):
        return reject("Verification failed. Please try again.", 400)

    today = datetime.now().strftime("%Y-%m-%d")

    # First-come-first-served: if this slot is already taken today, reject it.
    if db.is_slot_taken(today, time):
        return reject("Sorry, that time slot just got booked. Please pick another one.", 409)

    # The reservations table stores this field as "message"; we're using it
    # to hold the service address collected from the booking form.
    db.create_reservation(name, phone, today, time, service, address)

    # Notify the business owner by email (won't crash booking if email fails)
    send_booking_notification(name, phone, today, time, service, address)

    success_message = "Reservation submitted successfully! We'll confirm by phone shortly."
    if wants_json:
        return {"message": success_message}, 200
    flash(success_message)
    return redirect("/")


@app.errorhandler(429)
def ratelimit_handler(e):
    """
    Flask-Limiter raises a 429 before the /book view function body runs at
    all when a caller exceeds BOOKING_RATE_LIMIT, so no request data is
    read and no SQLite query is ever attempted for throttled requests.
    """
    if request.is_json or request.path == "/book":
        return {"message": "Too many requests. Please wait a moment and try again."}, 429
    flash("Too many requests. Please wait a moment and try again.")
    return redirect("/")


# ADMIN AREA

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapped


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect password.")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    reservations = db.get_all_reservations()
    return render_template("admin.html", reservations=reservations)


@app.route("/admin/cancel/<int:reservation_id>", methods=["POST"])
@login_required
def admin_cancel(reservation_id):
    db.cancel_reservation(reservation_id)
    flash("Appointment cancelled. That time slot is now available again.")
    return redirect(url_for("admin_dashboard"))


# ADMIN CALENDAR DRILL-DOWN (new)

@app.route("/admin/calendar")
@login_required
def admin_calendar():
    months = db.get_monthly_summary()
    return render_template("admin_calendar_months.html", months=months)


@app.route("/admin/calendar/<month>")
@login_required
def admin_calendar_month(month):
    days = db.get_daily_summary(month)
    return render_template("admin_calendar_days.html", days=days, month=month)


@app.route("/admin/calendar/<month>/<date>")
@login_required
def admin_calendar_day(month, date):
    reservations = db.get_reservations_for_date(date)
    return render_template("admin_calendar_day.html", reservations=reservations, date=date, month=month)


# RUN SERVER

if __name__ == "__main__":

    # debug is derived from app.config["DEBUG"] above -- never hardcoded True.
    # In production this must be run behind a real WSGI server (gunicorn,
    # waitress, etc.), not Flask's built-in dev server.
    app.run(
        host="127.0.0.1" if not IS_PRODUCTION else "0.0.0.0",
        port=5001,
        debug=app.config["DEBUG"],
    )