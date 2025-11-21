# LawBrain - Vertex AI Authentication Setup

Since you're using Vertex AI (not Google Colab), you need to set up authentication for your Google Cloud project `lool-471716`.

## Option 1: Using Service Account (Recommended for Codespaces)

### Step 1: Create a Service Account Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts?project=lool-471716)
2. Click "Create Service Account"
3. Name it: `lawbrain-service-account`
4. Click "Create and Continue"
5. Grant it the **"Vertex AI User"** role
6. Click "Done"
7. Click on the service account you just created
8. Go to "Keys" tab
9. Click "Add Key" → "Create new key"
10. Choose "JSON"
11. Download the JSON key file

### Step 2: Upload the Key to Codespace

1. In your codespace, upload the JSON file to `/workspaces/lool-/lawbrain/`
2. Rename it to `service-account-key.json`

### Step 3: Update .env File

Add this line to your `.env` file:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/workspaces/lool-/lawbrain/service-account-key.json
```

### Step 4: Add to .gitignore

Make sure the key is NOT committed to git:
```bash
echo "service-account-key.json" >> .gitignore
```

## Option 2: Using Application Default Credentials (Alternative)

If you have `gcloud` installed locally on your machine:

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth application-default login
```

Then copy the credentials file from:
- Linux/Mac: `~/.config/gcloud/application_default_credentials.json`
- Windows: `%APPDATA%\gcloud\application_default_credentials.json`

To your codespace at: `/home/codespace/.config/gcloud/application_default_credentials.json`

## Verification

Once authentication is set up, test it:

```bash
cd /workspaces/lool-/lawbrain
python -c "from agent import app; print('✅ Authentication successful!')"
```

## Enable Vertex AI API

Make sure Vertex AI API is enabled for your project:
https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project=lool-471716

Click "Enable" if it's not already enabled.
