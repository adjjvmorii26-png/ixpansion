import argparse

from agent import Agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple IXPANSION agent.")
    parser.add_argument("--name", default="ixpansion-agent", help="Name of the agent.")
    parser.add_argument("--goal", default="Explore the mesh", help="Goal for the agent to pursue.")
    parser.add_argument(
        "--use-xai", action="store_true", help="Ask xAI to summarize the goal."
    )
    args = parser.parse_args()

    agent = Agent(name=args.name)
    output = agent.run(args.goal)

    print(f"Agent: {agent.name}")
    print(f"Goal: {output['goal']}")
    print("Plan:")
    for step in output["plan"]:
        print(f"  - {step}")
    print("Results:")
    for result in output["results"]:
        print(f"  - {result}")
    if args.use_xai:
        print("xAI:")
        print(agent.ask(args.goal))


if __name__ == "__main__":
    main()
