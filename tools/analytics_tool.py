
from tools.openf1_tool import (
    fetch_data,
    find_meeting,
    find_session,
    compare_drivers_openf1,
)


def resolve_driver(session_key, driver):
    drivers = fetch_data(
        "drivers",
        {"session_key": session_key}
    )

    if isinstance(drivers, dict):
        return None

    search = str(driver).lower()

    for item in drivers:
        if (
            search == str(item.get("driver_number", "")).lower()
            or search == item.get("name_acronym", "").lower()
            or search in item.get("full_name", "").lower()
        ):
            return item

    return None


def get_driver_telemetry(
    year, grand_prix, driver, session_type="R"
):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "message": "Grand Prix not found"}

    session = find_session(meeting, session_type)

    if not session:
        return {"success": False, "message": "Session not found"}

    session_key = session["session_key"]
    driver_info = resolve_driver(session_key, driver)

    if not driver_info:
        return {"success": False, "message": "Driver not found"}

    data = fetch_data(
        "car_data",
        {
            "session_key": session_key,
            "driver_number": driver_info["driver_number"]
        }
    )

    if isinstance(data, dict) or not data:
        return {"success": False, "message": "Telemetry unavailable"}

    sample_size = min(100, len(data))
    step = max(1, len(data) // sample_size)
    sampled = data[::step][:100]

    telemetry = [
        {
            "date": item.get("date"),
            "speed": item.get("speed"),
            "throttle": item.get("throttle"),
            "brake": item.get("brake"),
            "gear": item.get("n_gear"),
            "rpm": item.get("rpm"),
            "drs": item.get("drs")
        }
        for item in sampled
    ]

    return {
        "success": True,
        "driver": driver_info.get("full_name"),
        "driver_number": driver_info["driver_number"],
        "session": session_type,
        "telemetry": telemetry,
        "message": "OpenF1 telemetry retrieved successfully."
    }


def compare_drivers(
    year, grand_prix, driver_1, driver_2,
    session_type="Q"
):
    return compare_drivers_openf1(
        year, grand_prix, driver_1, driver_2,
        session_type
    )


def analyze_tyre_strategy(
    year, grand_prix, driver, session_type="R"
):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "message": "Grand Prix not found"}

    session = find_session(meeting, session_type)

    if not session:
        return {"success": False, "message": "Session not found"}

    session_key = session["session_key"]
    driver_info = resolve_driver(session_key, driver)

    if not driver_info:
        return {"success": False, "message": "Driver not found"}

    stints = fetch_data(
        "stints",
        {
            "session_key": session_key,
            "driver_number": driver_info["driver_number"]
        }
    )

    if isinstance(stints, dict) or not stints:
        return {
            "success": False,
            "message": "Tyre stint data unavailable"
        }

    summary = []

    for stint in stints:
        summary.append({
            "stint_number": stint.get("stint_number"),
            "compound": stint.get("compound"),
            "lap_start": stint.get("lap_start"),
            "lap_end": stint.get("lap_end"),
            "tyre_age_at_start": stint.get("tyre_age_at_start")
        })

    return {
        "success": True,
        "driver": driver_info.get("full_name"),
        "driver_number": driver_info["driver_number"],
        "grand_prix": meeting["meeting_name"],
        "stints": summary,
        "message": "OpenF1 tyre strategy retrieved successfully."
    }
