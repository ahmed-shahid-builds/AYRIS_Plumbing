# AYRIS Plumbing

A portfolio project: a fictional plumbing business website with a full booking system, built to demonstrate end-to-end web development skills — from front-end pages to backend booking logic and deployment.

🔗 **Live demo:** [ayris-plumbing.vercel.app](https://ayris-plumbing.vercel.app)

## About

AYRIS Plumbing simulates a real-world small business website: customers can browse services and book a plumbing appointment directly through the site. It was built as a portfolio piece to showcase practical full-stack skills — page templating, a backend API, persistent storage for bookings, automated notifications, and a live production deployment — rather than as a real operating business.

## Features

- 🧰 **Service showcase** — informational pages describing the plumbing services offered
- 📅 **Online booking** — customers can request/schedule an appointment through the site
- 🗄️ **Persistent storage** — bookings and customer data are saved via the app's database layer
- 🔔 **Notifications** — automated alerts (e.g. email/SMS) when a new booking comes in
- ☁️ **Deployed on Vercel** — production build served directly from this repo

## Tech Stack

- **Backend:** Python
- **Templating:** HTML templates (Jinja-style) rendered from `templates/`
- **Static assets:** CSS/JS/images served from `static/`
- **Database:** Managed via `database.py`
- **Hosting/Deployment:** [Vercel](https://vercel.com) (configured via `vercel.json`)

> Note: adjust the framework name above (Flask/FastAPI/etc.) if it differs — happy to update once confirmed.

## Project Structure

```
AYRIS_Plumbing/
├── api/                  # Backend API routes/handlers
├── static/               # CSS, JS, images, and other static assets
├── templates/            # HTML page templates
├── .env.example          # Example environment variables (copy to .env)
├── .gitignore
├── database.py           # Database models / connection logic
├── jake_plumbing.py       # Core application entry point
├── notifications.py      # Booking notification logic (email/SMS alerts)
├── requirements.txt      # Python dependencies
└── vercel.json           # Vercel deployment configuration
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/ahmed-shahid-builds/AYRIS_Plumbing.git
   cd AYRIS_Plumbing
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp .env.example .env
   ```
   Then fill in `.env` with your own values (database URL, notification service keys, etc.).

5. Run the app locally
   ```bash
   python jake_plumbing.py
   ```

The site should now be running locally — check the console output for the local URL (typically `http://localhost:5000` or similar).

## Deployment

This project is configured for [Vercel](https://vercel.com) via `vercel.json` and deploys automatically from the `main` branch. The current production deployment is live at **[ayris-plumbing.vercel.app](https://ayris-plumbing.vercel.app)**.

To deploy your own copy:

1. Push this repo to your own GitHub account
2. Import the project into [Vercel](https://vercel.com/new)
3. Add the required environment variables (from `.env.example`) in the Vercel project settings
4. Deploy 🚀

## Environment Variables

See `.env.example` for the full list of variables required to run the project (database connection, notification service credentials, etc.). Never commit your actual `.env` file.

## About This Project

This repository is part of [ahmed-shahid-builds](https://github.com/ahmed-shahid-builds)'s developer portfolio, built to demonstrate skills in backend development, templating, and deployment. Feedback and suggestions are welcome via issues.

## License

No license has been specified for this project yet. Add a `LICENSE` file if you'd like to make usage terms explicit.

## Contact

Built by [ahmed-shahid-builds](https://github.com/ahmed-shahid-builds).