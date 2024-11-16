import os
import requests
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# LinkedIn API credentials from environment variables
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'r_liteprofile r_emailaddress'

# Step 1: Redirect user to LinkedIn for authentication
@app.route('/auth/linkedin')
def linkedin_login():
    linkedin_auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    )
    return redirect(linkedin_auth_url)

# Step 2: LinkedIn redirects here with authorization code
@app.route('/auth/linkedin/callback')
def linkedin_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code found"}), 400

    # Step 3: Exchange authorization code for access token
    access_token = get_access_token(code)
    if access_token:
        profile = get_user_profile(access_token)
        connections = get_linkedin_connections(access_token)
        return jsonify({"profile": profile, "connections": connections})
    else:
        return jsonify({"error": "Failed to obtain access token"}), 500

def get_access_token(code):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url,

