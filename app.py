"""
swim-today: Can I swim today? Just like wttr.in but for swimming.

Usage:
    curl <your-host>/Miami
    curl <your-host>/Barcelona
    curl <your-host>/Sydney?format=json
    curl <your-host>/Bali?format=short
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, Response, render_template, request

from lib.geocoding import LocationNotFound, GeocodingError, geocode, format_location
from lib.marine import MarineDataError, NoMarineData, fetch_marine_data
from lib.weather import WeatherDataError, fetch_weather_data
from lib.swim_score import evaluate_conditions
from lib.renderer import render_ansi, render_short, render_json
from lib.easter_eggs import get_easter_egg

app = Flask(__name__)

# Terminal user agents (like wttr.in)
TERMINAL_AGENTS = ["curl", "wget", "httpie", "fetch", "lwp-request", "python-requests"]

# Egypt coastal cities with hardcoded coordinates (avoids geocoding on every home page load)
EGYPT_CITIES = [
    {"name": "Hurghada",        "lat": 27.2579, "lon": 33.8116, "tz": "Africa/Cairo"},
    {"name": "Sharm El Sheikh", "lat": 27.9158, "lon": 34.3300, "tz": "Africa/Cairo"},
    {"name": "Dahab",           "lat": 28.5091, "lon": 34.5133, "tz": "Africa/Cairo"},
    {"name": "Marsa Alam",      "lat": 25.0660, "lon": 34.8990, "tz": "Africa/Cairo"},
    {"name": "El Gouna",        "lat": 27.1827, "lon": 33.6803, "tz": "Africa/Cairo"},
    {"name": "Ain Sokhna",      "lat": 29.6008, "lon": 32.3131, "tz": "Africa/Cairo"},
    {"name": "Alexandria",      "lat": 31.2001, "lon": 29.9187, "tz": "Africa/Cairo"},
    {"name": "Marsa Matrouh",   "lat": 31.3543, "lon": 27.2373, "tz": "Africa/Cairo"},
    {"name": "Nuweiba",         "lat": 29.0469, "lon": 34.6653, "tz": "Africa/Cairo"},
    {"name": "Taba",            "lat": 29.4917, "lon": 34.8903, "tz": "Africa/Cairo"},
    {"name": "Ras Sedr",        "lat": 29.5833, "lon": 32.7167, "tz": "Africa/Cairo"},
    {"name": "Safaga",          "lat": 26.7333, "lon": 33.9333, "tz": "Africa/Cairo"},
]


def _fetch_city_data(city: dict) -> dict:
    """Fetch marine + weather for one city. Returns a summary dict."""
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            mf = pool.submit(fetch_marine_data, city["lat"], city["lon"], city["tz"])
            wf = pool.submit(fetch_weather_data, city["lat"], city["lon"], city["tz"])
        marine = mf.result()
        weather = wf.result()
        score = evaluate_conditions(marine, weather)
        return {
            "name": city["name"],
            "verdict": score["verdict"],
            "water_temp": marine.get("sea_surface_temp"),
            "wave_height": marine.get("wave_height"),
            "wind_speed": weather.get("wind_speed"),
            "weather": score["factors"]["weather_code"]["label"],
            "summary": score["summary"],
            "ok": True,
        }
    except Exception:
        return {"name": city["name"], "ok": False}


def _fetch_all_egypt() -> list[dict]:
    """Fetch live data for all Egypt cities in parallel."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(_fetch_city_data, EGYPT_CITIES))
    return [r for r in results if r["ok"]]


def _is_terminal(user_agent: str) -> bool:
    """Detect if request is from a terminal client."""
    if not user_agent:
        return True  # Default to terminal for empty UA
    ua_lower = user_agent.lower()
    return any(agent in ua_lower for agent in TERMINAL_AGENTS)


