"""
Constants for swim-today: thresholds, ANSI codes, labels.
"""

# ── Verdict ──────────────────────────────────────────────────────────────────

YES = "YES"
MAYBE = "MAYBE"
NO = "NO"

# ── ANSI color codes ────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Foreground
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright foreground
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_CYAN = "\033[46m"

VERDICT_COLORS = {
    YES: BRIGHT_GREEN,
    MAYBE: BRIGHT_YELLOW,
    NO: BRIGHT_RED,
}

# ── Swim scoring thresholds ─────────────────────────────────────────────────

# Water temperature (°C) -- informational only, does not affect verdict
WATER_TEMP_LABELS = [
    (10, "Freezing", None),
    (15, "Very Cold", None),
    (18, "Cold", None),
    (20, "Cool", None),
    (24, "Mild", None),
    (27, "Comfortable", None),
    (30, "Warm", None),
    (35, "Very Warm", None),
    (float("inf"), "Hot", None),
]

# Wave height (meters)
WAVE_HEIGHT_LABELS = [
    (0.3, "Glassy", YES),
    (0.6, "Calm", YES),
    (1.0, "Slight", YES),
    (1.5, "Moderate", MAYBE),
    (2.0, "Rough", MAYBE),
    (3.0, "Very Rough", NO),
    (float("inf"), "Dangerous", NO),
]

# Wind speed (km/h)
WIND_SPEED_LABELS = [
    (10, "Calm", YES),
    (20, "Light Breeze", YES),
    (30, "Moderate", MAYBE),
    (40, "Strong", MAYBE),
    (50, "Very Strong", NO),
    (float("inf"), "Extreme", NO),
]

# UV index -- informational only, does not affect verdict
UV_INDEX_LABELS = [
    (2, "Low", None),
    (5, "Moderate", None),
    (7, "High", None),
    (10, "Very High", None),
    (float("inf"), "Extreme", None),
]

# Precipitation (mm/h)
PRECIP_LABELS = [
    (0.1, "None", YES),
    (2.0, "Light Rain", YES),
    (5.0, "Moderate Rain", MAYBE),
    (10.0, "Heavy Rain", NO),
    (float("inf"), "Torrential", NO),
]

# WMO Weather codes that indicate dangerous conditions
# See: https://open-meteo.com/en/docs
DANGEROUS_WEATHER_CODES = {
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}

WARNING_WEATHER_CODES = {
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
}

WMO_WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# ── Bar rendering ────────────────────────────────────────────────────────────

BAR_FILLED = "#"
BAR_EMPTY = "-"
BAR_LENGTH = 10

# ── Factor weights for overall score ────────────────────────────────────────

# Only safety factors drive the verdict (beach open/closed logic).
# Water temp and UV are informational -- they never close a beach.
SAFETY_FACTORS = {"wave_height", "wind_speed", "precipitation", "weather_code"}
