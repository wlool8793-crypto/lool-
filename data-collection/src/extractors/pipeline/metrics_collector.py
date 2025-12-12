"""
Metrics collector for Legal RAG Extraction System (Phase 3)
Comprehensive metrics tracking and reporting
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from ..logging_config import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """
    Collects and analyzes extraction metrics.

    Metrics Categories:
    1. Performance: Duration, throughput, success rate
    2. Quality: Quality scores, validation status
    3. Extraction: Fields extracted, confidence scores
    4. Errors: Error types, failure rates
    5. Resources: Memory, CPU (optional)
    """

    def __init__(self):
        # Performance metrics
        self.durations = []
        self.throughput_records = []

        # Quality metrics
        self.quality_scores = []
        self.validation_statuses = Counter()

        # Extraction metrics
        self.fields_extracted = defaultdict(int)
        self.confidence_scores = defaultdict(list)

        # Error metrics
        self.errors = Counter()
        self.failed_extractors = Counter()

        # Document counters
        self.total_documents = 0
        self.successful_documents = 0
        self.failed_documents = 0

        # Session metadata
        self.session_start = datetime.utcnow()
        self.last_update = datetime.utcnow()

    def record_extraction(
        self,
        result: Dict[str, Any],
        duration: float
    ):
        """
        Record extraction result.

        Args:
            result: Complete extraction result
            duration: Extraction duration in seconds
        """
        self.total_documents += 1
        self.last_update = datetime.utcnow()

        # Check if successful
        status = result.get('status', 'success')

        if status == 'failed':
            self.failed_documents += 1
            error = result.get('error', 'Unknown error')
            self.errors[error] += 1
            return

        self.successful_documents += 1

        # Record duration
        self.durations.append(duration)

        # Record quality metrics
        quality_analysis = result.get('quality_analysis', {})
        if quality_analysis:
            quality_score = quality_analysis.get('overall_score', 0.0)
            validation_status = quality_analysis.get('validation_status', 'unknown')

            self.quality_scores.append(quality_score)
            self.validation_statuses[validation_status] += 1

        # Record extraction metrics
        self._record_fields(result)
        self._record_confidence_scores(result)

        # Record failed extractors
        execution_log = result.get('extraction_metadata', {}).get('execution_log', [])
        for entry in execution_log:
            if entry.get('status') == 'error':
                extractor_name = entry.get('extractor', 'Unknown')
                self.failed_extractors[extractor_name] += 1

    def _record_fields(self, result: Dict[str, Any]):
        """Record which fields were extracted."""
        if result.get('title'):
            self.fields_extracted['title'] += 1

        if result.get('citations'):
            self.fields_extracted['citations'] += 1

        parties = result.get('parties', {})
        if parties.get('petitioner'):
            self.fields_extracted['petitioner'] += 1
        if parties.get('respondent'):
            self.fields_extracted['respondent'] += 1

        if result.get('judges'):
            self.fields_extracted['judges'] += 1

        dates = result.get('dates', {})
        if dates.get('judgment_date'):
            self.fields_extracted['judgment_date'] += 1

        if result.get('sections_cited'):
            self.fields_extracted['sections_cited'] += 1

        if result.get('keywords'):
            self.fields_extracted['keywords'] += 1

        if result.get('subject_classification', {}).get('primary_subject'):
            self.fields_extracted['subject_classification'] += 1

    def _record_confidence_scores(self, result: Dict[str, Any]):
        """Record confidence scores from extractors."""
        # Citations
        citations = result.get('citations', [])
        for citation in citations:
            confidence = citation.get('confidence', 0.0)
            self.confidence_scores['citation'].append(confidence)

        # Subject classification
        subject = result.get('subject_classification', {})
        if subject.get('primary_confidence'):
            self.confidence_scores['subject'].append(
                subject['primary_confidence']
            )

        # Keywords (if they have scores)
        keywords = result.get('keywords', [])
        for keyword in keywords:
            if isinstance(keyword, dict) and 'final_score' in keyword:
                self.confidence_scores['keyword'].append(
                    keyword['final_score']
                )

    # ==================== Performance Metrics ====================

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.durations:
            return {
                'total_documents': self.total_documents,
                'successful': self.successful_documents,
                'failed': self.failed_documents,
                'success_rate': 0.0
            }

        return {
            'total_documents': self.total_documents,
            'successful': self.successful_documents,
            'failed': self.failed_documents,
            'success_rate': self.successful_documents / self.total_documents
                            if self.total_documents > 0 else 0.0,

            'duration_stats': {
                'mean': statistics.mean(self.durations),
                'median': statistics.median(self.durations),
                'min': min(self.durations),
                'max': max(self.durations),
                'total': sum(self.durations)
            },

            'throughput': {
                'documents_per_second': self.total_documents / sum(self.durations)
                                       if sum(self.durations) > 0 else 0.0,
                'avg_seconds_per_document': statistics.mean(self.durations)
                                           if self.durations else 0.0
            },

            'session_duration': (
                datetime.utcnow() - self.session_start
            ).total_seconds()
        }

    # ==================== Quality Metrics ====================

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality metrics."""
        if not self.quality_scores:
            return {
                'scores_collected': 0,
                'validation_statuses': dict(self.validation_statuses)
            }

        return {
            'scores_collected': len(self.quality_scores),

            'quality_score_stats': {
                'mean': statistics.mean(self.quality_scores),
                'median': statistics.median(self.quality_scores),
                'min': min(self.quality_scores),
                'max': max(self.quality_scores),
                'stdev': statistics.stdev(self.quality_scores)
                        if len(self.quality_scores) > 1 else 0.0
            },

            'validation_statuses': dict(self.validation_statuses),

            'quality_distribution': {
                'excellent': sum(1 for s in self.quality_scores if s >= 0.90),
                'good': sum(1 for s in self.quality_scores if 0.75 <= s < 0.90),
                'acceptable': sum(1 for s in self.quality_scores if 0.60 <= s < 0.75),
                'poor': sum(1 for s in self.quality_scores if 0.40 <= s < 0.60),
                'unacceptable': sum(1 for s in self.quality_scores if s < 0.40)
            }
        }

    # ==================== Extraction Metrics ====================

    def get_extraction_metrics(self) -> Dict[str, Any]:
        """Get extraction field metrics."""
        total = self.successful_documents if self.successful_documents > 0 else 1

        # Field extraction rates
        field_rates = {
            field: count / total
            for field, count in self.fields_extracted.items()
        }

        # Confidence score stats
        confidence_stats = {}
        for field, scores in self.confidence_scores.items():
            if scores:
                confidence_stats[field] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }

        return {
            'field_extraction_counts': dict(self.fields_extracted),
            'field_extraction_rates': field_rates,
            'confidence_scores': confidence_stats
        }

    # ==================== Error Metrics ====================

    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics."""
        total = self.total_documents if self.total_documents > 0 else 1

        return {
            'total_errors': self.failed_documents,
            'error_rate': self.failed_documents / total,

            'error_types': dict(self.errors.most_common()),

            'failed_extractors': dict(self.failed_extractors.most_common()),

            'most_common_error': self.errors.most_common(1)[0][0]
                                if self.errors else None
        }

    # ==================== Complete Report ====================

    def get_complete_report(self) -> Dict[str, Any]:
        """Get complete metrics report."""
        return {
            'performance': self.get_performance_metrics(),
            'quality': self.get_quality_metrics(),
            'extraction': self.get_extraction_metrics(),
            'errors': self.get_error_metrics(),

            'session_metadata': {
                'session_start': self.session_start.isoformat() + 'Z',
                'last_update': self.last_update.isoformat() + 'Z',
                'total_documents': self.total_documents
            }
        }

    def get_summary(self) -> str:
        """Get human-readable summary."""
        perf = self.get_performance_metrics()
        quality = self.get_quality_metrics()
        errors = self.get_error_metrics()

        summary = f"""
