#!/usr/bin/env python3
"""
Fast parallel upload to Google Drive using ThreadPoolExecutor
"""

import os
import pickle
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

TOKEN_FILE = './config/token.pickle'
SOURCE_DIR = './data/pdfs/bangladesh/bdlaws'
DRIVE_ROOT_FOLDER_NAME = 'Bangladesh_Laws'
MAX_WORKERS = 10  # Parallel uploads

# Thread-safe counters
stats = {'uploaded': 0, 'skipped': 0, 'errors': 0}
stats_lock = Lock()
folder_cache = {}
folder_lock = Lock()

def load_credentials():
    with open(TOKEN_FILE, 'rb') as token:
        creds = pickle.load(token)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_service():
    """Create a new service instance for each thread."""
    creds = load_credentials()
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, name, parent_id=None):
    """Get existing folder or create new one (cached)."""
    cache_key = f"{parent_id}:{name}"

    with folder_lock:
        if cache_key in folder_cache:
            return folder_cache[cache_key]

    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if files:
        folder_id = files[0]['id']
    else:
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]
        folder = service.files().create(body=metadata, fields='id').execute()
        folder_id = folder['id']

    with folder_lock:
        folder_cache[cache_key] = folder_id

    return folder_id

def upload_single_file(args):
    """Upload a single file (called by thread pool)."""
    file_path, year, root_folder_id = args

    try:
        service = get_service()

        # Get or create year folder
        year_folder_id = get_or_create_folder(service, year, root_folder_id)

        file_name = os.path.basename(file_path)

        # Check if exists
        query = f"name='{file_name}' and '{year_folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()

        if results.get('files'):
            with stats_lock:
                stats['skipped'] += 1
            return 'skipped', file_name

        # Upload
        mime_type = 'application/pdf' if file_path.endswith('.pdf') else 'text/html'
        metadata = {'name': file_name, 'parents': [year_folder_id]}
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        service.files().create(body=metadata, media_body=media, fields='id').execute()

        with stats_lock:
            stats['uploaded'] += 1
        return 'uploaded', file_name

    except Exception as e:
        with stats_lock:
            stats['errors'] += 1
        return 'error', f"{file_path}: {e}"

def main():
    print(f"Starting parallel upload with {MAX_WORKERS} workers...")

    # Setup
    service = get_service()
    root_folder_id = get_or_create_folder(service, DRIVE_ROOT_FOLDER_NAME)
    print(f"Root folder: {root_folder_id}")

    # Collect all files
    source_path = Path(SOURCE_DIR)
    tasks = []

    for year_folder in sorted(source_path.iterdir()):
        if year_folder.is_dir():
            year = year_folder.name
            for file_path in year_folder.iterdir():
                tasks.append((str(file_path), year, root_folder_id))

    total = len(tasks)
    print(f"Total files: {total}")
    print("=" * 60)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(upload_single_file, task): task for task in tasks}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            status, info = future.result()

            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            remaining = (total - completed) / rate if rate > 0 else 0

            with stats_lock:
                u, s, e = stats['uploaded'], stats['skipped'], stats['errors']

            print(f"\r[{completed}/{total}] Up:{u} Skip:{s} Err:{e} | "
                  f"Rate:{rate:.1f}/s | ETA:{remaining/60:.1f}min", end="", flush=True)

    elapsed = time.time() - start_time
    print(f"\n\n{'=' * 60}")
    print(f"COMPLETE in {elapsed/60:.1f} minutes")
    print(f"Uploaded: {stats['uploaded']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nDrive folder: https://drive.google.com/drive/folders/{root_folder_id}")

if __name__ == '__main__':
    main()
