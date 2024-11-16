import os
import requests
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# LinkedIn API credentials from environment variables
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')  # e.g., http://localhost:5000/auth/linkedin/callback
SCOPE = 'r_liteprofile r_emailaddress w_member_social'

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
        return "Error: No authorization code found", 400

    # Step 3: Exchange authorization code for access token
    access_token = get_access_token(code)

    if access_token:
        # Fetch user profile
        profile = get_user_profile(access_token)
        
        # Fetch user connections
        connections = get_linkedin_connections(access_token)
        
        # Combine profile and connections data
        result = {
            "profile": profile,
            "connections": connections
        }

        return jsonify(result)
    else:
        return "Error: Unable to retrieve access token", 500

def get_access_token(code):
    """Exchange the authorization code for an access token."""
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("Error obtaining access token:", response.json())
        return None

def get_user_profile(access_token):
    """Retrieve user's LinkedIn profile information."""
    url = "https://api.linkedin.com/v2/me"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching user profile:", response.json())
        return {}

def get_linkedin_connections(access_token):
    """Retrieve first-degree connections from LinkedIn."""
    url = "https://api.linkedin.com/v2/connections"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching connections:", response.json())
        return {}

if __name__ == '__main__':
    app.run(debug=True)
