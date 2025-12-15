# Small adapter to run the Flask WSGI app as an ASGI app using asgiref
# Vercel's Python builder can handle ASGI apps when the function file exports
# an ASGI callable. We convert the existing Flask WSGI app to ASGI here.
from asgiref.wsgi import WsgiToAsgi

from src.app import app as flask_app

# Convert WSGI Flask app to ASGI and export it as `app`
asgi_app = WsgiToAsgi(flask_app)
app = asgi_app
