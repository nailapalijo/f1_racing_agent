
from tools.race_intelligence_tool import get_pit_stop_analysis


def get_pit_strategy_analysis(year, grand_prix):
    """
    Analyze pit stop performance for every driver.
    """

    data = get_pit_stop_analysis(year, grand_prix)

    if not data.get("success"):
        return data

    pit_stops = data.get("pit_stops", [])

    if not pit_stops:
        return {
            "success": False,
            "message": "No valid pit stop data available."
        }

    driver_stats = {}

    for stop in pit_stops:
        driver = stop["driver"]
        duration = stop["pit_duration_seconds"]

        if driver not in driver_stats:
            driver_stats[driver] = {
                "driver": driver,
                "team": stop["team"],
                "total_stops": 0,
                "durations": []
            }

        driver_stats[driver]["total_stops"] += 1
        driver_stats[driver]["durations"].append(duration)

    strategy = []

    for driver, stats in driver_stats.items():
        durations = stats["durations"]

        strategy.append({
            "driver": driver,
            "team": stats["team"],
            "total_stops": stats["total_stops"],
            "fastest_stop": min(durations),
            "average_duration": round(
                sum(durations) / len(durations), 3
            )
        })

    strategy.sort(
        key=lambda x: x["average_duration"]
    )

    return {
        "success": True,
        "grand_prix": data["grand_prix"],
        "total_drivers": len(strategy),
        "total_valid_stops": len(pit_stops),
        "driver_strategy": strategy,
        "message": "Pit stop strategy analysis completed."
    }
