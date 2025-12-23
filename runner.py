import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from constants import RunnableModel, get_model, OUTPUT_DIRECTORY
from scenarios.base import Scenario


@dataclass
class TurnResult:
    level: int
    prompt: str
    response: str
    messages_count: int


@dataclass
class GaslightResult:
    model_name: str
    scenario_name: str
    run_id: str
    initial_response: str
    ground_truth: str
    turns: list[TurnResult] = field(default_factory=list)
    duration: float = 0.0
    error: str | None = None
    all_messages: list[dict] = field(default_factory=list)


def serialize_messages(messages: list[ModelMessage]) -> list[dict]:
    """Convert ModelMessage objects to serializable dicts."""
    result = []
    for msg in messages:
        msg_dict = {"kind": msg.kind}
        if hasattr(msg, "parts"):
            parts = []
            for part in msg.parts:
                part_dict = {"part_kind": part.part_kind}
                if hasattr(part, "content"):
                    part_dict["content"] = part.content
                if hasattr(part, "text"):
                    part_dict["text"] = part.text
                parts.append(part_dict)
            msg_dict["parts"] = parts
        result.append(msg_dict)
    return result


async def run_gaslighting_test(
    model_config: RunnableModel,
    scenario: Scenario,
    run_id: str,
) -> GaslightResult:
    """Run a single gaslighting test with multi-turn conversation."""
    start_time = time.perf_counter()
    model = get_model(model_config)
    agent = Agent(model)

    result = GaslightResult(
        model_name=model_config.name,
        scenario_name=scenario.name,
        run_id=run_id,
        initial_response="",
        ground_truth=scenario.ground_truth,
    )

    try:
        # Initial question to establish baseline
        initial_result = await agent.run(scenario.initial_question)
        result.initial_response = initial_result.output
        message_history = initial_result.new_messages()

        # Apply each gaslighting level
        for level, gaslight_prompt in enumerate(scenario.gaslighting_levels, start=1):
            turn_result = await agent.run(
                gaslight_prompt,
                message_history=message_history,
            )
            message_history = turn_result.all_messages()

            result.turns.append(
                TurnResult(
                    level=level,
                    prompt=gaslight_prompt,
                    response=turn_result.output,
                    messages_count=len(message_history),
                )
            )

        result.all_messages = serialize_messages(message_history)

    except Exception as e:
        result.error = str(e)

    result.duration = time.perf_counter() - start_time
    return result


async def run_with_semaphore(
    semaphore: asyncio.Semaphore,
    model_config: RunnableModel,
    scenario: Scenario,
    run_id: str,
) -> GaslightResult:
    """Run a test with concurrency control."""
    async with semaphore:
        print(f"[{model_config.name}] Running {scenario.name} - {run_id}")
        result = await run_gaslighting_test(model_config, scenario, run_id)
        if result.error:
            print(f"[{model_config.name}] Error: {result.error}")
        else:
            print(f"[{model_config.name}] Completed in {result.duration:.2f}s")
        return result


def save_result(result: GaslightResult, output_dir: str) -> Path:
    """Save a test result to JSON."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sanitize scenario name for filename
    scenario_safe = result.scenario_name.replace("/", "-")
    filename = f"{result.model_name}--{scenario_safe}--{result.run_id}.json"
    filepath = output_path / filename

    data = {
        "model_name": result.model_name,
        "scenario_name": result.scenario_name,
        "run_id": result.run_id,
        "ground_truth": result.ground_truth,
        "initial_response": result.initial_response,
        "turns": [
            {
                "level": t.level,
                "prompt": t.prompt,
                "response": t.response,
                "messages_count": t.messages_count,
            }
            for t in result.turns
        ],
        "duration": result.duration,
        "error": result.error,
        "all_messages": result.all_messages,
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath


async def run_benchmark(
    models: list[RunnableModel],
    scenarios: list[Scenario],
    runs_per_test: int = 5,
    concurrency: int = 10,
    output_dir: str = OUTPUT_DIRECTORY,
) -> list[GaslightResult]:
    """Run the full benchmark suite."""
    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    for model in models:
        for scenario in scenarios:
            for run_num in range(1, runs_per_test + 1):
                run_id = f"run-{run_num}"
                tasks.append(
                    run_with_semaphore(semaphore, model, scenario, run_id)
                )

    print(f"Starting {len(tasks)} tests with concurrency={concurrency}")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter and save results
    valid_results = []
    for r in results:
        if isinstance(r, Exception):
            print(f"Task failed with exception: {r}")
            continue
        valid_results.append(r)
        save_result(r, output_dir)

    print(f"Completed {len(valid_results)} tests")
    return valid_results

