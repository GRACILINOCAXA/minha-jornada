import os

os.environ.setdefault('FLASK_ENV', 'production')

from backend.app import app

# Expose the Flask app object required by WSGI and serverless hosts.
# Vercel uses this import path to serve the application.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
