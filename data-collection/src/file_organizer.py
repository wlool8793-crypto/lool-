"""
File Organizer Module for Universal Legal Document System
Handles file organization, validation, and folder structure management
"""

import os
import shutil
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

try:
    from .utils import (
        calculate_file_hash,
        create_directory_if_not_exists,
        get_file_size,
        format_file_size,
        sanitize_filename
    )
except ImportError:
    # Standalone mode
    from utils import (
        calculate_file_hash,
        create_directory_if_not_exists,
        get_file_size,
        format_file_size,
        sanitize_filename
    )

logger = logging.getLogger(__name__)


class FileOrganizer:
    """
    Manages file organization for the legal document system.
    Handles folder creation, file movement, validation, and cleanup.
    """

    def __init__(self, base_path: Union[str, Path] = 'Legal_Database'):
        """
        Initialize FileOrganizer.

        Args:
            base_path: Base directory for legal documents
        """
        self.base_path = Path(base_path)
        self.temp_path = Path('data/temp_pdfs')
        self.logger = logging.getLogger(__name__)

    def create_folder_structure(self, country: str, doc_categories: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        Create complete folder structure for a country.

        Args:
            country: Country code (e.g., 'BD', 'IN', 'PK')
            doc_categories: List of document categories to create folders for

        Returns:
            Dictionary mapping category names to their Path objects

        Examples:
            >>> organizer = FileOrganizer()
            >>> folders = organizer.create_folder_structure('BD', ['CASE', 'ACT', 'RULE'])
        """
        if doc_categories is None:
            doc_categories = ['CASE', 'ACT', 'RULE', 'ORDER', 'MISC']

        country = country.upper()
        country_path = self.base_path / country

        folders = {}

        # Create main country folder
        create_directory_if_not_exists(country_path)
        folders['root'] = country_path

        # Create category folders
        for category in doc_categories:
            category_path = country_path / category
            create_directory_if_not_exists(category_path)
            folders[category] = category_path

            # Create subcategories based on category type
            if category == 'CASE':
                # Create court-level subfolders
                courts = ['SC', 'HC', 'DISTRICT', 'TRIBUNAL']
                for court in courts:
                    court_path = category_path / court
                    create_directory_if_not_exists(court_path)
                    folders[f'{category}_{court}'] = court_path

            elif category in ['ACT', 'ORDINANCE']:
                # Create jurisdiction subfolders
                jurisdictions = ['CENTRAL', 'STATE', 'PROVINCIAL']
                for jurisdiction in jurisdictions:
                    jurisdiction_path = category_path / jurisdiction
                    create_directory_if_not_exists(jurisdiction_path)
                    folders[f'{category}_{jurisdiction}'] = jurisdiction_path

                # Create time period folders
                time_periods = ['1799-1850', '1851-1900', '1901-1950', '1951-2000', '2001-2050']
                for period in time_periods:
                    period_path = category_path / period
                    create_directory_if_not_exists(period_path)
                    folders[f'{category}_{period}'] = period_path

        self.logger.info(f"Created folder structure for {country} with {len(folders)} folders")
        return folders

    def get_destination_folder(self, metadata: Dict[str, Any]) -> Path:
        """
        Determine destination folder based on document metadata.

        Args:
            metadata: Document metadata dictionary

        Returns:
            Path to destination folder

        Examples:
            >>> metadata = {'country_code': 'BD', 'doc_category': 'ACT', 'jurisdiction_level': 'CENTRAL'}
            >>> folder = organizer.get_destination_folder(metadata)
        """
        country = metadata.get('country_code', 'XX').upper()
        category = metadata.get('doc_category', 'MISC').upper()

        # Base path
        dest_path = self.base_path / country / category

        # Add subcategory based on document type
        if category == 'CASE':
            # Use court level
            court_code = metadata.get('court_code', 'MISC')
            dest_path = dest_path / court_code.upper()

        elif category in ['ACT', 'ORDINANCE']:
            # Check if we should organize by jurisdiction or time period
            jurisdiction = metadata.get('jurisdiction_level', '').upper()
            year = metadata.get('doc_year', 0)

            if jurisdiction in ['CENTRAL', 'STATE', 'PROVINCIAL']:
                dest_path = dest_path / jurisdiction
            elif year:
                # Organize by time period
                period = self._get_time_period(year)
                dest_path = dest_path / period
            else:
                dest_path = dest_path / 'MISC'

        elif category == 'RULE':
            # Organize rules by parent law or ministry
            parent_law = metadata.get('parent_law_code', '')
            if parent_law:
                dest_path = dest_path / parent_law
            else:
                ministry = metadata.get('ministry', 'MISC')
                dest_path = dest_path / ministry.upper()

        # Ensure folder exists
        create_directory_if_not_exists(dest_path)

        return dest_path

    def _get_time_period(self, year: int) -> str:
        """
        Get time period folder name for a year.

        Args:
            year: Document year

        Returns:
            Time period string (e.g., '1851-1900')
        """
        periods = [
            (1799, 1850),
            (1851, 1900),
            (1901, 1950),
            (1951, 2000),
            (2001, 2050),
            (2051, 2100)
        ]

        for start, end in periods:
            if start <= year <= end:
                return f'{start}-{end}'

        return 'OTHER'

    def move_temp_to_final(
        self,
        temp_path: Union[str, Path],
        filename: str,
        metadata: Dict[str, Any],
        validate_hash: bool = True
    ) -> Optional[Path]:
        """
        Move file from temporary to final location with validation.

        Args:
            temp_path: Path to temporary file
            filename: Final filename
            metadata: Document metadata
            validate_hash: Validate file hash after move

        Returns:
            Path to final file or None if failed

        Examples:
            >>> final_path = organizer.move_temp_to_final(
            ...     'data/temp_pdfs/temp.pdf',
            ...     'BD_ACT_CENTRAL_1860_XLV_0045_Penal_Code.pdf',
            ...     metadata
            ... )
        """
        temp_path = Path(temp_path)

        if not temp_path.exists():
            self.logger.error(f"Temporary file not found: {temp_path}")
            return None

        # Get destination folder
        dest_folder = self.get_destination_folder(metadata)

        # Add .pdf extension if not present
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # Final path
        final_path = dest_folder / filename

        try:
            # Calculate hash before move (if requested)
            original_hash = None
            if validate_hash:
                original_hash = calculate_file_hash(temp_path)

            # Move file
            shutil.move(str(temp_path), str(final_path))

            # Validate hash after move
            if validate_hash and original_hash:
                new_hash = calculate_file_hash(final_path)
                if original_hash != new_hash:
                    self.logger.error(f"Hash mismatch after move: {filename}")
                    # Restore file if possible
                    if final_path.exists():
                        final_path.unlink()
                    return None

            file_size = get_file_size(final_path)
            self.logger.info(f"Moved file to {final_path} ({format_file_size(file_size)})")

            return final_path

        except Exception as e:
            self.logger.error(f"Error moving file {temp_path} to {final_path}: {e}")
            return None

    def copy_file(
        self,
        source_path: Union[str, Path],
        dest_path: Union[str, Path],
        overwrite: bool = False
    ) -> bool:
        """
        Copy file from source to destination.

        Args:
            source_path: Source file path
            dest_path: Destination file path
            overwrite: Overwrite existing file

        Returns:
            True if successful
        """
        source_path = Path(source_path)
        dest_path = Path(dest_path)

        if not source_path.exists():
            self.logger.error(f"Source file not found: {source_path}")
            return False

        if dest_path.exists() and not overwrite:
            self.logger.warning(f"Destination exists and overwrite=False: {dest_path}")
            return False

        try:
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(str(source_path), str(dest_path))

            self.logger.info(f"Copied {source_path} to {dest_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error copying file: {e}")
            return False

    def validate_file_integrity(
        self,
        file_path: Union[str, Path],
        expected_hash: Optional[str] = None,
        expected_size: Optional[int] = None,
        min_size: int = 1024
    ) -> Dict[str, Any]:
        """
        Validate file integrity.

        Args:
            file_path: Path to file
            expected_hash: Expected SHA256 hash
            expected_size: Expected file size in bytes
            min_size: Minimum file size in bytes

        Returns:
            Dictionary with validation results

        Examples:
            >>> result = organizer.validate_file_integrity('document.pdf', expected_hash='abc123...')
            >>> if result['valid']:
            ...     print("File is valid")
        """
        file_path = Path(file_path)

        result = {
            'valid': False,
            'exists': False,
            'size': None,
            'hash': None,
            'errors': []
        }

        # Check file exists
        if not file_path.exists():
            result['errors'].append('File does not exist')
            return result

        result['exists'] = True

        # Check file size
        file_size = get_file_size(file_path)
        result['size'] = file_size

        if file_size is None:
            result['errors'].append('Could not determine file size')
            return result

        if file_size < min_size:
            result['errors'].append(f'File too small: {file_size} bytes (min: {min_size})')

        if expected_size and file_size != expected_size:
            result['errors'].append(f'Size mismatch: expected {expected_size}, got {file_size}')

        # Check hash
        file_hash = calculate_file_hash(file_path)
        result['hash'] = file_hash

        if expected_hash and file_hash != expected_hash:
            result['errors'].append('Hash mismatch')

        # Check if PDF
        if file_path.suffix.lower() == '.pdf':
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header != b'%PDF':
                        result['errors'].append('Invalid PDF header')
            except Exception as e:
                result['errors'].append(f'Could not read file: {e}')

        # Valid if no errors
        result['valid'] = len(result['errors']) == 0

        return result

    def organize_by_date(
        self,
        country: str,
        doc_category: str,
        year: int,
        month: Optional[int] = None
    ) -> Path:
        """
        Get folder path organized by date.

        Args:
            country: Country code
            doc_category: Document category
            year: Year
            month: Month (optional)

        Returns:
            Path to date-organized folder

        Examples:
            >>> folder = organizer.organize_by_date('IN', 'CASE', 2023, 5)
            >>> # Returns: Legal_Database/IN/CASE/2023/05/
        """
        country = country.upper()
        doc_category = doc_category.upper()

        # Base path
        folder_path = self.base_path / country / doc_category / str(year)

        if month:
            folder_path = folder_path / f'{month:02d}'

        # Create folder
        create_directory_if_not_exists(folder_path)

        return folder_path

    def cleanup_temp_files(
        self,
        temp_dir: Optional[Union[str, Path]] = None,
        older_than_hours: Optional[int] = None
    ) -> int:
        """
        Clean up temporary files.

        Args:
            temp_dir: Temporary directory path (default: self.temp_path)
            older_than_hours: Only delete files older than X hours

        Returns:
            Number of files deleted

        Examples:
            >>> count = organizer.cleanup_temp_files(older_than_hours=24)
            >>> print(f"Deleted {count} temporary files")
        """
        if temp_dir is None:
            temp_dir = self.temp_path

        temp_dir = Path(temp_dir)

        if not temp_dir.exists():
            return 0

        deleted_count = 0
        current_time = datetime.now().timestamp()

        try:
            for file_path in temp_dir.glob('*'):
                if not file_path.is_file():
                    continue

                # Check age if specified
                if older_than_hours:
                    file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
                    if file_age_hours < older_than_hours:
                        continue

                # Delete file
                file_path.unlink()
                deleted_count += 1

            self.logger.info(f"Cleaned up {deleted_count} temporary files from {temp_dir}")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

        return deleted_count

    def get_folder_statistics(self, folder_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get statistics for a folder.

        Args:
            folder_path: Path to folder

        Returns:
            Dictionary with folder statistics

        Examples:
            >>> stats = organizer.get_folder_statistics('Legal_Database/BD/ACT')
            >>> print(f"Total files: {stats['total_files']}")
        """
        folder_path = Path(folder_path)

        stats = {
            'total_files': 0,
            'total_size': 0,
            'pdf_count': 0,
            'largest_file': None,
            'smallest_file': None,
            'average_size': 0
        }

        if not folder_path.exists():
            return stats

        file_sizes = []

        for file_path in folder_path.rglob('*'):
            if not file_path.is_file():
                continue

            stats['total_files'] += 1

            if file_path.suffix.lower() == '.pdf':
                stats['pdf_count'] += 1

            file_size = get_file_size(file_path)
            if file_size:
                file_sizes.append(file_size)
                stats['total_size'] += file_size

                if stats['largest_file'] is None or file_size > get_file_size(stats['largest_file']):
                    stats['largest_file'] = file_path

                if stats['smallest_file'] is None or file_size < get_file_size(stats['smallest_file']):
                    stats['smallest_file'] = file_path

        if file_sizes:
            stats['average_size'] = sum(file_sizes) / len(file_sizes)

        return stats


if __name__ == '__main__':
    # Quick tests
    organizer = FileOrganizer()

    print("Testing FileOrganizer...")

    # Test folder creation
    print("\n1. Creating folder structure for Bangladesh...")
    folders = organizer.create_folder_structure('BD', ['ACT', 'CASE'])
    print(f"Created {len(folders)} folders")

    # Test destination folder determination
    print("\n2. Testing destination folder...")
    metadata = {
        'country_code': 'BD',
        'doc_category': 'ACT',
        'jurisdiction_level': 'CENTRAL',
        'doc_year': 1860
    }
    dest_folder = organizer.get_destination_folder(metadata)
    print(f"Destination: {dest_folder}")

    # Test file validation
    print("\n3. Testing file validation...")
    # (Would test with an actual file)

    print("\nAll tests completed!")
