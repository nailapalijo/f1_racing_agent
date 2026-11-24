
from tools.openf1_tool import (
    fetch_data,
    find_meeting,
    find_session,
)


def get_pit_stop_analysis(year, grand_prix):
    # Find Grand Prix
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {
            "success": False,
            "message": "Grand Prix not found"
        }

    # Find Race session
    session = find_session(meeting, "Race")

    if not session:
        return {
            "success": False,
            "message": "Race session not found"
        }

    session_key = session["session_key"]

    # Fetch data
    pits = fetch_data(
        "pit",
        {"session_key": session_key}
    )

    drivers = fetch_data(
        "drivers",
        {"session_key": session_key}
    )

    if isinstance(pits, dict) or isinstance(drivers, dict):
        return {
            "success": False,
            "message": "Pit data unavailable"
        }

    # Driver lookup
    driver_map = {
        driver["driver_number"]: driver
        for driver in drivers
    }

    results = []

    # Process pit records
    for pit in pits:
        driver_number = pit.get("driver_number")
        driver = driver_map.get(driver_number, {})

        results.append({
            "driver": driver.get("full_name", "Unknown"),
            "team": driver.get("team_name", "Unknown"),
            "lap": pit.get("lap_number"),
            "pit_duration_seconds": pit.get("pit_duration"),
            "stop_time": pit.get("date")
        })

    # Sort raw records
    results.sort(
        key=lambda x: (
            x["pit_duration_seconds"]
            if isinstance(x["pit_duration_seconds"], (int, float))
            else float("inf")
        )
    )

    # Filter valid pit stops
    valid_pit_stops = [
        stop
        for stop in results
        if isinstance(stop["pit_duration_seconds"], (int, float))
        and 0 < stop["pit_duration_seconds"] <= 120
        and isinstance(stop["lap"], int)
        and stop["lap"] > 1
    ]

    # Calculate average
    valid_times = [
        stop["pit_duration_seconds"]
        for stop in valid_pit_stops
    ]

    average_duration = (
        round(sum(valid_times) / len(valid_times), 3)
        if valid_times
        else None
    )

    return {
        "success": True,
        "grand_prix": meeting["meeting_name"],
        "total_pit_stops": len(results),
        "valid_pit_stop_count": len(valid_pit_stops),
        "average_pit_duration": average_duration,
        "pit_stops": valid_pit_stops,
        "message": "Pit stop analysis completed successfully."
    }
