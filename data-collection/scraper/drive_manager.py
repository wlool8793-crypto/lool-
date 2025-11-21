"""
Google Drive Manager Module
Handles batch upload of PDFs to Google Drive with quota management
"""

import logging
import os
import pickle
import time
from pathlib import Path
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveManager:
    """Manages Google Drive uploads with batch processing and error handling."""

    def __init__(self, config: Dict):
        """
        Initialize Drive Manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.credentials_file = config.get('google_drive', {}).get(
            'credentials_file',
            './config/credentials.json'
        )
        self.token_file = './config/token.pickle'
        self.folder_name = config.get('storage', {}).get('drive_folder_name', 'IndianKanoon_PDFs')
        self.organize_by = config.get('storage', {}).get('organize_by', 'flat')  # flat/court/year
        self.batch_size = config.get('google_drive', {}).get('batch_size', 50)
        self.max_retries = config.get('google_drive', {}).get('max_retries', 3)

        # Service and credentials
        self.creds: Optional[Credentials] = None
        self.service = None

        # Folder ID cache
        self.folder_ids: Dict[str, str] = {}

        # Statistics
        self.stats = {
            'files_uploaded': 0,
            'bytes_uploaded': 0,
            'errors': 0,
            'retries': 0
        }

    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API using OAuth 2.0.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load credentials from token file if exists
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)

            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials...")
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.error("Please download credentials.json from Google Cloud Console")
                        return False

                    logger.info("Starting OAuth 2.0 authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next time
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                logger.info("✓ Credentials saved")

            # Build Drive service
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("✓ Google Drive API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive.

        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (None for root)

        Returns:
            Folder ID if successful, None otherwise
        """
        try:
            # Check if folder already exists in cache
            cache_key = f"{parent_id}:{folder_name}" if parent_id else folder_name
            if cache_key in self.folder_ids:
                return self.folder_ids[cache_key]

            # Check if folder exists on Drive
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])
            if files:
                folder_id = files[0]['id']
                logger.info(f"✓ Found existing folder: {folder_name} (ID: {folder_id})")
            else:
                # Create new folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    file_metadata['parents'] = [parent_id]

                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()

                folder_id = folder.get('id')
                logger.info(f"✓ Created folder: {folder_name} (ID: {folder_id})")

            # Cache folder ID
            self.folder_ids[cache_key] = folder_id
            return folder_id

        except HttpError as e:
            logger.error(f"Failed to create folder {folder_name}: {e}")
            return None

    def get_or_create_upload_folder(self, court: Optional[str] = None, year: Optional[int] = None) -> Optional[str]:
        """
        Get or create the appropriate upload folder based on organization strategy.

        Args:
            court: Court name (for court organization)
            year: Year (for year organization)

        Returns:
            Folder ID or None
        """
        # Create main folder
        main_folder_id = self.create_folder(self.folder_name)
        if not main_folder_id:
            return None

        # Flat structure - just use main folder
        if self.organize_by == 'flat':
            return main_folder_id

        # Organize by court
        if self.organize_by == 'court' and court:
            court_folder = court.replace('/', '_')  # Sanitize folder name
            return self.create_folder(court_folder, main_folder_id)

        # Organize by year
        if self.organize_by == 'year' and year:
            year_folder = str(year)
            return self.create_folder(year_folder, main_folder_id)

        # Default to main folder
        return main_folder_id

    def upload_file(self, file_path: str, folder_id: str, retries: int = 0) -> Optional[str]:
        """
        Upload a single file to Google Drive.

        Args:
            file_path: Path to the file to upload
            folder_id: ID of the folder to upload to
            retries: Current retry attempt

        Returns:
            File ID if successful, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # Check if file already exists
            query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])
            if files:
                logger.info(f"  ⊙ File already exists on Drive: {file_name}")
                return files[0]['id']

            # Upload file
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')

            # Update statistics
            self.stats['files_uploaded'] += 1
            self.stats['bytes_uploaded'] += file_size

            logger.info(f"  ✓ Uploaded: {file_name} ({file_size:,} bytes) → Drive ID: {file_id}")
            return file_id

        except HttpError as e:
            self.stats['errors'] += 1

            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                logger.error("Google Drive quota exceeded! Please wait or upgrade your account.")
                raise  # Re-raise to stop upload process

            if retries < self.max_retries:
                self.stats['retries'] += 1
                wait_time = (2 ** retries) * 2  # Exponential backoff
                logger.warning(f"  ⟳ Upload failed, retry {retries + 1}/{self.max_retries} in {wait_time}s: {e}")
                time.sleep(wait_time)
                return self.upload_file(file_path, folder_id, retries + 1)
            else:
                logger.error(f"  ✗ Failed to upload {file_path} after {self.max_retries} retries: {e}")
                return None

        except Exception as e:
            logger.error(f"Unexpected error uploading {file_path}: {e}")
            return None

    def upload_batch(self, file_paths: List[str], court: Optional[str] = None, year: Optional[int] = None) -> Dict:
        """
        Upload a batch of files to Google Drive.

        Args:
            file_paths: List of file paths to upload
            court: Optional court name for organization
            year: Optional year for organization

        Returns:
            Dictionary with upload statistics
        """
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Starting batch upload: {len(file_paths)} files")
        logger.info(f"{'=' * 70}")

        # Get or create upload folder
        folder_id = self.get_or_create_upload_folder(court, year)
        if not folder_id:
            logger.error("Failed to create upload folder")
            return {'success': False, 'uploaded': 0}

        uploaded_files = []
        failed_files = []

        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"\n[{i}/{len(file_paths)}] Uploading: {os.path.basename(file_path)}")

            file_id = self.upload_file(file_path, folder_id)
            if file_id:
                uploaded_files.append(file_path)
            else:
                failed_files.append(file_path)

            # Polite delay between uploads
            if i < len(file_paths):
                time.sleep(0.5)

        # Summary
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Batch Upload Complete")
        logger.info(f"{'=' * 70}")
        logger.info(f"Uploaded: {len(uploaded_files)}/{len(file_paths)}")
        logger.info(f"Failed: {len(failed_files)}")
        logger.info(f"Total bytes uploaded: {self.stats['bytes_uploaded']:,}")
        logger.info(f"{'=' * 70}")

        return {
            'success': True,
            'uploaded': len(uploaded_files),
            'failed': len(failed_files),
            'uploaded_files': uploaded_files,
            'failed_files': failed_files
        }

    def delete_local_files(self, file_paths: List[str]):
        """
        Delete local files after successful upload.

        Args:
            file_paths: List of file paths to delete
        """
        deleted = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted += 1
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")

        if deleted > 0:
            logger.info(f"✓ Deleted {deleted} local files after upload")

    def get_folder_url(self, folder_id: str) -> str:
        """
        Get the web URL for a folder.

        Args:
            folder_id: Folder ID

        Returns:
            Web URL of the folder
        """
        return f"https://drive.google.com/drive/folders/{folder_id}"

    def get_stats(self) -> Dict:
        """
        Get upload statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def __enter__(self):
        """Context manager entry."""
        if not self.authenticate():
            raise Exception("Failed to authenticate with Google Drive")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Print final statistics
        if self.stats['files_uploaded'] > 0:
            logger.info("\n" + "=" * 70)
            logger.info("Google Drive Upload Statistics")
            logger.info("=" * 70)
            logger.info(f"Files uploaded: {self.stats['files_uploaded']}")
            logger.info(f"Bytes uploaded: {self.stats['bytes_uploaded']:,}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info(f"Retries: {self.stats['retries']}")
            logger.info("=" * 70)
