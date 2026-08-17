import unittest

from agent import Agent
from run_agent import render_dashboard


class CliTests(unittest.TestCase):
    def test_dashboard_contains_run_summary_and_skills(self):
        agent = Agent(name="display-agent")
        output = agent.run("Inspect the API")

        dashboard = render_dashboard(agent, output)

        self.assertIn("IXPANSION AGENT DASHBOARD", dashboard)
        self.assertIn("Agent: display-agent", dashboard)
        self.assertIn("Goal: Inspect the API", dashboard)
        self.assertIn("[1] Define goal: Inspect the API", dashboard)
        self.assertIn("check_goal", dashboard)
        self.assertIn("Memory entries: 1", dashboard)

    def test_dashboard_has_consistent_border_width(self):
        agent = Agent()
        dashboard = render_dashboard(agent, agent.run("Short goal"))
        rows = dashboard.splitlines()

        self.assertTrue(rows)
        self.assertTrue(all(len(row) == len(rows[0]) for row in rows))


if __name__ == "__main__":
    unittest.main()