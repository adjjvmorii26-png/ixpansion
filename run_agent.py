import argparse

from agent import Agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple IXPANSION agent.")
    parser.add_argument("--name", default="ixpansion-agent", help="Name of the agent.")
    parser.add_argument("--goal", default="Explore the mesh", help="Goal for the agent to pursue.")
    parser.add_argument(
        "--use-tokenrouter",
        "--use-xai",
        dest="use_tokenrouter",
        action="store_true",
        help="Ask TokenRouter to summarize the goal.",
    )
    args = parser.parse_args()

    agent = Agent(name=args.name)
    if args.use_tokenrouter and not agent.api_key:
        parser.error("TOKENROUTER_API_KEY is not configured")

    output = agent.run(args.goal)

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
