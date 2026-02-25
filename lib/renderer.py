"""
ANSI terminal renderer: produces beautiful colored output for curl users.
"""

from lib.constants import (
    YES, MAYBE, NO,
    RESET, BOLD, DIM,
    CYAN, BLUE, GREEN, YELLOW, RED, WHITE, BRIGHT_CYAN,
    BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_RED, BRIGHT_WHITE, BRIGHT_BLUE,
    VERDICT_COLORS,
    BAR_FILLED, BAR_EMPTY, BAR_LENGTH,
)


def render_ansi(location: str, score: dict, marine: dict, weather: dict) -> str:
    """
    Render the full swim report as ANSI-colored terminal output.
    """
    verdict = score["verdict"]
    factors = score["factors"]
    tips = score["tips"]
    summary = score["summary"]

    vc = VERDICT_COLORS[verdict]
    lines = []

    # ── Header ───────────────────────────────────────────────────────────
    lines.append("")
    lines.append(f"  {BOLD}{BRIGHT_CYAN}Can I Swim Today?{RESET}  {WHITE}{location}{RESET}")
    lines.append(f"  {DIM}{'=' * (len(_strip_ansi(f'Can I Swim Today?  {location}')) + 1)}{RESET}")
    lines.append("")

    # ── Waves ASCII art + Verdict ────────────────────────────────────────
    verdict_text = _verdict_art(verdict)
    for line in verdict_text:
        lines.append(line)
    lines.append("")

    # ── Metrics ──────────────────────────────────────────────────────────

    # Water temperature
    wt = factors["water_temp"]
    if wt["value"] is not None:
        temp_c = wt["value"]
        temp_f = temp_c * 9 / 5 + 32
        lines.append(_metric_line(
            "Water Temp",
            f"{temp_c:.0f}C ({temp_f:.0f}F)",
            wt["bar"], wt["label"], wt["verdict"],
            bar_color_fn=_temp_bar_color,
        ))
    else:
        lines.append(_metric_line_na("Water Temp", "No data (too far from coast?)"))

    # Wave height
    wh = factors["wave_height"]
    if wh["value"] is not None:
        lines.append(_metric_line(
            "Wave Height",
            f"{wh['value']:.1f} m",
            wh["bar"], wh["label"], wh["verdict"],
            bar_color_fn=_wave_bar_color,
            invert=True,
        ))
    else:
        lines.append(_metric_line_na("Wave Height", "No data"))

    # Wind speed
    ws = factors["wind_speed"]
    if ws["value"] is not None:
        lines.append(_metric_line(
            "Wind Speed",
            f"{ws['value']:.0f} km/h",
            ws["bar"], ws["label"], ws["verdict"],
            bar_color_fn=_danger_bar_color,
            invert=True,
        ))
    else:
        lines.append(_metric_line_na("Wind Speed", "No data"))

    # UV Index
    uv = factors["uv_index"]
    if uv["value"] is not None:
        lines.append(_metric_line(
            "UV Index",
            f"{uv['value']:.0f}",
            uv["bar"], uv["label"], uv["verdict"],
            bar_color_fn=_uv_bar_color,
            invert=True,
        ))
    else:
        lines.append(_metric_line_na("UV Index", "No data"))

    # Air temperature
    air_temp = weather.get("air_temp")
    if air_temp is not None:
        air_f = air_temp * 9 / 5 + 32
        lines.append(f"  {WHITE}{'Air Temp':<15}{RESET}{BRIGHT_WHITE}{air_temp:.0f}C ({air_f:.0f}F){RESET}")
    
    # Weather condition
    wc = factors["weather_code"]
    lines.append(f"  {WHITE}{'Weather':<15}{RESET}{BRIGHT_WHITE}{wc['label']}{RESET}")

    # Rain
    precip = factors["precipitation"]
    if precip["value"] is not None and precip["value"] > 0:
        lines.append(f"  {WHITE}{'Rain':<15}{RESET}{BRIGHT_WHITE}{precip['value']:.1f} mm{RESET}  {precip['label']}")

    # Humidity
    humidity = weather.get("humidity")
    if humidity is not None:
        lines.append(f"  {WHITE}{'Humidity':<15}{RESET}{BRIGHT_WHITE}{humidity}%{RESET}")

    lines.append("")

    # ── Divider ──────────────────────────────────────────────────────────
    lines.append(f"  {DIM}{'-' * 50}{RESET}")

    # ── Summary ──────────────────────────────────────────────────────────
    lines.append(f"  {vc}{BOLD}{summary}{RESET}")

    # ── Tips ─────────────────────────────────────────────────────────────
    if tips:
        for tip in tips[:3]:
            lines.append(f"  {DIM}{tip}{RESET}")

    # ── Footer ───────────────────────────────────────────────────────────
    lines.append("")
    lines.append(f"  {DIM}swim.today | Powered by Open-Meteo{RESET}")
    lines.append("")

    return "\n".join(lines)


def render_short(location: str, score: dict, marine: dict, weather: dict) -> str:
    """One-line output for status bars and scripts."""
    verdict = score["verdict"]
    wt = score["factors"]["water_temp"]
    wh = score["factors"]["wave_height"]

    temp_str = f"{wt['value']:.0f}C" if wt["value"] is not None else "N/A"
    wave_str = f"{wh['value']:.1f}m" if wh["value"] is not None else "N/A"

    return f"{location}: {verdict}  {temp_str} water  {wave_str} waves\n"


