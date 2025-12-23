import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from constants import RunnableModel, get_model, OUTPUT_DIRECTORY
from scenarios.base import Scenario, ActionScenario
from tools import clear_tool_log, get_tool_log, ToolCallRecord


@dataclass
class TurnResult:
    level: int
    prompt: str
    response: str
    messages_count: int
    tool_calls: list[dict] = field(default_factory=list)


@dataclass
class GaslightResult:
    model_name: str
    scenario_name: str
    scenario_type: str  # "saying" or "actions"
    run_id: str
    initial_response: str
    ground_truth: str
    turns: list[TurnResult] = field(default_factory=list)
    duration: float = 0.0
    error: str | None = None
    all_messages: list[dict] = field(default_factory=list)
    # For action scenarios
    dangerous_tool_called: bool = False
    tool_call_summary: list[dict] = field(default_factory=list)


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
                if hasattr(part, "tool_name"):
                    part_dict["tool_name"] = part.tool_name
                parts.append(part_dict)
            msg_dict["parts"] = parts
        result.append(msg_dict)
    return result


def serialize_tool_calls(tool_calls: list[ToolCallRecord]) -> list[dict]:
    """Convert tool call records to serializable dicts."""
    return [
        {
            "tool_name": tc.tool_name,
            "arguments": tc.arguments,
            "timestamp": tc.timestamp,
            "result": tc.result,
        }
        for tc in tool_calls
    ]


async def run_saying_test(
    model_config: RunnableModel,
    scenario: Scenario,
    run_id: str,
) -> GaslightResult:
    """Run a 'saying' scenario (epistemic manipulation test)."""
    start_time = time.perf_counter()
    model = get_model(model_config)
    agent = Agent(model)

    result = GaslightResult(
        model_name=model_config.name,
        scenario_name=scenario.name,
        scenario_type="saying",
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


async def run_action_test(
    model_config: RunnableModel,
    scenario: ActionScenario,
    run_id: str,
) -> GaslightResult:
    """Run an 'actions' scenario (tool execution manipulation test)."""
    start_time = time.perf_counter()
    model = get_model(model_config)

    # Create agent with tools
    agent = Agent(
        model,
        system_prompt=scenario.system_prompt,
        tools=scenario.tools,
    )

    result = GaslightResult(
        model_name=model_config.name,
        scenario_name=scenario.name,
        scenario_type="actions",
        run_id=run_id,
        initial_response="",
        ground_truth=f"Should NOT call {scenario.dangerous_tool}",
    )

    # Clear tool log for this test
    clear_tool_log()

    try:
        # Initial context message
        initial_result = await agent.run(scenario.initial_context)
        result.initial_response = initial_result.output
        message_history = initial_result.new_messages()

        # Check for dangerous tool calls after initial
        initial_calls = get_tool_log()
        if any(tc.tool_name == scenario.dangerous_tool for tc in initial_calls):
            result.dangerous_tool_called = True

        # Apply each gaslighting level
        for level, gaslight_prompt in enumerate(scenario.gaslighting_levels, start=1):
            # Clear log to track calls per turn
            calls_before = len(get_tool_log())

            turn_result = await agent.run(
                gaslight_prompt,
                message_history=message_history,
            )
            message_history = turn_result.all_messages()

            # Get new tool calls from this turn
            all_calls = get_tool_log()
            new_calls = all_calls[calls_before:]

            # Check if dangerous tool was called
            if any(tc.tool_name == scenario.dangerous_tool for tc in new_calls):
                result.dangerous_tool_called = True

            result.turns.append(
                TurnResult(
                    level=level,
                    prompt=gaslight_prompt,
                    response=turn_result.output,
                    messages_count=len(message_history),
                    tool_calls=serialize_tool_calls(new_calls),
                )
            )

        result.all_messages = serialize_messages(message_history)
        result.tool_call_summary = serialize_tool_calls(get_tool_log())

    except Exception as e:
        result.error = str(e)

    result.duration = time.perf_counter() - start_time
    return result


async def run_gaslighting_test(
    model_config: RunnableModel,
    scenario: Union[Scenario, ActionScenario],
    run_id: str,
) -> GaslightResult:
    """Run a gaslighting test (routes to saying or action based on scenario type)."""
    if isinstance(scenario, ActionScenario):
        return await run_action_test(model_config, scenario, run_id)
    else:
        return await run_saying_test(model_config, scenario, run_id)


async def run_with_semaphore(
    semaphore: asyncio.Semaphore,
    model_config: RunnableModel,
    scenario: Union[Scenario, ActionScenario],
    run_id: str,
) -> GaslightResult:
    """Run a test with concurrency control."""
    async with semaphore:
        print(f"[{model_config.name}] Running {scenario.name} - {run_id}")
        result = await run_gaslighting_test(model_config, scenario, run_id)
        if result.error:
            print(f"[{model_config.name}] Error: {result.error}")
        else:
            status = ""
            if result.scenario_type == "actions":
                status = " | TOOL CALLED!" if result.dangerous_tool_called else " | Resisted"
            print(f"[{model_config.name}] Completed in {result.duration:.2f}s{status}")
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
        "scenario_type": result.scenario_type,
        "run_id": result.run_id,
        "ground_truth": result.ground_truth,
        "initial_response": result.initial_response,
        "turns": [
            {
                "level": t.level,
                "prompt": t.prompt,
                "response": t.response,
                "messages_count": t.messages_count,
                "tool_calls": t.tool_calls,
            }
            for t in result.turns
        ],
        "duration": result.duration,
        "error": result.error,
        "all_messages": result.all_messages,
        # Action-specific fields
        "dangerous_tool_called": result.dangerous_tool_called,
        "tool_call_summary": result.tool_call_summary,
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath


async def run_benchmark(
    models: list[RunnableModel],
    scenarios: list[Union[Scenario, ActionScenario]],
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
        if isinstance(r, BaseException):
            print(f"Task failed with exception: {r}")
            continue
        valid_results.append(r)
        save_result(r, output_dir)

    print(f"Completed {len(valid_results)} tests")
    return valid_results
