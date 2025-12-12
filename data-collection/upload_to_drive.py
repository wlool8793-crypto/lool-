#!/usr/bin/env python3
"""
Upload Bangladesh law files to Google Drive
Organizes files by year in folders
"""

import os
import pickle
import time
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

TOKEN_FILE = './config/token.pickle'
SOURCE_DIR = './data/pdfs/bangladesh/bdlaws'
DRIVE_ROOT_FOLDER_NAME = 'Bangladesh_Laws'

def load_credentials():
    """Load saved credentials."""
    with open(TOKEN_FILE, 'rb') as token:
        creds = pickle.load(token)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_or_create_folder(service, name, parent_id=None):
    """Get existing folder or create new one."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']

    # Create folder
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]

    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']

def upload_file(service, file_path, folder_id):
    """Upload a file to Google Drive."""
    file_name = os.path.basename(file_path)

    # Check if file already exists
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    if results.get('files'):
        return results['files'][0]['id'], False  # Already exists

    # Determine mime type
    if file_path.endswith('.pdf'):
        mime_type = 'application/pdf'
    else:
        mime_type = 'text/html'

    metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields='id').execute()

    return file['id'], True  # Newly uploaded

def main():
    print("Loading credentials...")
    creds = load_credentials()
    service = build('drive', 'v3', credentials=creds)

    print(f"Creating root folder: {DRIVE_ROOT_FOLDER_NAME}")
    root_folder_id = get_or_create_folder(service, DRIVE_ROOT_FOLDER_NAME)
    print(f"Root folder ID: {root_folder_id}")

    # Get all year folders
    source_path = Path(SOURCE_DIR)
    year_folders = sorted([d for d in source_path.iterdir() if d.is_dir()])

    total_files = sum(len(list(yf.iterdir())) for yf in year_folders)
    print(f"\nTotal files to upload: {total_files}")
    print(f"Year folders: {len(year_folders)}")
    print("="*60)

    uploaded_count = 0
    skipped_count = 0
    error_count = 0
    start_time = time.time()

    for year_folder in year_folders:
        year = year_folder.name

        # Create year folder in Drive
        year_folder_id = get_or_create_folder(service, year, root_folder_id)

        files = list(year_folder.iterdir())

        for file_path in files:
            try:
                file_id, is_new = upload_file(service, str(file_path), year_folder_id)

                if is_new:
                    uploaded_count += 1
                else:
                    skipped_count += 1

                total_processed = uploaded_count + skipped_count + error_count
                elapsed = time.time() - start_time
                rate = total_processed / elapsed if elapsed > 0 else 0
                eta = (total_files - total_processed) / rate if rate > 0 else 0

                print(f"\r[{total_processed}/{total_files}] Year {year}: {file_path.name[:40]:<40} "
                      f"| Uploaded: {uploaded_count} | Skipped: {skipped_count} | "
                      f"Rate: {rate:.1f}/s | ETA: {eta/60:.1f}min", end="", flush=True)

            except Exception as e:
                error_count += 1
                print(f"\nError uploading {file_path.name}: {e}")

    elapsed = time.time() - start_time
    print(f"\n\n{'='*60}")
    print(f"UPLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"Total files: {total_files}")
    print(f"Uploaded: {uploaded_count}")
    print(f"Skipped (already existed): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"\nFiles available at: https://drive.google.com/drive/folders/{root_folder_id}")

if __name__ == '__main__':
    main()
