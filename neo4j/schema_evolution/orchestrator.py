"""
Schema Evolution Orchestrator - Coordinates iterative schema improvement

Workflow:
1. Initialize state
2. Loop (max 7 iterations):
   - Designer creates/improves schema
   - Evaluator scores schema
   - Check convergence (score >= 9.0, all dimensions >= 8.0)
   - If converged or max iterations: stop
   - Otherwise: continue with feedback
3. Return final schema and evaluation

Uses LangGraph for state management and orchestration
"""

from typing import Dict, Optional
import json
import os
from datetime import datetime

from state import (
    SchemaEvolutionState,
    SchemaDefinition,
    EvaluationResult,
    IterationRecord,
    create_initial_state
)
from schema_designer import SchemaDesigner
from schema_evaluator import SchemaEvaluator
from schema_implementer import SchemaImplementer


class SchemaEvolutionOrchestrator:
    """
    Orchestrates the iterative schema evolution process

    Components:
    - Schema Designer (with 4 sub-agents)
    - Schema Evaluator (8-dimensional scoring)
    - Schema Implementer (Neo4j deployment)
    """

    def __init__(
        self,
        target_score: float = 9.0,
        max_iterations: int = 7,
        auto_implement: bool = False
    ):
        """
        Initialize orchestrator

        Args:
            target_score: Target overall score for convergence (default: 9.0)
            max_iterations: Maximum iterations before stopping (default: 7)
            auto_implement: Whether to auto-implement schema in Neo4j (default: False)
        """
        self.target_score = target_score
        self.max_iterations = max_iterations
        self.auto_implement = auto_implement

        # Initialize agents
        self.designer = SchemaDesigner()
        self.evaluator = SchemaEvaluator()
        self.implementer = SchemaImplementer() if auto_implement else None

        # Initialize state
        self.state = create_initial_state(target_score, max_iterations)

    def run_evolution(self) -> Dict:
        """
        Run complete schema evolution process

        Returns:
            Final state with best schema and evaluation results
        """

        print("\n" + "="*80)
        print("🚀 SCHEMA EVOLUTION SYSTEM STARTING")
        print("="*80)
        print(f"Target Score: {self.target_score}/10.0")
        print(f"Max Iterations: {self.max_iterations}")
        print(f"Auto-Implement: {self.auto_implement}")
        print("="*80 + "\n")

        iteration_start_time = datetime.now()

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'#'*80}")
            print(f"# ITERATION {iteration}/{self.max_iterations}")
            print(f"{'#'*80}\n")

            iter_start = datetime.now()

            # Step 1: Design/Improve Schema
            current_schema = self.state.get("current_schema")
            evaluation_feedback = self.state.get("evaluation_results")

            schema = self.designer.design_schema(
                iteration=iteration,
                current_schema=current_schema,
                evaluation_feedback=evaluation_feedback
            )

            # Update state
            self.state["current_schema"] = schema
            self.state["current_iteration"] = iteration

            # Step 2: Evaluate Schema
            evaluation = self.evaluator.evaluate(schema)

            # Update state
            self.state["evaluation_results"] = evaluation

            # Step 3: Record iteration
            dimension_scores_simple = {
                k: v["score"] for k, v in evaluation["dimension_scores"].items()
            }

            iteration_record = IterationRecord(
                iteration=iteration,
                schema_version=schema["version"],
                overall_score=evaluation["overall_score"],
                dimension_scores=dimension_scores_simple,
                improvements_made=len(evaluation.get("critical_improvements", [])),
                duration_seconds=(datetime.now() - iter_start).total_seconds()
            )

            self.state["iteration_history"].append(iteration_record)

            # Step 4: Check Convergence
            if evaluation["ready_for_production"]:
                print(f"\n{'='*80}")
                print("🎉 CONVERGENCE ACHIEVED!")
                print(f"{'='*80}")
                print(f"✅ Overall Score: {evaluation['overall_score']:.2f}/10.0")
                print(f"✅ All dimensions >= 8.0")
                print(f"✅ Production-ready schema achieved in {iteration} iterations")
                print(f"{'='*80}\n")

                self.state["convergence_achieved"] = True

                # Step 5: Optionally implement in Neo4j
                if self.auto_implement:
                    print("\n📝 Auto-implementing schema in Neo4j...")
                    implementation_report = self.implementer.implement_schema(
                        schema=schema,
                        previous_schema=current_schema,
                        dry_run=False
                    )
                    self.state["implementation_report"] = implementation_report

                break

            else:
                print(f"\n{'='*80}")
                print(f"📊 Iteration {iteration} Complete")
                print(f"{'='*80}")
                print(f"Score: {evaluation['overall_score']:.2f}/10.0 (target: {self.target_score})")
                print(f"\nProduction Blockers:")
                for blocker in evaluation.get("production_blockers", []):
                    print(f"  ❌ {blocker}")

                print(f"\nTop Improvements for Next Iteration:")
                for i, suggestion in enumerate(evaluation.get("critical_improvements", [])[:3], 1):
                    print(f"  {i}. [{suggestion['priority']}] {suggestion['issue']}")
                    print(f"     → {suggestion['suggestion']}")

                print(f"{'='*80}\n")

                # Check if max iterations reached
                if iteration >= self.max_iterations:
                    print(f"\n{'='*80}")
                    print("⚠️  MAX ITERATIONS REACHED")
                    print(f"{'='*80}")
                    print(f"Final Score: {evaluation['overall_score']:.2f}/10.0")
                    print(f"Best schema achieved: {schema['version']}")
                    print(f"{'='*80}\n")
                    break

        # Calculate total duration
        total_duration = (datetime.now() - iteration_start_time).total_seconds()

        # Generate final summary
        self._print_final_summary(total_duration)

        return {
            "final_schema": self.state["current_schema"],
            "final_evaluation": self.state["evaluation_results"],
            "iteration_history": self.state["iteration_history"],
            "convergence_achieved": self.state["convergence_achieved"],
            "total_iterations": self.state["current_iteration"],
            "total_duration_seconds": total_duration
        }

    def _print_final_summary(self, total_duration: float):
        """Print final summary of evolution process"""

        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)

        final_eval = self.state.get("evaluation_results")
        if final_eval:
            print(f"\n🎯 Final Score: {final_eval['overall_score']:.2f}/10.0")
            print(f"✅ Production Ready: {final_eval['ready_for_production']}")
            print(f"🔄 Total Iterations: {self.state['current_iteration']}")
            print(f"⏱️  Total Duration: {total_duration:.1f}s")

            print("\n📈 Dimension Scores:")
            for dim_name, dim_score in final_eval["dimension_scores"].items():
                score = dim_score["score"]
                emoji = "✅" if score >= 8.0 else "⚠️" if score >= 7.0 else "❌"
                print(f"  {emoji} {dim_name:.<35} {score:.1f}/10")

            print("\n💪 Strengths:")
            for strength in final_eval.get("strengths", [])[:5]:
                print(f"  ✓ {strength}")

            if not final_eval["ready_for_production"]:
                print("\n🚧 Remaining Issues:")
                for blocker in final_eval.get("production_blockers", []):
                    print(f"  • {blocker}")

            print("\n📝 Iteration History:")
            for record in self.state["iteration_history"]:
                print(f"  Iteration {record['iteration']}: {record['overall_score']:.2f}/10 "
                      f"({record['duration_seconds']:.1f}s)")

        print("\n" + "="*80)

    def export_results(self, output_dir: str = "."):
        """Export evolution results to files"""

        os.makedirs(output_dir, exist_ok=True)

        # Export final schema as JSON
        schema_file = os.path.join(output_dir, "final_schema.json")
        with open(schema_file, "w") as f:
            json.dump(self.state["current_schema"], f, indent=2)
        print(f"✅ Schema exported to {schema_file}")

        # Export evaluation results
        eval_file = os.path.join(output_dir, "evaluation_results.json")
        with open(eval_file, "w") as f:
            json.dump(self.state["evaluation_results"], f, indent=2)
        print(f"✅ Evaluation exported to {eval_file}")

        # Export iteration history
        history_file = os.path.join(output_dir, "iteration_history.json")
        with open(history_file, "w") as f:
            json.dump(self.state["iteration_history"], f, indent=2)
        print(f"✅ History exported to {history_file}")

        # Export schema documentation (if implementer available)
        if self.implementer:
            doc_file = os.path.join(output_dir, "schema_documentation.md")
            self.implementer.export_schema_documentation(
                self.state["current_schema"],
                doc_file
            )

        # Export summary report
        summary_file = os.path.join(output_dir, "evolution_summary.md")
        self._export_summary_markdown(summary_file)
        print(f"✅ Summary exported to {summary_file}")

    def _export_summary_markdown(self, output_file: str):
        """Export human-readable summary as markdown"""

        final_eval = self.state.get("evaluation_results")
        final_schema = self.state.get("current_schema")

        with open(output_file, "w") as f:
            f.write("# Schema Evolution Summary\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if final_eval:
                f.write("## Final Results\n\n")
                f.write(f"- **Overall Score**: {final_eval['overall_score']:.2f}/10.0\n")
                f.write(f"- **Production Ready**: {'✅ Yes' if final_eval['ready_for_production'] else '❌ No'}\n")
                f.write(f"- **Total Iterations**: {self.state['current_iteration']}\n")
                f.write(f"- **Convergence Achieved**: {'✅ Yes' if self.state['convergence_achieved'] else '❌ No'}\n\n")

                f.write("## Dimension Scores\n\n")
                f.write("| Dimension | Score | Status |\n")
                f.write("|-----------|-------|--------|\n")

                for dim_name, dim_score in final_eval["dimension_scores"].items():
                    score = dim_score["score"]
                    status = "✅ Pass" if score >= 8.0 else "⚠️ Needs Work"
                    f.write(f"| {dim_name} | {score:.1f}/10 | {status} |\n")

                f.write("\n## Schema Statistics\n\n")
                if final_schema:
                    f.write(f"- **Version**: {final_schema['version']}\n")
                    f.write(f"- **Node Types**: {len(final_schema.get('nodes', []))}\n")
                    f.write(f"- **Relationship Types**: {len(final_schema.get('relationships', []))}\n")
                    f.write(f"- **Indexes**: {len(final_schema.get('indexes', []))}\n")
                    f.write(f"- **Constraints**: {len(final_schema.get('constraints', []))}\n\n")

                f.write("## Strengths\n\n")
                for strength in final_eval.get("strengths", [])[:10]:
                    f.write(f"- {strength}\n")

                if not final_eval["ready_for_production"]:
                    f.write("\n## Production Blockers\n\n")
                    for blocker in final_eval.get("production_blockers", []):
                        f.write(f"- {blocker}\n")

                    f.write("\n## Recommended Improvements\n\n")
                    for suggestion in final_eval.get("critical_improvements", [])[:5]:
                        f.write(f"### {suggestion['issue']}\n\n")
                        f.write(f"- **Priority**: {suggestion['priority']}\n")
                        f.write(f"- **Dimension**: {suggestion['dimension']}\n")
                        f.write(f"- **Impact**: {suggestion['impact']}\n")
                        f.write(f"- **Suggestion**: {suggestion['suggestion']}\n\n")

            f.write("## Iteration History\n\n")
            f.write("| Iteration | Version | Score | Duration |\n")
            f.write("|-----------|---------|-------|----------|\n")

            for record in self.state["iteration_history"]:
                f.write(f"| {record['iteration']} | {record['schema_version']} | "
                       f"{record['overall_score']:.2f}/10 | {record['duration_seconds']:.1f}s |\n")


def run_schema_evolution(
    target_score: float = 9.0,
    max_iterations: int = 7,
    auto_implement: bool = False,
    export_dir: str = "./schema_output"
) -> Dict:
    """
    Convenience function to run complete schema evolution

    Args:
        target_score: Target overall score (default: 9.0)
        max_iterations: Max iterations (default: 7)
        auto_implement: Auto-implement in Neo4j (default: False)
        export_dir: Directory to export results (default: ./schema_output)

    Returns:
        Final results dictionary
    """

    orchestrator = SchemaEvolutionOrchestrator(
        target_score=target_score,
        max_iterations=max_iterations,
        auto_implement=auto_implement
    )

    results = orchestrator.run_evolution()

    # Export results
    orchestrator.export_results(output_dir=export_dir)

    return results