def render_json(location: str, geo: dict, score: dict, marine: dict, weather: dict) -> dict:
    """Structured JSON output for APIs and scripts."""
    return {
        "location": {
            "name": geo.get("name"),
            "country": geo.get("country"),
            "region": geo.get("admin1"),
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
        },
        "verdict": score["verdict"],
        "summary": score["summary"],
        "tips": score["tips"],
        "conditions": {
            "water_temperature_c": marine.get("sea_surface_temp"),
            "wave_height_m": marine.get("wave_height"),
            "wave_period_s": marine.get("wave_period"),
            "wave_direction_deg": marine.get("wave_direction"),
            "swell_height_m": marine.get("swell_wave_height"),
            "ocean_current_kmh": marine.get("ocean_current_velocity"),
            "air_temperature_c": weather.get("air_temp"),
            "feels_like_c": weather.get("apparent_temp"),
            "wind_speed_kmh": weather.get("wind_speed"),
            "wind_gusts_kmh": weather.get("wind_gusts"),
            "uv_index": weather.get("uv_index"),
            "precipitation_mm": weather.get("precipitation"),
            "cloud_cover_pct": weather.get("cloud_cover"),
            "humidity_pct": weather.get("humidity"),
            "weather_description": score["factors"]["weather_code"]["label"],
        },
        "factors": {
            k: {"value": v["value"], "label": v["label"], "verdict": v["verdict"]}
            for k, v in score["factors"].items()
        },
    }


# ── Internal helpers ─────────────────────────────────────────────────────────

def _verdict_art(verdict: str) -> list[str]:
    """Generate asciiquarium-inspired ASCII art with fish, bubbles, and verdict."""
    vc = VERDICT_COLORS[verdict]
    wave = BRIGHT_CYAN
    bub = DIM + WHITE

    if verdict == YES:
        verdict_display = "Y E S !"
    elif verdict == MAYBE:
        verdict_display = "M A Y B E"
    else:
        verdict_display = "N O"

    # Center the verdict in a wave field
    pad_total = 24 - len(verdict_display)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left

    lines = [
        f"  {bub}    .  o  .              .  o  .{RESET}",
        f"  {wave}><>   ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   {RESET}{wave}<><{RESET}",
        f"  {wave}  ~ ~ {RESET}{vc}{BOLD} {' ' * pad_left}{verdict_display}{' ' * pad_right} {RESET}{wave}~ ~{RESET}",
        f"  {wave}<><   ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   {RESET}{wave}><>{RESET}",
        f"  {bub}    .  o  .              .  o  .{RESET}",
    ]
    return lines


def _metric_line(
    name: str,
    value_str: str,
    bar_fill: int,
    label: str,
    verdict: str,
    bar_color_fn=None,
    invert: bool = False,
) -> str:
    """Render a single metric line with bar and label."""
    # Name column (15 chars)
    name_part = f"  {WHITE}{name:<15}{RESET}"

    # Value column (18 chars)
    value_part = f"{BRIGHT_WHITE}{value_str:<18}{RESET}"

    # Bar
    bar_fill = max(0, min(BAR_LENGTH, bar_fill))
    if bar_color_fn:
        bar_color = bar_color_fn(bar_fill, invert)
    else:
        bar_color = GREEN
    filled = BAR_FILLED * bar_fill
    empty = BAR_EMPTY * (BAR_LENGTH - bar_fill)
    bar_part = f"{bar_color}{filled}{DIM}{empty}{RESET}"

    # Label with verdict color
    label_color = VERDICT_COLORS.get(verdict, WHITE)
    label_part = f"  {label_color}{label}{RESET}"

    return f"{name_part}{value_part}{bar_part}{label_part}"


def _metric_line_na(name: str, reason: str) -> str:
    """Render a metric line when data is not available."""
    return f"  {WHITE}{name:<15}{RESET}{DIM}{reason}{RESET}"


def _temp_bar_color(fill: int, invert: bool = False) -> str:
    """Color for temperature bar: blue(cold) → green(good) → yellow(hot)."""
    if fill <= 3:
        return BLUE
    elif fill <= 6:
        return BRIGHT_GREEN
    elif fill <= 8:
        return GREEN
    else:
        return YELLOW


def _wave_bar_color(fill: int, invert: bool = False) -> str:
    """Color for wave bar: green(calm) → yellow → red(dangerous)."""
    if fill <= 3:
        return BRIGHT_GREEN
    elif fill <= 5:
        return GREEN
    elif fill <= 7:
        return YELLOW
    else:
        return RED


def _danger_bar_color(fill: int, invert: bool = False) -> str:
    """Color for danger bars (wind, precip): green(low) → red(high)."""
    if fill <= 3:
        return BRIGHT_GREEN
    elif fill <= 5:
        return GREEN
    elif fill <= 7:
        return YELLOW
    else:
        return RED


def _uv_bar_color(fill: int, invert: bool = False) -> str:
    """Color for UV index bar."""
    if fill <= 2:
        return BRIGHT_GREEN
    elif fill <= 5:
        return GREEN
    elif fill <= 7:
        return YELLOW
    elif fill <= 10:
        return RED
    else:
        return BRIGHT_RED


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text for length calculation."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)