def _get_format(args, user_agent: str) -> str:
    """Determine output format from query params or user agent."""
    fmt = args.get("format", "").lower()
    if fmt in ("json", "j1"):
        return "json"
    if fmt in ("short", "s", "1"):
        return "short"
    if fmt in ("html",):
        return "html"
    if _is_terminal(user_agent):
        return "ansi"
    return "html"


@app.route("/")
def index():
    """Help page / landing page with live Egypt data."""
    user_agent = request.headers.get("User-Agent", "")
    cities = _fetch_all_egypt()

    if _is_terminal(user_agent):
        return Response(_render_terminal_home(cities, request.host), mimetype="text/plain")

    return render_template("index.html", cities=cities, host=request.host)


@app.route("/favicon.ico")
def favicon():
    return Response("", status=204)


@app.route("/:help")
def help_page():
    cities = _fetch_all_egypt()
    return Response(_render_terminal_home(cities, request.host), mimetype="text/plain")


@app.route("/<path:location>")
def swim_report(location: str):
    """Main endpoint: get swim report for a location."""
    location = location.replace("+", " ")
    user_agent = request.headers.get("User-Agent", "")
    fmt = _get_format(request.args, user_agent)

    # ── Geocode ──────────────────────────────────────────────────────────
    try:
        geo = geocode(location)
    except LocationNotFound as e:
        return _error_response(str(e), fmt, 404)
    except GeocodingError as e:
        return _error_response(str(e), fmt, 502)

    lat = geo["latitude"]
    lon = geo["longitude"]
    tz = geo.get("timezone", "auto")
    location_str = format_location(geo)

    # ── Fetch marine + weather data in parallel ──────────────────────────
    with ThreadPoolExecutor(max_workers=2) as executor:
        marine_future = executor.submit(fetch_marine_data, lat, lon, tz)
        weather_future = executor.submit(fetch_weather_data, lat, lon, tz)

    try:
        marine = marine_future.result()
    except NoMarineData:
        return _not_coastal_response(location_str, fmt)
    except MarineDataError as e:
        return _error_response(f"Marine data error: {e}", fmt, 502)

    try:
        weather = weather_future.result()
    except WeatherDataError as e:
        return _error_response(f"Weather data error: {e}", fmt, 502)

    # ── Score conditions ─────────────────────────────────────────────────
    score = evaluate_conditions(marine, weather)

    # ── Render output ────────────────────────────────────────────────────
    if fmt == "json":
        data = render_json(location_str, geo, score, marine, weather)
        return Response(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            mimetype="application/json",
        )

    if fmt == "short":
        return Response(render_short(location_str, score, marine, weather), mimetype="text/plain")

    if fmt == "html":
        return render_template(
            "report.html",
            location=location_str,
            score=score,
            marine=marine,
            weather=weather,
            geo=geo,
            host=request.host,
        )

    # ANSI terminal output
    return Response(render_ansi(location_str, score, marine, weather), mimetype="text/plain")


def _not_coastal_response(location: str, fmt: str) -> Response:
    """Friendly rejection for inland locations -- now with easter eggs."""
    egg = get_easter_egg(location)
    water = egg.get("water")
    joke = egg["joke"]
    suggestion = egg.get("suggestion", "Nice")
    host = request.host

    if fmt == "json":
        payload = {
            "error": True,
            "message": f"{location} is not near the coast.",
            "hint": "swim.today works for coastal cities and beaches.",
            "joke": joke,
        }
        if water:
            payload["water_body"] = water
        return Response(
            json.dumps(payload, indent=2) + "\n",
            mimetype="application/json",
            status=404,
        )

    if fmt == "short":
        short_joke = joke.split(".")[0] + "."
        return Response(
            f"{location}: N/A -- {short_joke}\n",
            mimetype="text/plain",
            status=404,
        )

    if fmt == "ansi":
        header = water if water else f"{location} is not near the coast."
        # Word-wrap the joke at ~60 chars for terminal readability
        wrapped = _wrap_text(joke, width=60, indent="  ")
        text = (
            f"\n"
            f"  \033[1m\033[96mCan I Swim Today?\033[0m  \033[37m{location}\033[0m\n"
            f"  \033[2m{'=' * (len(f'Can I Swim Today?  {location}') + 1)}\033[0m\n"
            f"\n"
            f"  \033[96m<><\033[0m  \033[93m{header}\033[0m\n"
            f"\n"
            f"{wrapped}\n"
            f"\n"
            f"  \033[37mTry a real beach instead:\033[0m\n"
            f"\n"
            f"    curl {host}/{suggestion}\n"
            f"    curl {host}/Miami\n"
            f"    curl {host}/Barcelona\n"
            f"\n"
            f"  \033[2m><>  swim.today | Powered by Open-Meteo  <><\033[0m\n"
            f"\n"
        )
        return Response(text, mimetype="text/plain", status=404)

    # HTML
    return Response(
        render_template(
            "not_coastal.html",
            location=location,
            water=water,
            joke=joke,
            suggestion=suggestion,
        ),
        mimetype="text/html",
        status=404,
    )