Extraction Metrics Summary
==========================

Performance:
- Total Documents: {self.total_documents}
- Successful: {self.successful_documents}
- Failed: {self.failed_documents}
- Success Rate: {perf.get('success_rate', 0):.1%}
"""

        if self.durations:
            duration_stats = perf['duration_stats']
            summary += f"""
- Avg Duration: {duration_stats['mean']:.2f}s
- Total Time: {duration_stats['total']:.2f}s
- Throughput: {perf['throughput']['documents_per_second']:.2f} docs/s
"""

        if self.quality_scores:
            quality_stats = quality['quality_score_stats']
            summary += f"""
Quality:
- Avg Quality Score: {quality_stats['mean']:.2%}
- Min/Max: {quality_stats['min']:.2%} / {quality_stats['max']:.2%}
- Valid: {self.validation_statuses.get('valid', 0)}
- Needs Review: {self.validation_statuses.get('needs_review', 0)}
- Invalid: {self.validation_statuses.get('invalid', 0)}
"""

        if self.failed_documents > 0:
            summary += f"""
Errors:
- Error Rate: {errors['error_rate']:.1%}
- Most Common: {errors.get('most_common_error', 'N/A')}
"""

        return summary.strip()

    # ==================== Reset ====================

    def reset(self):
        """Reset all metrics."""
        self.durations.clear()
        self.throughput_records.clear()
        self.quality_scores.clear()
        self.validation_statuses.clear()
        self.fields_extracted.clear()
        self.confidence_scores.clear()
        self.errors.clear()
        self.failed_extractors.clear()

        self.total_documents = 0
        self.successful_documents = 0
        self.failed_documents = 0

        self.session_start = datetime.utcnow()
        self.last_update = datetime.utcnow()

    # ==================== Export ====================

    def export_to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return self.get_complete_report()

    def export_to_json(self) -> str:
        """Export metrics as JSON string."""
        import json
        return json.dumps(self.export_to_dict(), indent=2)


# ==================== Global Metrics Collector ====================

_global_metrics = MetricsCollector()


def get_global_metrics() -> MetricsCollector:
    """Get global metrics collector instance."""
    return _global_metrics


def record_extraction(result: Dict[str, Any], duration: float):
    """
    Record extraction to global metrics.

    Args:
        result: Extraction result
        duration: Duration in seconds
    """
    _global_metrics.record_extraction(result, duration)


def get_metrics_report() -> Dict[str, Any]:
    """Get global metrics report."""
    return _global_metrics.get_complete_report()


def get_metrics_summary() -> str:
    """Get global metrics summary."""
    return _global_metrics.get_summary()


def reset_global_metrics():
    """Reset global metrics."""
    _global_metrics.reset()
