import os
import requests
from flask import Flask, redirect, request, jsonify, session
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

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
        return "Error: No authorization code found", 400

    # Step 3: Exchange authorization code for access token
    access_token = get_access_token(code)

    if access_token:
        # Fetch user profile
        profile = get_user_profile(access_token)

        # Fetch user connections
        connections = get_linkedin_connections(access_token)
        
        # Check for any changes in the profiles of the user's connections
        connection_changes = check_connection_changes(connections)
        
        # Combine profile and changes data
        result = {
            "profile": profile,
            "connections": connections,
            "connection_changes": connection_changes
        }

        # Store the data in session for easy access in frontend
        session['user_data'] = result

        # Redirect to the main page to display data
        return redirect('/dashboard')

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
    url = "https://api.linkedin.com/v2/connections?q=firstName,lastName"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching connections:", response.json())
        return {}

def check_connection_changes(connections):
    """Check for changes in user connections' profiles (mocked for simplicity)."""
    connection_changes = []

    # Iterate through the connections and check for profile updates (mocked here)
    for connection in connections.get('elements', []):
        last_updated = connection.get('lastUpdated', None)
        if last_updated:
            last_updated = datetime.strptime(last_updated, '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_updated > datetime.now() - timedelta(days=7):
                connection_changes.append({
                    'name': f"{connection['firstName']['localized']['en_US']} {connection['lastName']['localized']['en_US']}",
                    'updated_at': last_updated.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return connection_changes

# Route to display the user's dashboard with profile, connections, and changes
@app.route('/dashboard')
def dashboard():
    if 'user_data' not in session:
        return redirect('/')
    
    data = session['user_data']
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)


