# LawBrain Authentication Setup

Your LawBrain system uses **Google Cloud Vertex AI** with Project ID: `lool-471716`

## Step 1: Create a Service Account

1. Go to Google Cloud Console: https://console.cloud.google.com/iam-admin/serviceaccounts?project=lool-471716

2. Click **"+ CREATE SERVICE ACCOUNT"**

3. Fill in:
   - **Name**: `lawbrain-service-account`
   - **Description**: `Service account for LawBrain AI Law Firm`
   - Click **CREATE AND CONTINUE**

4. Grant these roles:
   - **Vertex AI User** (roles/aiplatform.user)
   - Click **CONTINUE**, then **DONE**

## Step 2: Create and Download JSON Key

1. Click on the service account you just created

2. Go to the **KEYS** tab

3. Click **ADD KEY** → **Create new key**

4. Choose **JSON** format

5. Click **CREATE** - This will download a JSON file

## Step 3: Configure LawBrain

1. Upload the JSON key file to this directory: `/workspaces/lool-/lawbrain/`

2. Rename it to something simple like: `service-account-key.json`

3. Update your `.env` file:
   ```bash
   GOOGLE_CLOUD_PROJECT=lool-471716
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=/workspaces/lool-/lawbrain/service-account-key.json
   ```

4. **IMPORTANT**: Add to `.gitignore` to avoid committing the key:
   ```bash
   echo "service-account-key.json" >> .gitignore
   echo "*.json" >> .gitignore
   ```

## Step 4: Test the Setup

Run:
```bash
python test_direct.py
```

## Alternative: Use Colab

If you prefer, you can run LawBrain in Google Colab where authentication is simpler:

1. Upload `agent.py` to Colab
2. Run:
   ```python
   from google.colab import auth
   auth.authenticate_user(project_id="lool-471716")
   ```
3. Then run your LawBrain code

## Troubleshooting

### Error: "Could not automatically determine credentials"
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct JSON file path
- Check that the file exists and is readable

### Error: "Permission Denied"
- Verify the service account has the "Vertex AI User" role
- Check that Vertex AI API is enabled: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project=lool-471716

### Error: "Project not found"
- Verify your project ID is correct: `lool-471716`
- Make sure you have access to the project
