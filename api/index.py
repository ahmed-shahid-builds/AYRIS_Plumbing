import sys
import os

# Make the project root importable so "from jake_plumbing import app" works
# no matter how Vercel invokes this file.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jake_plumbing import app  # noqa: E402

# Vercel's Python runtime looks for a WSGI-compatible callable named "app"
# in this file. Flask's `app` object already is one, so nothing else is
# needed here.
