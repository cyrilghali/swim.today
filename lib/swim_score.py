"""
Swim verdict engine: evaluates conditions and produces YES / MAYBE / NO.

The verdict models whether a beach would be open -- whether lifeguards
would let you in. Safety factors (waves, wind, storms, heavy rain) drive
the verdict. Water temperature and UV are informational only.
"""

from lib.constants import (
    YES, MAYBE, NO,
    WATER_TEMP_LABELS, WAVE_HEIGHT_LABELS, WIND_SPEED_LABELS,
    UV_INDEX_LABELS, PRECIP_LABELS,
    DANGEROUS_WEATHER_CODES, WARNING_WEATHER_CODES,
    WMO_WEATHER_DESCRIPTIONS,
    SAFETY_FACTORS,
)


def _classify(value, thresholds):
    """
    Classify a value using a list of (upper_bound, label, verdict) thresholds.
    Returns (label, verdict, ratio).
    """
    if value is None:
        return ("Unknown", None, 0.0)

    prev_bound = 0
    for upper, label, verdict in thresholds:
        if value < upper:
            bucket_range = upper - prev_bound if upper != float("inf") else 1
            ratio = min(1.0, max(0.0, (value - prev_bound) / bucket_range)) if bucket_range > 0 else 0
            return (label, verdict, ratio)
        prev_bound = upper

    last_label, last_verdict = thresholds[-1][1], thresholds[-1][2]
    return (last_label, last_verdict, 1.0)


def evaluate_conditions(marine: dict, weather: dict) -> dict:
    """
    Evaluate all swimming conditions and produce a verdict.

    Safety factors (affect verdict): wave height, wind, precipitation, weather code.
    Info factors (display only):     water temperature, UV index.
    """
    factors = {}
    tips = []

    # ── Water temperature (informational) ────────────────────────────────
    water_temp = marine.get("sea_surface_temp")
    wt_label, _, _ = _classify(water_temp, WATER_TEMP_LABELS)

    factors["water_temp"] = {
        "value": water_temp,
        "unit": "C",
        "label": wt_label,
        "verdict": None,       # never affects the overall verdict
        "bar": _temp_bar(water_temp) if water_temp is not None else 0,
    }

    if water_temp is not None:
        if water_temp < 15:
            tips.append("Water is very cold. Consider a wetsuit.")
        elif water_temp < 18:
            tips.append("Water is cold. A wetsuit may help.")

    # ── Wave height (SAFETY) ─────────────────────────────────────────────
    wave_height = marine.get("wave_height")
    wh_label, wh_verdict, _ = _classify(wave_height, WAVE_HEIGHT_LABELS)

    factors["wave_height"] = {
        "value": wave_height,
        "unit": "m",
        "label": wh_label,
        "verdict": wh_verdict,
        "bar": _wave_bar(wave_height) if wave_height is not None else 0,
    }

    if wave_height is not None:
        if wave_height >= 2.5:
            tips.append("Dangerous waves. Red flag conditions.")
        elif wave_height >= 1.5:
            tips.append("Rough waves. Experienced swimmers only.")

    # ── Wind speed (SAFETY) ──────────────────────────────────────────────
    wind_speed = weather.get("wind_speed")
    ws_label, ws_verdict, _ = _classify(wind_speed, WIND_SPEED_LABELS)

    factors["wind_speed"] = {
        "value": wind_speed,
        "unit": "km/h",
        "label": ws_label,
        "verdict": ws_verdict,
        "bar": _wind_bar(wind_speed) if wind_speed is not None else 0,
    }

    if wind_speed is not None and wind_speed >= 40:
        tips.append("Strong winds create dangerous rip currents.")

    # ── UV index (informational) ─────────────────────────────────────────
    uv_index = weather.get("uv_index")
    uv_label, _, _ = _classify(uv_index, UV_INDEX_LABELS)

    factors["uv_index"] = {
        "value": uv_index,
        "unit": "",
        "label": uv_label,
        "verdict": None,       # never affects the overall verdict
        "bar": min(10, int(uv_index)) if uv_index is not None else 0,
    }

    if uv_index is not None:
        if uv_index >= 8:
            tips.append("Very high UV. Wear sunscreen SPF 50+ and reapply often.")
        elif uv_index >= 6:
            tips.append("High UV. Wear sunscreen.")
        elif uv_index >= 3:
            tips.append("Moderate UV. Sunscreen recommended.")

    # ── Precipitation (SAFETY) ───────────────────────────────────────────
    precip = weather.get("precipitation", 0) or 0
    pr_label, pr_verdict, _ = _classify(precip, PRECIP_LABELS)

    factors["precipitation"] = {
        "value": precip,
        "unit": "mm",
        "label": pr_label,
        "verdict": pr_verdict,
        "bar": min(10, int(precip)),
    }

    # ── Weather code (SAFETY -- thunderstorms close beaches) ─────────────
    weather_code = weather.get("weather_code", 0) or 0
    wc_desc = WMO_WEATHER_DESCRIPTIONS.get(weather_code, "Unknown")

    if weather_code in DANGEROUS_WEATHER_CODES:
        wc_verdict = NO
        tips.append(f"Dangerous weather: {wc_desc}. Beach closed.")
    elif weather_code in WARNING_WEATHER_CODES:
        wc_verdict = MAYBE
    else:
        wc_verdict = YES

    factors["weather_code"] = {
        "value": weather_code,
        "unit": "",
        "label": wc_desc,
        "verdict": wc_verdict,
        "bar": 0,
    }

    # ── Overall verdict (safety factors only) ────────────────────────────
    verdict = _compute_verdict(factors)
    summary = _generate_summary(verdict, factors)

    return {
        "verdict": verdict,
        "factors": factors,
        "tips": tips,
        "summary": summary,
    }


