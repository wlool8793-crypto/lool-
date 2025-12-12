#!/usr/bin/env python3
"""
Simple Google Drive Authentication Script
Handles OAuth flow for remote/codespace environments
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    """Authenticate with Google Drive API."""

    credentials_file = './config/credentials.json'
    token_file = './config/token.pickle'

    creds = None

    # Load existing token if available
    if os.path.exists(token_file):
        print(f"Loading existing token from {token_file}...")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                print(f"ERROR: Credentials file not found: {credentials_file}")
                print("Please place credentials.json in the config folder")
                return False

            print("\n" + "="*70)
            print("Google Drive Authentication")
            print("="*70)
            print("\nStarting OAuth flow...")
            print("You'll get a URL to open in your browser.")
            print("="*70 + "\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                SCOPES
            )

            # Get the authorization URL with all required parameters
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )

            print("\n" + "="*70)
            print("STEP 1: Open this URL in your browser:")
            print("="*70)
            print(f"\n{auth_url}\n")
            print("="*70)
            print("STEP 2: After authorizing, you'll see a code.")
            print("        Copy that code and paste it below.")
            print("="*70 + "\n")

            code = input("Enter the authorization code: ").strip()

            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                print("\n✓ Authentication successful!")
            except Exception as e:
                print(f"\n✗ Authentication failed: {e}")
                return False

        # Save the credentials for future use
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✓ Token saved to: {token_file}")
    else:
        print("✓ Using existing valid credentials")

    print("\n" + "="*70)
    print("✓ Google Drive authentication complete!")
    print("="*70)
    return True

if __name__ == '__main__':
    success = authenticate()
    exit(0 if success else 1)