def _wrap_text(text: str, width: int = 60, indent: str = "  ") -> str:
    """Word-wrap text to a given width with an indent prefix."""
    words = text.split()
    lines = []
    current = indent
    for word in words:
        if len(current) + len(word) + 1 > width + len(indent) and current != indent:
            lines.append(current)
            current = indent
        current += (" " if current != indent else "") + word
    if current != indent:
        lines.append(current)
    return "\n".join(lines)


def _error_response(message: str, fmt: str, status: int) -> Response:
    """Return an error in the appropriate format."""
    if fmt == "json":
        return Response(
            json.dumps({"error": True, "message": message}, indent=2) + "\n",
            mimetype="application/json",
            status=status,
        )

    if fmt in ("ansi", "short"):
        error_text = f"\n  \033[91mError:\033[0m {message}\n\n"
        return Response(error_text, mimetype="text/plain", status=status)

    return Response(
        render_template("error.html", message=message),
        mimetype="text/html",
        status=status,
    )


def _render_terminal_home(cities: list[dict], host: str) -> str:
    """Render the terminal home page with live Egypt data table."""
    R = "\033[0m"
    B = "\033[1m"
    D = "\033[2m"
    CY = "\033[96m"
    W = "\033[37m"
    GR = "\033[92m"
    YL = "\033[93m"
    RD = "\033[91m"
    WH = "\033[97m"

    verdict_color = {"YES": GR, "MAYBE": YL, "NO": RD}

    lines = [
        "",
        f"  {CY}><>{R}  {B}{CY}swim.today{R}  {CY}<><{R} -- Can I swim today?",
        "",
        f"  {B}Egypt Coast{R}          Water  Waves  Wind   Weather",
        f"  {D}{'-' * 62}{R}",
    ]

    for c in cities:
        vc = verdict_color.get(c["verdict"], W)
        v = f"{vc}{c['verdict']:<5}{R}"

        wt = f"{c['water_temp']:.0f}C" if c.get("water_temp") is not None else " -- "
        wh = f"{c['wave_height']:.1f}m" if c.get("wave_height") is not None else " -- "
        ws = f"{c['wind_speed']:.0f}km/h" if c.get("wind_speed") is not None else " -- "
        wx = c.get("weather", "")[:12]

        lines.append(
            f"  {v} {WH}{c['name']:<17}{R}"
            f"{wt:>5}  {wh:>5}  {ws:>6}   {D}{wx}{R}"
        )

    lines.append(f"  {D}{'-' * 62}{R}")
    lines.append("")
    lines.append(f"  {B}Usage:{R}  curl {host}/Hurghada")
    lines.append(f"          curl {host}/Sharm+El+Sheikh")
    lines.append(f"          curl {host}/Dahab?format=json")
    lines.append("")
    lines.append(f"  {D}swim.today | Powered by Open-Meteo{R}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
