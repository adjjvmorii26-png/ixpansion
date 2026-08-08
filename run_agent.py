import argparse
import textwrap
from typing import Any, Dict

from agent import Agent


def render_dashboard(agent: Agent, output: Dict[str, Any]) -> str:
    """Render a compact, terminal-safe view of one agent run."""
    width = 62

    def row(content: str = "") -> str:
        return "|" + content[:width].ljust(width) + "|"

    lines = [
        "+" + "-" * width + "+",
        row(" IXPANSION AGENT DASHBOARD"),
        "+" + "-" * width + "+",
        row(f" Agent: {agent.name}"),
        row(f" Goal: {output['goal']}"),
        row(" Status: complete"),
        "+" + "-" * width + "+",
        row(" PLAN"),
    ]
    lines.extend(
        row(f" [{index}] {step}")
        for index, step in enumerate(output["plan"], start=1)
    )
    skills = ", ".join(agent.list_skills())
    skill_rows = textwrap.wrap(
        skills,
        width=width - 1,
        break_long_words=False,
        break_on_hyphens=False,
    ) or ["none"]
    lines.extend(
        [
            "+" + "-" * width + "+",
            row(" SKILLS"),
            "+" + "-" * width + "+",
        ]
    )
    lines.extend(row(f" {skill_row}") for skill_row in skill_rows)
    lines.extend(
        [
            row(f" Memory entries: {len(agent.memory)}"),
            "+" + "-" * width + "+",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple IXPANSION agent.")
    parser.add_argument("--name", default="ixpansion-agent", help="Name of the agent.")
    parser.add_argument("--goal", default="Explore the mesh", help="Goal for the agent to pursue.")
    parser.add_argument(
        "--model",
        default=None,
        help="TokenRouter model override; defaults to TOKENROUTER_MODEL or the premium standard model.",
    )
    parser.add_argument(
        "--use-tokenrouter",
        "--use-xai",
        dest="use_tokenrouter",
        action="store_true",
        help="Ask TokenRouter to summarize the goal.",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Show a compact visual dashboard after the run.",
    )
    args = parser.parse_args()

    agent = Agent(name=args.name, model=args.model)
    if args.use_tokenrouter and not agent.api_key:
        parser.error("TOKENROUTER_API_KEY is not configured")

    output = agent.run(args.goal)

    if args.dashboard:
        print(render_dashboard(agent, output))
        return

    print(f"Agent: {agent.name}")
    print(f"Goal: {output['goal']}")
    print("Plan:")
    for step in output["plan"]:
        print(f"  - {step}")
    print("Results:")
    for result in output["results"]:
        print(f"  - {result}")
    if args.use_tokenrouter:
        print("TokenRouter:")
        try:
            print(agent.ask(args.goal))
        except RuntimeError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
