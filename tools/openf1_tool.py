import json
import urllib.parse
import urllib.request


BASE_URL = "https://api.openf1.org/v1"


def fetch_data(endpoint, params=None):
    try:
        query = urllib.parse.urlencode(params or {})
        url = f"{BASE_URL}/{endpoint}?{query}"

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "APEX-F1-Agent"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    except Exception as e:
        return {"error": str(e)}


def find_meeting(year, grand_prix):
    meetings = fetch_data(
        "meetings",
        {"year": year}
    )

    if isinstance(meetings, dict):
        return None

    search = grand_prix.lower()

    for meeting in meetings:
        name = meeting.get("meeting_name", "").lower()

        if search in name:
            return meeting

    return None


def find_session(meeting, session_type):
    sessions = fetch_data(
        "sessions",
        {"meeting_key": meeting["meeting_key"]}
    )

    if isinstance(sessions, dict):
        return None

    search = session_type.lower()

    for session in sessions:
        name = session.get("session_name", "").lower()

        if search in name:
            return session

    return None
def get_fastest_lap_openf1(year, grand_prix, session_type="Qualifying"):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "error": "Grand Prix not found"}

    session = find_session(meeting, session_type)

    if not session:
        return {"success": False, "error": "Session not found"}

    laps = fetch_data(
        "laps",
        {"session_key": session["session_key"]}
    )

    if isinstance(laps, dict) or not laps:
        return {"success": False, "error": "Lap data unavailable"}

    valid_laps = [
        lap for lap in laps
        if lap.get("lap_duration") is not None
    ]

    if not valid_laps:
        return {"success": False, "error": "No valid lap times found"}

    fastest = min(valid_laps, key=lambda lap: lap["lap_duration"])

    drivers = fetch_data(
        "drivers",
        {"session_key": session["session_key"]}
    )

    driver_info = next(
        (
            d for d in drivers
            if d.get("driver_number") == fastest.get("driver_number")
        ),
        {}
    )

    return {
        "success": True,
        "grand_prix": meeting["meeting_name"],
        "session": session_type,
        "driver": driver_info.get("full_name", "Unknown"),
        "driver_number": fastest.get("driver_number"),
        "lap_number": fastest.get("lap_number"),
        "fastest_lap_seconds": fastest["lap_duration"]
    }
def compare_drivers_openf1(
    year, grand_prix, driver_1, driver_2,
    session_type="Qualifying"
):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "error": "Grand Prix not found"}

    session = find_session(meeting, session_type)

    if not session:
        return {"success": False, "error": "Session not found"}

    params = {"session_key": session["session_key"]}

    laps = fetch_data("laps", params)
    drivers = fetch_data("drivers", params)

    if isinstance(laps, dict) or isinstance(drivers, dict):
        return {"success": False, "error": "OpenF1 data unavailable"}

    driver_map = {
        d["driver_number"]: d
        for d in drivers
    }

    def best_lap(driver_name):
        number = next(
            (
                n for n, d in driver_map.items()
                if driver_name.lower() in d.get("full_name", "").lower()
                or driver_name.lower() == d.get("name_acronym", "").lower()
            ),
            None
        )

        if number is None:
            return None

        times = [
            lap["lap_duration"]
            for lap in laps
            if lap.get("driver_number") == number
            and lap.get("lap_duration") is not None
        ]

        return min(times) if times else None

    time_1 = best_lap(driver_1)
    time_2 = best_lap(driver_2)

    if time_1 is None or time_2 is None:
        return {"success": False, "error": "Driver lap data not found"}

    return {
        "success": True,
        "driver_1": driver_1,
        "driver_1_best_lap": time_1,
        "driver_2": driver_2,
        "driver_2_best_lap": time_2,
        "difference_seconds": round(abs(time_1 - time_2), 3),
        "faster_driver": driver_1 if time_1 < time_2 else driver_2
    }
def get_race_summary_openf1(year, grand_prix):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "error": "Grand Prix not found"}

    session = find_session(meeting, "Race")

    if not session:
        return {"success": False, "error": "Race session not found"}

    params = {"session_key": session["session_key"]}

    drivers = fetch_data("drivers", params)
    laps = fetch_data("laps", params)

    if isinstance(drivers, dict) or isinstance(laps, dict):
        return {"success": False, "error": "Race data unavailable"}

    return {
        "success": True,
        "grand_prix": meeting["meeting_name"],
        "circuit": meeting.get("circuit_short_name"),
        "year": year,
        "session": "Race",
        "total_drivers": len(drivers),
        "total_lap_records": len(laps),
        "drivers": [
            {
                "name": d.get("full_name"),
                "team": d.get("team_name"),
                "number": d.get("driver_number")
            }
            for d in drivers
        ]
    }
def get_race_results_openf1(year, grand_prix):
    meeting = find_meeting(year, grand_prix)

    if not meeting:
        return {"success": False, "error": "Grand Prix not found"}

    session = find_session(meeting, "Race")

    if not session:
        return {"success": False, "error": "Race session not found"}

    positions = fetch_data(
        "position",
        {"session_key": session["session_key"]}
    )

    drivers = fetch_data(
        "drivers",
        {"session_key": session["session_key"]}
    )

    if isinstance(positions, dict) or isinstance(drivers, dict):
        return {"success": False, "error": "Race results unavailable"}

    latest_positions = {}

    for item in positions:
        number = item.get("driver_number")
        if number is None:
            continue

        if (
            number not in latest_positions
            or item.get("date", "") > latest_positions[number].get("date", "")
        ):
            latest_positions[number] = item

    driver_map = {
        d["driver_number"]: d
        for d in drivers
    }

    results = []

    for number, item in latest_positions.items():
        driver = driver_map.get(number, {})

        results.append({
            "position": item.get("position"),
            "driver": driver.get("full_name", "Unknown"),
            "team": driver.get("team_name", "Unknown"),
            "driver_number": number
        })

    results.sort(
        key=lambda x: x["position"] if x["position"] is not None else 999
    )

    return {
        "success": True,
        "grand_prix": meeting["meeting_name"],
        "year": year,
        "results": results
    }
