"""
Checkpoint Manager Module
Handles automatic checkpoint creation, validation, and resume functionality
for long-running data collection processes.
"""

import logging
from typing import Optional, Dict, Tuple
from datetime import datetime
from src.database import CaseDatabase, Checkpoint, CheckpointStatus

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages checkpoint operations for resumable processes.

    Features:
    - Automatic checkpoint saving every N cases
    - Checkpoint validation and integrity checks
    - Auto-detection and resume from last checkpoint
    - Graceful handling of corrupted checkpoints
    """

    def __init__(self, db: CaseDatabase, process_name: str, checkpoint_interval: int = 100):
        """
        Initialize CheckpointManager.

        Args:
            db: CaseDatabase instance
            process_name: Name of the process (e.g., 'bulk_download')
            checkpoint_interval: Save checkpoint every N cases
        """
        self.db = db
        self.process_name = process_name
        self.checkpoint_interval = checkpoint_interval
        self.current_checkpoint = None
        self.cases_since_checkpoint = 0

        logger.info(f"CheckpointManager initialized for '{process_name}' with interval={checkpoint_interval}")

    def should_save_checkpoint(self) -> bool:
        """
        Determine if a checkpoint should be saved based on the interval.

        Returns:
            True if checkpoint should be saved
        """
        return self.cases_since_checkpoint >= self.checkpoint_interval

    def save(
        self,
        case_id: int,
        offset: int,
        pdfs_downloaded: int = 0,
        details_fetched: int = 0,
        failures: int = 0,
        metadata: Dict = None
    ) -> bool:
        """
        Save a checkpoint with current progress.

        Args:
            case_id: ID of the last processed case
            offset: Current offset in batch processing
            pdfs_downloaded: Number of PDFs downloaded so far
            details_fetched: Number of case details fetched
            failures: Number of failures encountered
            metadata: Additional metadata to store

        Returns:
            True if checkpoint saved successfully
        """
        stats = {
            'pdfs_downloaded': pdfs_downloaded,
            'details_fetched': details_fetched,
            'failures': failures,
            'metadata': metadata or {}
        }

        checkpoint_id = self.db.save_checkpoint(
            process_name=self.process_name,
            last_case_id=case_id,
            last_offset=offset,
            stats=stats
        )

        if checkpoint_id:
            self.cases_since_checkpoint = 0
            logger.info(
                f"Checkpoint saved: case_id={case_id}, offset={offset}, "
                f"pdfs={pdfs_downloaded}, details={details_fetched}, failures={failures}"
            )
            return True

        logger.error("Failed to save checkpoint")
        return False

    def increment_progress(self):
        """Increment the case counter for checkpoint interval tracking."""
        self.cases_since_checkpoint += 1

    def auto_save_if_needed(
        self,
        case_id: int,
        offset: int,
        pdfs_downloaded: int = 0,
        details_fetched: int = 0,
        failures: int = 0,
        metadata: Dict = None
    ) -> bool:
        """
        Automatically save checkpoint if interval threshold is reached.

        Args:
            case_id: ID of the last processed case
            offset: Current offset in batch processing
            pdfs_downloaded: Number of PDFs downloaded so far
            details_fetched: Number of case details fetched
            failures: Number of failures encountered
            metadata: Additional metadata to store

        Returns:
            True if checkpoint was saved (or not needed), False if save failed
        """
        self.increment_progress()

        if self.should_save_checkpoint():
            return self.save(
                case_id=case_id,
                offset=offset,
                pdfs_downloaded=pdfs_downloaded,
                details_fetched=details_fetched,
                failures=failures,
                metadata=metadata
            )

        return True  # No save needed

    def detect_last_checkpoint(self) -> Optional[Checkpoint]:
        """
        Auto-detect the last checkpoint for this process.

        Returns:
            Checkpoint object or None if no valid checkpoint found
        """
        logger.info(f"Searching for last checkpoint for process '{self.process_name}'...")

        checkpoint = self.db.get_latest_checkpoint(self.process_name)

        if not checkpoint:
            logger.info("No previous checkpoint found. Starting from beginning.")
            return None

        logger.info(
            f"Found checkpoint: ID={checkpoint.id}, "
            f"last_case_id={checkpoint.last_case_id}, "
            f"offset={checkpoint.last_offset}, "
            f"created_at={checkpoint.created_at}, "
            f"updated_at={checkpoint.updated_at}"
        )

        return checkpoint

    def validate_and_load(self) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Validate and load the last checkpoint.

        Returns:
            Tuple of (success, start_offset, checkpoint_id)
            - success: True if valid checkpoint found and validated
            - start_offset: Offset to resume from (or 0 if no checkpoint)
            - checkpoint_id: ID of the checkpoint (or None)
        """
        checkpoint = self.detect_last_checkpoint()

        if not checkpoint:
            return False, 0, None

        # Validate checkpoint integrity
        if not self.validate(checkpoint):
            logger.warning(
                f"Checkpoint {checkpoint.id} failed validation. "
                "Invalidating and starting from beginning."
            )
            self.db.invalidate_checkpoint(
                checkpoint.id,
                error_message="Failed validation check"
            )
            return False, 0, None

        logger.info(
            f"Checkpoint validated successfully. "
            f"Resuming from offset={checkpoint.last_offset}"
        )

        self.current_checkpoint = checkpoint
        return True, checkpoint.last_offset, checkpoint.id

    def validate(self, checkpoint: Checkpoint) -> bool:
        """
        Validate checkpoint integrity.

        Args:
            checkpoint: Checkpoint object to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Use database validation method
            is_valid = self.db.validate_checkpoint(checkpoint)

            if is_valid:
                logger.info(f"Checkpoint {checkpoint.id} validation: PASSED")
            else:
                logger.warning(f"Checkpoint {checkpoint.id} validation: FAILED")

            return is_valid

        except Exception as e:
            logger.error(f"Error during checkpoint validation: {e}")
            return False

    def resume_from_checkpoint(self) -> Tuple[bool, int, Dict]:
        """
        Attempt to resume from last checkpoint.

        Returns:
            Tuple of (should_resume, start_offset, checkpoint_stats)
            - should_resume: True if resuming from checkpoint
            - start_offset: Offset to start processing from
            - checkpoint_stats: Dictionary with checkpoint statistics
        """
        success, start_offset, checkpoint_id = self.validate_and_load()

        checkpoint_stats = {
            'resumed': success,
            'checkpoint_id': checkpoint_id,
            'start_offset': start_offset
        }

        if success and self.current_checkpoint:
            checkpoint_stats.update({
                'pdfs_downloaded': self.current_checkpoint.pdfs_downloaded,
                'details_fetched': self.current_checkpoint.details_fetched,
                'failures': self.current_checkpoint.failures,
                'total_processed': self.current_checkpoint.total_processed,
                'created_at': self.current_checkpoint.created_at,
                'updated_at': self.current_checkpoint.updated_at
            })

            logger.info(
                f"Resuming from checkpoint {checkpoint_id}: "
                f"processed={self.current_checkpoint.total_processed}, "
                f"pdfs={self.current_checkpoint.pdfs_downloaded}, "
                f"offset={start_offset}"
            )

        return success, start_offset, checkpoint_stats

    def complete(self) -> bool:
        """
        Mark the current checkpoint as completed.

        Returns:
            True if successful
        """
        if self.current_checkpoint:
            success = self.db.complete_checkpoint(self.current_checkpoint.id)
            if success:
                logger.info(f"Checkpoint {self.current_checkpoint.id} marked as COMPLETED")
            return success

        logger.warning("No active checkpoint to complete")
        return False

    def invalidate(self, error_message: str = None) -> bool:
        """
        Mark the current checkpoint as invalidated.

        Args:
            error_message: Optional error message

        Returns:
            True if successful
        """
        if self.current_checkpoint:
            success = self.db.invalidate_checkpoint(
                self.current_checkpoint.id,
                error_message=error_message
            )
            if success:
                logger.info(f"Checkpoint {self.current_checkpoint.id} marked as INVALIDATED")
            return success

        logger.warning("No active checkpoint to invalidate")
        return False

    def get_stats(self) -> Dict:
        """
        Get statistics about checkpoints for this process.

        Returns:
            Dictionary with checkpoint statistics
        """
        return self.db.get_checkpoint_stats(self.process_name)

    def force_save_final(
        self,
        case_id: int,
        offset: int,
        pdfs_downloaded: int = 0,
        details_fetched: int = 0,
        failures: int = 0,
        metadata: Dict = None
    ) -> bool:
        """
        Force save a final checkpoint (ignores interval).

        Useful for saving progress when process is interrupted or completed.

        Args:
            case_id: ID of the last processed case
            offset: Current offset in batch processing
            pdfs_downloaded: Number of PDFs downloaded
            details_fetched: Number of case details fetched
            failures: Number of failures encountered
            metadata: Additional metadata to store

        Returns:
            True if checkpoint saved successfully
        """
        logger.info("Force saving final checkpoint...")
        return self.save(
            case_id=case_id,
            offset=offset,
            pdfs_downloaded=pdfs_downloaded,
            details_fetched=details_fetched,
            failures=failures,
            metadata=metadata
        )
