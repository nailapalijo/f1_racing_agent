
import fastf1
import pandas as pd
from pathlib import Path

# Store FastF1 cache inside the project
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_race_session(year: int, grand_prix: str, session_type: str = "R"):
    """
    Load a Formula 1 session using FastF1.

    Session types:
    FP1, FP2, FP3, Q, SQ, S, R
    """

    try:
        session = fastf1.get_session(
            year,
            grand_prix,
            session_type
        )

        session.load(
            laps=True,
            telemetry=False,
            weather=True,
            messages=False
        )

        return {
            "success": True,
            "session": session,
            "message": "F1 session loaded successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "session": None,
            "message": f"Unable to load session: {error}"
        }


def get_session_summary(year: int, grand_prix: str, session_type: str = "R"):
    """Return basic information about an F1 session."""

    result = get_race_session(year, grand_prix, session_type)

    if not result["success"]:
        return result

    session = result["session"]
    laps = session.laps

    return {
        "success": True,
        "year": year,
        "grand_prix": grand_prix,
        "session_type": session_type,
        "total_laps": len(laps),
        "drivers": sorted(laps["Driver"].dropna().unique().tolist()),
        "message": "Session summary generated."
    }


def get_driver_laps(
    year: int,
    grand_prix: str,
    driver: str,
    session_type: str = "R"
):
    """Get lap times and lap numbers for a driver."""

    result = get_race_session(year, grand_prix, session_type)

    if not result["success"]:
        return result

    session = result["session"]
    driver_laps = session.laps.pick_drivers(driver)

    if driver_laps.empty:
        return {
            "success": False,
            "message": f"No lap data found for driver {driver}."
        }

    selected = driver_laps[
        ["LapNumber", "LapTime", "Compound", "TyreLife"]
    ].copy()

    selected["LapTime"] = selected["LapTime"].apply(
        lambda value: round(value.total_seconds(), 3)
        if pd.notna(value) else None
    )

    return {
        "success": True,
        "driver": driver,
        "laps": selected.to_dict(orient="records"),
        "message": "Driver lap data retrieved."
    }


def get_fastest_lap(
    year: int,
    grand_prix: str,
    session_type: str = "Q"
):
    """Find the fastest recorded lap in a session."""

    result = get_race_session(year, grand_prix, session_type)

    if not result["success"]:
        return result

    fastest = result["session"].laps.pick_fastest()

    if fastest.empty:
        return {
            "success": False,
            "message": "No valid fastest lap found."
        }

    return {
        "success": True,
        "driver": fastest["Driver"],
        "lap_time_seconds": round(
            fastest["LapTime"].total_seconds(), 3
        ),
        "team": fastest["Team"],
        "message": "Fastest lap retrieved."
    }
