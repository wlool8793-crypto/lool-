"""
Shared state definitions for schema evolution system
"""

from typing import Dict, List, TypedDict, Optional, Annotated
from typing_extensions import TypedDict
import operator


class SchemaDefinition(TypedDict):
    """Schema definition structure"""
    version: str
    iteration: int
    nodes: List[Dict]
    relationships: List[Dict]
    indexes: List[Dict]
    constraints: List[Dict]
    rag_configuration: Dict
    changes_from_previous: List[str]
    design_rationale: Dict


class DimensionScore(TypedDict):
    """Score for a single evaluation dimension"""
    score: float
    max_score: float
    details: Dict
    missing_components: List[str]
    strengths: List[str]


class ImprovementSuggestion(TypedDict):
    """Suggestion for improving schema"""
    priority: str  # HIGH, MEDIUM, LOW
    dimension: str
    issue: str
    impact: str
    suggestion: str


class EvaluationResult(TypedDict):
    """Complete evaluation results"""
    evaluation_id: str
    schema_version: str
    timestamp: str
    overall_score: float
    dimension_scores: Dict[str, DimensionScore]
    critical_improvements: List[ImprovementSuggestion]
    strengths: List[str]
    ready_for_production: bool
    production_blockers: List[str]


class ImplementationChange(TypedDict):
    """Record of an implementation change"""
    change_id: str
    type: str  # add_property, create_index, new_node_type, etc.
    description: str
    cypher: str
    status: str  # success, failed
    execution_time_ms: int


class ImplementationReport(TypedDict):
    """Report from schema implementer"""
    implementation_id: str
    source_version: str
    target_version: str
    timestamp: str
    changes_applied: List[ImplementationChange]
    validation_results: Dict
    rollback_available: bool


class IterationRecord(TypedDict):
    """Record of a single iteration"""
    iteration: int
    schema_version: str
    overall_score: float
    dimension_scores: Dict[str, float]
    improvements_made: int
    duration_seconds: float


class SchemaEvolutionState(TypedDict):
    """Main state for the evolution system"""
    # Current iteration number
    current_iteration: int

    # Current schema being evolved
    current_schema: Optional[SchemaDefinition]

    # Latest evaluation results
    evaluation_results: Optional[EvaluationResult]

    # Latest implementation report
    implementation_report: Optional[ImplementationReport]

    # History of all iterations
    iteration_history: Annotated[List[IterationRecord], operator.add]

    # Convergence tracking
    convergence_achieved: bool
    target_score: float
    max_iterations: int

    # Messages for agent communication
    messages: Annotated[List[Dict], operator.add]


def create_initial_state(target_score: float = 9.0, max_iterations: int = 7) -> SchemaEvolutionState:
    """Create initial state for schema evolution"""
    return SchemaEvolutionState(
        current_iteration=0,
        current_schema=None,
        evaluation_results=None,
        implementation_report=None,
        iteration_history=[],
        convergence_achieved=False,
        target_score=target_score,
        max_iterations=max_iterations,
        messages=[]
    )