def _compute_verdict(factors: dict) -> str:
    """
    Compute verdict from safety factors only.
    Water temp and UV are excluded -- they don't close beaches.
    """
    no_count = 0
    maybe_count = 0

    for key, factor in factors.items():
        if key not in SAFETY_FACTORS:
            continue
        v = factor.get("verdict")
        if v == NO:
            no_count += 1
        elif v == MAYBE:
            maybe_count += 1

    if no_count >= 1:
        return NO
    if maybe_count >= 2:
        return NO      # two yellow flags = red flag
    if maybe_count == 1:
        return MAYBE
    return YES


def _generate_summary(verdict: str, factors: dict) -> str:
    """Generate a human-readable summary sentence."""
    if verdict == YES:
        return "Beach is open. Go swim!"

    if verdict == MAYBE:
        issues = []
        for key in SAFETY_FACTORS:
            f = factors.get(key, {})
            if f.get("verdict") == MAYBE:
                issues.append(f["label"].lower() + " " + _factor_name(key))
        if issues:
            return f"Swim with caution: {', '.join(issues)}."
        return "Conditions are mixed. Swim with caution."

    # NO
    dangers = []
    for key in SAFETY_FACTORS:
        f = factors.get(key, {})
        if f.get("verdict") in (NO, MAYBE):
            dangers.append(f["label"].lower() + " " + _factor_name(key))
    if dangers:
        return f"Beach closed: {', '.join(dangers[:2])}."
    return "Not safe to swim."


def _factor_name(key: str) -> str:
    return {
        "wave_height": "waves",
        "wind_speed": "wind",
        "precipitation": "rain",
        "weather_code": "weather",
    }.get(key, key)


def _temp_bar(temp_c: float) -> int:
    """Map water temperature to bar fill (0-10)."""
    if temp_c < 10:
        return 1
    elif temp_c < 15:
        return 2
    elif temp_c < 18:
        return 3
    elif temp_c < 20:
        return 4
    elif temp_c < 22:
        return 5
    elif temp_c < 24:
        return 6
    elif temp_c < 26:
        return 7
    elif temp_c < 28:
        return 8
    elif temp_c < 30:
        return 9
    else:
        return 10


def _wave_bar(wave_m: float) -> int:
    """Map wave height to bar fill (0-10). Higher = worse."""
    if wave_m < 0.2:
        return 1
    elif wave_m < 0.4:
        return 2
    elif wave_m < 0.6:
        return 3
    elif wave_m < 0.8:
        return 4
    elif wave_m < 1.0:
        return 5
    elif wave_m < 1.5:
        return 6
    elif wave_m < 2.0:
        return 7
    elif wave_m < 2.5:
        return 8
    elif wave_m < 3.0:
        return 9
    else:
        return 10


def _wind_bar(wind_kmh: float) -> int:
    """Map wind speed to bar fill (0-10). Higher = worse."""
    return min(10, max(1, int(wind_kmh / 5)))
