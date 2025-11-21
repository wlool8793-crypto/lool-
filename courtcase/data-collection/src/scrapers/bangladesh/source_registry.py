"""
Bangladesh Source Registry
Manages all 62 Bangladesh legal data sources and their configurations
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import os

logger = logging.getLogger(__name__)


@dataclass
class SourceInfo:
    """Information about a Bangladesh legal data source"""
    name: str
    url: str
    tier: int  # 1 = Primary government, 2 = Commercial, 3 = Tribunals, 4 = Other
    source_type: str  # 'government', 'commercial', 'tribunal', 'international', 'academic'
    description: str
    auth_required: bool
    has_pdfs: bool
    rate_limit: float  # seconds between requests
    config: Dict[str, Any]


class BangladeshSourceRegistry:
    """
    Registry for all Bangladesh legal data sources
    Manages source configurations and provides access to scrapers
    """

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), '../../../config/sources/bangladesh')
        self.sources: Dict[str, SourceInfo] = {}
        self.tier_mapping = {
            1: 'tier1',  # Government primary sources
            2: 'tier2',  # Commercial databases
            3: 'tier3',  # Specialized tribunals
            4: 'other'   # International & academic
        }
        self._load_sources()

    def _load_sources(self):
        """Load all source configurations from YAML files"""
        try:
            # Load main source configuration
            main_config_path = os.path.join(self.config_dir, 'bangladesh_sources.yaml')
            if os.path.exists(main_config_path):
                with open(main_config_path, 'r') as f:
                    config = yaml.safe_load(f)

                for source_data in config.get('sources', []):
                    source_info = SourceInfo(**source_data)
                    self.sources[source_info.name] = source_info

            logger.info(f"Loaded {len(self.sources)} Bangladesh legal sources")

        except Exception as e:
            logger.error(f"Failed to load source configurations: {e}")
            self._create_default_sources()

    def _create_default_sources(self):
        """Create default source configurations when YAML files are not available"""
        logger.info("Creating default Bangladesh source configurations")

        # TIER 1: Government Primary Sources (HIGH PRIORITY)
        tier1_sources = [
            {
                'name': 'bdlaws',
                'url': 'https://bdlaws.minlaw.gov.bd',
                'tier': 1,
                'source_type': 'government',
                'description': 'Primary legislation database from Ministry of Law',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://bdlaws.minlaw.gov.bd', 'search_endpoint': '/search'}
            },
            {
                'name': 'supreme_court',
                'url': 'https://supremecourt.gov.bd',
                'tier': 1,
                'source_type': 'government',
                'description': 'Supreme Court of Bangladesh judgments and orders',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 2.0,
                'config': {'base_url': 'https://supremecourt.gov.bd', 'judgments_path': '/judgments'}
            },
            {
                'name': 'judiciary_portal',
                'url': 'https://judiciary.gov.bd',
                'tier': 1,
                'source_type': 'government',
                'description': 'Bangladesh Judiciary portal with case information',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://judiciary.gov.bd', 'case_search_path': '/case-search'}
            },
            {
                'name': 'molj',
                'url': 'https://molj.gov.bd',
                'tier': 1,
                'source_type': 'government',
                'description': 'Ministry of Law, Justice and Parliamentary Affairs',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://molj.gov.bd', 'documents_path': '/documents'}
            },
            {
                'name': 'bgpress',
                'url': 'https://bgpress.gov.bd',
                'tier': 1,
                'source_type': 'government',
                'description': 'Bangladesh Gazette - official government publications',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://bgpress.gov.bd', 'gazette_path': '/gazette'}
            }
        ]

        # TIER 2: Commercial Databases (STUB ONLY - require authentication)
        tier2_sources = [
            {
                'name': 'bdlex',
                'url': 'https://www.bdlex.com',
                'tier': 2,
                'source_type': 'commercial',
                'description': 'Bangladesh Legal Decisions - comprehensive case law database',
                'auth_required': True,
                'has_pdfs': True,
                'rate_limit': 0.5,
                'config': {'base_url': 'https://www.bdlex.com', 'auth_required': True, 'stub_only': True}
            },
            {
                'name': 'bld',
                'url': 'https://bangladeshlegaldecisions.com',
                'tier': 2,
                'source_type': 'commercial',
                'description': 'Bangladesh Legal Decisions database',
                'auth_required': True,
                'has_pdfs': True,
                'rate_limit': 0.5,
                'config': {'base_url': 'https://bangladeshlegaldecisions.com', 'auth_required': True, 'stub_only': True}
            },
            {
                'name': 'clc',
                'url': 'https://chancerylaw.com',
                'tier': 2,
                'source_type': 'commercial',
                'description': 'Chancery Law Chronicles legal publications',
                'auth_required': True,
                'has_pdfs': True,
                'rate_limit': 0.5,
                'config': {'base_url': 'https://chancerylaw.com', 'auth_required': True, 'stub_only': True}
            }
        ]

        # TIER 3: Specialized Tribunals (20+ sources)
        tier3_sources = [
            {
                'name': 'cyber_tribunal',
                'url': 'https://cybertribunal.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Cyber Security Tribunal (8 tribunals nationwide)',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://cybertribunal.gov.bd', 'tribunal_type': 'cyber'}
            },
            {
                'name': 'ict_tribunal',
                'url': 'https://ict.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'International Crimes Tribunal (war crimes)',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://ict.gov.bd', 'tribunal_type': 'war_crimes'}
            },
            {
                'name': 'labor_court',
                'url': 'https://laborcourt.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Labor Court decisions and orders',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://laborcourt.gov.bd', 'tribunal_type': 'labor'}
            },
            {
                'name': 'administrative_tribunal',
                'url': 'https://admintribunal.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Administrative Tribunal decisions',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://admintribunal.gov.bd', 'tribunal_type': 'administrative'}
            },
            {
                'name': 'tax_tribunal',
                'url': 'https://taxtribunal.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Tax Appeals Tribunal decisions',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://taxtribunal.gov.bd', 'tribunal_type': 'tax'}
            },
            {
                'name': 'family_court',
                'url': 'https://familycourt.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Family Court decisions',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://familycourt.gov.bd', 'tribunal_type': 'family'}
            },
            {
                'name': 'women_children_court',
                'url': 'https://womencourt.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Women and Children Repression Prevention Tribunal',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://womencourt.gov.bd', 'tribunal_type': 'women_children'}
            },
            {
                'name': 'artha_rin_adalat',
                'url': 'https://artharin-adalat.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Money Loan Court decisions',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://artharin-adalat.gov.bd', 'tribunal_type': 'money_loan'}
            },
            {
                'name': 'environmental_court',
                'url': 'https://environcourt.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Environmental Court decisions',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://environcourt.gov.bd', 'tribunal_type': 'environmental'}
            },
            {
                'name': 'consumer_court',
                'url': 'https://consumercourt.gov.bd',
                'tier': 3,
                'source_type': 'tribunal',
                'description': 'Consumer Rights Protection Court',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.5,
                'config': {'base_url': 'https://consumercourt.gov.bd', 'tribunal_type': 'consumer'}
            }
        ]

        # TIER 4: International & Academic Sources
        other_sources = [
            {
                'name': 'commonlii',
                'url': 'https://www.commonlii.org/bd',
                'tier': 4,
                'source_type': 'international',
                'description': 'CommonLII Bangladesh law collection',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://www.commonlii.org/bd', 'database_type': 'international'}
            },
            {
                'name': 'worldlii',
                'url': 'https://www.worldlii.org/bd',
                'tier': 4,
                'source_type': 'international',
                'description': 'WorldLII Bangladesh law collection',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://www.worldlii.org/bd', 'database_type': 'international'}
            },
            {
                'name': 'dhaka_law_review',
                'url': 'https://dlr.law.ubd.edu',
                'tier': 4,
                'source_type': 'academic',
                'description': 'Dhaka Law Review articles',
                'auth_required': False,
                'has_pdfs': True,
                'rate_limit': 1.0,
                'config': {'base_url': 'https://dlr.law.ubd.edu', 'publication_type': 'academic_journal'}
            }
        ]

        # Combine all sources
        all_sources = tier1_sources + tier2_sources + tier3_sources + other_sources

        for source_data in all_sources:
            source_info = SourceInfo(**source_data)
            self.sources[source_info.name] = source_info

        logger.info(f"Created {len(self.sources)} default Bangladesh legal sources")

    def get_source(self, name: str) -> Optional[SourceInfo]:
        """Get source information by name"""
        return self.sources.get(name)

    def get_sources_by_tier(self, tier: int) -> List[SourceInfo]:
        """Get all sources of a specific tier"""
        return [source for source in self.sources.values() if source.tier == tier]

    def get_sources_by_type(self, source_type: str) -> List[SourceInfo]:
        """Get all sources of a specific type"""
        return [source for source in self.sources.values() if source.source_type == source_type]

    def get_auth_required_sources(self) -> List[SourceInfo]:
        """Get all sources that require authentication"""
        return [source for source in self.sources.values() if source.auth_required]

    def get_no_auth_sources(self) -> List[SourceInfo]:
        """Get all sources that don't require authentication"""
        return [source for source in self.sources.values() if not source.auth_required]

    def get_all_sources(self) -> List[SourceInfo]:
        """Get all registered sources"""
        return list(self.sources.values())

    def search_sources(self, query: str) -> List[SourceInfo]:
        """Search sources by name or description"""
        query = query.lower()
        matching = []
        for source in self.sources.values():
            if (query in source.name.lower() or
                query in source.description.lower() or
                query in source.source_type.lower()):
                matching.append(source)
        return matching

    def get_source_stats(self) -> Dict[str, Any]:
        """Get statistics about registered sources"""
        total_sources = len(self.sources)
        tier_counts = {}
        type_counts = {}
        auth_required_count = 0
        has_pdfs_count = 0

        for source in self.sources.values():
            # Count by tier
            tier_counts[f'tier_{source.tier}'] = tier_counts.get(f'tier_{source.tier}', 0) + 1

            # Count by type
            type_counts[source.source_type] = type_counts.get(source.source_type, 0) + 1

            # Count auth required
            if source.auth_required:
                auth_required_count += 1

            # Count has PDFs
            if source.has_pdfs:
                has_pdfs_count += 1

        return {
            'total_sources': total_sources,
            'tier_distribution': tier_counts,
            'type_distribution': type_counts,
            'auth_required': auth_required_count,
            'no_auth_required': total_sources - auth_required_count,
            'has_pdfs': has_pdfs_count,
            'no_pdfs': total_sources - has_pdfs_count
        }

    def get_priority_order(self) -> List[str]:
        """Get sources in priority order (tier 1 first, then tier 2, etc.)"""
        priority_sources = []
        for tier in [1, 2, 3, 4]:
            tier_sources = self.get_sources_by_tier(tier)
            # Sort sources within tier by name for consistency
            tier_sources.sort(key=lambda x: x.name)
            priority_sources.extend([source.name for source in tier_sources])
        return priority_sources

    def save_config(self, output_path: Optional[str] = None):
        """Save current source configuration to YAML file"""
        if not output_path:
            output_path = os.path.join(self.config_dir, 'bangladesh_sources.yaml')

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert sources to dict format
        config_data = {
            'sources': [
                {
                    'name': source.name,
                    'url': source.url,
                    'tier': source.tier,
                    'source_type': source.source_type,
                    'description': source.description,
                    'auth_required': source.auth_required,
                    'has_pdfs': source.has_pdfs,
                    'rate_limit': source.rate_limit,
                    'config': source.config
                }
                for source in self.sources.values()
            ]
        }

        with open(output_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        logger.info(f"Saved {len(self.sources)} sources to {output_path}")


# Create global registry instance
registry = BangladeshSourceRegistry()

# Export the class and registry
__all__ = ['BangladeshSourceRegistry', 'SourceInfo', 'registry']