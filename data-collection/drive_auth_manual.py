#!/usr/bin/env python3
"""
Manual Google Drive Authentication for Headless Environments
Uses authorization code flow with manual code entry
"""

import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = './config/credentials.json'
TOKEN_FILE = './config/token.pickle'

def authenticate_manual():
    """
    Authenticate using manual authorization code entry.
    This works in headless environments where browser redirect isn't possible.
    """

    # Check for existing valid token
    creds = None
    if os.path.exists(TOKEN_FILE):
        print("Loading existing token...")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if creds and creds.valid:
        print("Existing token is valid!")
        return creds

    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print("Token refreshed successfully!")
            return creds
        except Exception as e:
            print(f"Token refresh failed: {e}")
            print("Need to re-authenticate...")

    # Load client configuration
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        return None

    with open(CREDENTIALS_FILE, 'r') as f:
        client_config = json.load(f)

    # Get client details
    if 'installed' in client_config:
        client_id = client_config['installed']['client_id']
        client_secret = client_config['installed']['client_secret']
    elif 'web' in client_config:
        client_id = client_config['web']['client_id']
        client_secret = client_config['web']['client_secret']
    else:
        print("Invalid credentials.json format")
        return None

    # Build authorization URL (using localhost redirect)
    redirect_uri = "http://localhost:8080"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/drive.file&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    print("\n" + "="*70)
    print("GOOGLE DRIVE AUTHENTICATION")
    print("="*70)
    print("\nSTEP 1: Open this URL in your browser:")
    print("-"*70)
    print(auth_url)
    print("-"*70)
    print("\nSTEP 2: Sign in and authorize the application")
    print("\nSTEP 3: After authorization, you'll be redirected to localhost")
    print("        which will show an error (that's expected!)")
    print("\nSTEP 4: Copy the 'code' parameter from the URL bar")
    print("        Example: http://localhost:8080?code=4/0AfJoh...&scope=...")
    print("        Copy just the code part: 4/0AfJoh...")
    print("="*70)

    code = input("\nPaste the authorization code here: ").strip()

    if not code:
        print("No code provided!")
        return None

    # Exchange code for tokens
    import requests
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    print("\nExchanging code for tokens...")
    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        print(f"Token exchange failed: {response.text}")
        return None

    token_data = response.json()

    # Create credentials object
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )

    # Save token
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)

    print("\nAuthentication successful!")
    print(f"Token saved to: {TOKEN_FILE}")

    return creds

def test_drive_connection(creds):
    """Test the Drive connection by listing files."""
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"\nDrive connection test: SUCCESS")
        print(f"Found {len(files)} files in Drive")
        return True
    except Exception as e:
        print(f"\nDrive connection test FAILED: {e}")
        return False

if __name__ == '__main__':
    creds = authenticate_manual()
    if creds:
        test_drive_connection(creds)
    else:
        print("\nAuthentication failed!")
        exit(1)
