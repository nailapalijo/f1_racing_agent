
from tools.race_intelligence_tool import get_pit_stop_analysis
from tools.pit_strategy_tool import get_pit_strategy_analysis

from tools.race_tool import (
    get_session_summary,
    get_driver_laps,
)

from tools.analytics_tool import (
    get_driver_telemetry,
    analyze_tyre_strategy,
)

from tools.openf1_tool import (
    get_fastest_lap_openf1,
    compare_drivers_openf1,
    get_race_summary_openf1,
    get_race_results_openf1,
)


class F1AgentExecutor:

    def __init__(self):
        self.tools = {
            "session_summary": get_session_summary,
            "race_summary": get_race_summary_openf1,
            "race_results": get_race_results_openf1,
            "driver_laps": get_driver_laps,
            "fastest_lap": get_fastest_lap_openf1,
            "driver_telemetry": get_driver_telemetry,
            "compare_drivers": compare_drivers_openf1,
            "tyre_strategy": analyze_tyre_strategy,
            "pit_stop_analysis": get_pit_stop_analysis,
            "pit_strategy_analysis": get_pit_strategy_analysis,
        }

    def select_tool(self, question: str):
        text = question.lower()

        if any(word in text for word in [
            "pit strategy", "pit stop strategy",
            "pit crew strategy", "pit stop performance"
        ]):
            return "pit_strategy_analysis"

        if any(word in text for word in [
            "race results", "finishing positions",
            "final positions", "race classification",
            "who won", "race winner"
        ]):
            return "race_results"

        if any(word in text for word in [
            "telemetry", "throttle", "brake",
            "rpm", "speed", "gear"
        ]):
            return "driver_telemetry"

        if any(word in text for word in [
            "compare", "comparison", "versus",
            " vs ", "who is faster"
        ]):
            return "compare_drivers"

        if any(word in text for word in [
            "tyre strategy", "tire strategy",
            "stint", "tyre wear", "tire wear",
            "tyre compound", "tire compound"
        ]):
            return "tyre_strategy"

        if any(word in text for word in [
            "pit stop", "pit stops", "pitstop"
        ]):
            return "pit_stop_analysis"

        if any(word in text for word in [
            "fastest lap", "quickest lap", "best lap"
        ]):
            return "fastest_lap"

        if any(word in text for word in [
            "driver laps", "lap times",
            "lap time", "tyre life"
        ]):
            return "driver_laps"

        if any(word in text for word in [
            "race summary", "race overview",
            "race information", "race session"
        ]):
            return "race_summary"

        if any(word in text for word in [
            "session summary", "which drivers",
            "total laps"
        ]):
            return "session_summary"

        return None

    def execute(self, question: str, **kwargs):
        tool_name = self.select_tool(question)

        if tool_name is None:
            return {
                "success": False,
                "tool": None,
                "message": "Could not identify the required racing tool."
            }

        required_parameters = {
            "session_summary": ["year", "grand_prix"],
            "race_summary": ["year", "grand_prix"],
            "race_results": ["year", "grand_prix"],
            "driver_laps": ["year", "grand_prix", "driver"],
            "fastest_lap": ["year", "grand_prix"],
            "driver_telemetry": ["year", "grand_prix", "driver"],
            "compare_drivers": [
                "year", "grand_prix", "driver_1", "driver_2"
            ],
            "tyre_strategy": ["year", "grand_prix", "driver"],
            "pit_stop_analysis": ["year", "grand_prix"],
            "pit_strategy_analysis": ["year", "grand_prix"],
        }

        missing = [
            parameter
            for parameter in required_parameters[tool_name]
            if parameter not in kwargs
        ]

        if missing:
            return {
                "success": False,
                "tool": tool_name,
                "message": "Missing required information: "
                + ", ".join(missing)
            }

        try:
            result = self.tools[tool_name](**kwargs)

            return {
                "success": result.get("success", False),
                "tool": tool_name,
                "result": result,
                "message": result.get("message", "Tool executed.")
            }

        except Exception as error:
            return {
                "success": False,
                "tool": tool_name,
                "message": f"Tool execution failed: {error}"
            }


if __name__ == "__main__":
    agent = F1AgentExecutor()
    print("APEX F1 Agent initialized.")
    print("Available tools:", list(agent.tools.keys()))
