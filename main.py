import argparse
import asyncio
from dotenv import load_dotenv


from constants import (
    MODELS_TO_RUN,
    MAX_CONCURRENCY,
    TEST_RUNS_PER_MODEL,
    OUTPUT_DIRECTORY,
    get_model_by_name,
)
from runner import run_benchmark
from scenarios import get_all_scenarios, get_scenario_by_name, get_scenarios_by_category

load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GaslightBench - Test LLM resistance to gaslighting"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        help="Specific model name to run (e.g., 'claude-4-sonnet')",
    )
    parser.add_argument(
        "--scenario",
        "-s",
        type=str,
        help="Specific scenario to run (e.g., 'factual/basic_math')",
    )
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        help="Run all scenarios in a category (e.g., 'factual')",
    )
    parser.add_argument(
        "--runs",
        "-n",
        type=int,
        default=TEST_RUNS_PER_MODEL,
        help=f"Number of runs per model/scenario (default: {TEST_RUNS_PER_MODEL})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=MAX_CONCURRENCY,
        help=f"Max concurrent API calls (default: {MAX_CONCURRENCY})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIRECTORY,
        help=f"Output directory for results (default: {OUTPUT_DIRECTORY})",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Only run models marked with test_mode=True",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Quick test: 1 run, limited concurrency, test models only",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available scenarios and exit",
    )
    return parser.parse_args()


def list_models() -> None:
    print("Available models:")
    for model in MODELS_TO_RUN:
        flags = []
        if model.test_mode:
            flags.append("test")
        if model.reasoning:
            flags.append("reasoning")
        flags_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  - {model.name}{flags_str}")


def list_scenarios() -> None:
    print("Available scenarios:")
    for scenario in get_all_scenarios():
        print(f"  - {scenario.name} ({scenario.category})")
        print(f"      {scenario.description}")


async def main() -> None:
    args = parse_args()

    if args.list_models:
        list_models()
        return

    if args.list_scenarios:
        list_scenarios()
        return

    # Determine which models to run
    if args.model:
        model_config = get_model_by_name(args.model)
        if not model_config:
            print(f"Error: Model '{args.model}' not found")
            list_models()
            return
        models = [model_config]
    elif args.test_mode or args.dry_run:
        models = [m for m in MODELS_TO_RUN if m.test_mode]
        if not models:
            print("No test_mode models found")
            return
    else:
        models = MODELS_TO_RUN

    # Determine which scenarios to run
    if args.scenario:
        scenario = get_scenario_by_name(args.scenario)
        if not scenario:
            print(f"Error: Scenario '{args.scenario}' not found")
            list_scenarios()
            return
        scenarios = [scenario]
    elif args.category:
        scenarios = get_scenarios_by_category(args.category)
        if not scenarios:
            print(f"Error: No scenarios in category '{args.category}'")
            return
    else:
        scenarios = get_all_scenarios()

    # Apply dry-run settings
    runs = args.runs
    concurrency = args.concurrency
    output_dir = args.output_dir

    if args.dry_run:
        runs = 1
        concurrency = min(5, concurrency)
        output_dir = "./results/dry-run"
        print("=== DRY RUN MODE ===")

    print(f"Models: {[m.name for m in models]}")
    print(f"Scenarios: {[s.name for s in scenarios]}")
    print(f"Runs per test: {runs}")
    print(f"Concurrency: {concurrency}")
    print(f"Output: {output_dir}")
    print()

    results = await run_benchmark(
        models=models,
        scenarios=scenarios,
        runs_per_test=runs,
        concurrency=concurrency,
        output_dir=output_dir,
    )

    # Print summary
    print("\n=== SUMMARY ===")
    error_count = sum(1 for r in results if r.error)
    success_count = len(results) - error_count
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")

    if results:
        avg_duration = sum(r.duration for r in results) / len(results)
        print(f"Average duration: {avg_duration:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
