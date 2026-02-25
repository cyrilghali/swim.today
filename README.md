<div align="center">

<br>

```
                          ><>
            ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

# swim.today

_Can I swim today? Like [wttr.in](https://wttr.in), but for swimming._

<br>

[![License](https://img.shields.io/badge/license-MIT-0891b2?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-0891b2?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Powered by](https://img.shields.io/badge/data-Open--Meteo-0891b2?style=flat-square)](https://open-meteo.com)

</div>

<br>

```
$ curl swim.today/Hurghada

  ><>  Can I Swim Today?  Hurghada, Red Sea, Egypt  <><
  =========================================================

                 . o  O  o .
              o       . O  .  o
            ><)))'> ><)))'> ><)))'>
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
              Y  E  S  !    Go  swim!
         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Water Temp    28C       [########--]  Warm
  Wave Height   0.3m      [##--------]  Calm
  Wind Speed    12 km/h   [##--------]  Light Breeze
  UV Index      7.2       [#######---]  High
  Precip.       0.0 mm    [----------]  None
  Weather       Clear sky

  Beach is open. Go swim!

  * High UV. Wear sunscreen.

  ><>  swim.today | Powered by Open-Meteo  <><
```

<br>

```
          ><>          <><         ><>
   .  o    .     O   .    o  .        .  o
  ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

<br>

## ><> How it works

You give it a coastal city. It fetches **live marine + weather data**, scores the conditions, and tells you if it's safe to swim -- just like a lifeguard would.

```
                                         +-----------+
  curl swim.today/Bali  ──>  geocode  ──>| Open-Meteo|──>  score  ──>  YES / MAYBE / NO
                                         |  (marine) |
                                         |  (weather)|
                                         +-----------+
```

The verdict is driven by **safety factors** -- the same things that determine whether a beach flies a green, yellow, or red flag:

| Factor | YES | MAYBE | NO |
|:--|:--|:--|:--|
| Waves | < 1.0 m | 1.0 - 2.0 m | > 2.0 m |
| Wind | < 20 km/h | 20 - 40 km/h | > 40 km/h |
| Rain | < 2 mm | 2 - 5 mm | > 5 mm |
| Weather | Clear / Cloudy | Drizzle / Showers | Thunderstorm |

Water temperature and UV index are **informational** -- they never close a beach, but you'll get tips like _"Water is very cold. Consider a wetsuit."_ or _"Very high UV. Wear sunscreen SPF 50+."_

**Two yellow flags = red flag.** If two or more factors are MAYBE, the verdict escalates to NO.

<br>

```
   <><     ><>        }}>      <><
  ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

<br>

## ><> Usage

```bash
curl swim.today/Miami
curl swim.today/Barcelona
curl swim.today/Sharm+El+Sheikh
curl swim.today/Nice?format=json
curl swim.today/Sydney?format=short
```

Open in a browser for the HTML version with animated fish:

```
https://swim-today.fly.dev/Bali
```

<br>

## ><> Formats

| Parameter | Output | Example |
|:--|:--|:--|
| _(none, terminal)_ | ANSI-colored report | `curl swim.today/Dahab` |
| _(none, browser)_ | HTML with aquarium animation | visit in browser |
| `?format=json` | Structured JSON | `curl swim.today/Dahab?format=json` |
| `?format=short` | Single line | `curl swim.today/Dahab?format=short` |

**Short format** -- perfect for scripts and status bars:

```
$ curl swim.today/Dahab?format=short
Dahab, South Sinai, Egypt: YES  28C water  0.3m waves
```

**JSON format** -- for programmatic use:

```json
{
  "location": "Dahab, South Sinai, Egypt",
  "verdict": "YES",
  "summary": "Beach is open. Go swim!",
  "conditions": {
    "water_temp": 28.1,
    "wave_height": 0.3,
    "wind_speed": 12.4,
    "uv_index": 7.2,
    "precipitation": 0.0,
    "weather_code": 0
  },
  "factors": { ... },
  "tips": ["High UV. Wear sunscreen."]
}
```

<br>

```
    ><)))*>                          ><))'>
        .  o  .    O    .   o   .  O    .
  ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

<br>

## ><> Home page

The landing page shows **live conditions for 12 Egyptian coastal cities**, fetched in parallel:

```
$ curl swim.today

  ><>  swim.today  <><  -- Can I swim today?

  Egypt Coast          Water  Waves  Wind   Weather
  --------------------------------------------------------------
  YES   Hurghada           28C   0.3m   12km/h   Clear sky
  YES   Sharm El Sheikh    27C   0.2m    8km/h   Partly cloudy
  YES   Dahab              28C   0.3m   15km/h   Clear sky
  MAYBE Ain Sokhna         24C   1.2m   25km/h   Moderate rain
  NO    Alexandria         21C   2.5m   42km/h   Thunderstorm
  ...
  --------------------------------------------------------------

  Usage:  curl swim.today/Hurghada
          curl swim.today/Sharm+El+Sheikh
          curl swim.today/Dahab?format=json

  swim.today | Powered by Open-Meteo
```

<br>

## ><> Not coastal?

swim.today only works for coastal cities and beaches. If you try an inland location, it'll let you know:

```
$ curl swim.today/Paris

  ><>  Can I Swim Today?  Paris, Ile-de-France, France  <><

  <><  Paris, Ile-de-France, France is not near the coast.

  swim.today only works for coastal cities and beaches.
  Try one of these instead:

    curl swim.today/Miami
    curl swim.today/Barcelona
    curl swim.today/Sydney
    curl swim.today/Nice
```

<br>

```
  .   O  .  o   .  O  .    o   .  O   .  o
       ><>        <><       ><>       <><
  ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

<br>

## ><> Self-host

swim.today is a Flask app with a Dockerfile. No API keys needed -- all data comes from the free [Open-Meteo](https://open-meteo.com) APIs.

```bash
# Docker
docker build -t swim-today .
docker run -p 8000:8000 swim-today

# Local
pip install -r requirements.txt
python app.py
```

<br>

## ><> Deploy to Fly.io

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
fly launch
```

The included `fly.toml` and `Dockerfile` handle everything.

<br>

## ><> Tests

```bash
pip install pytest
pytest
```

<br>

## ><> Credits

All marine and weather data provided by [Open-Meteo](https://open-meteo.com) -- free, open-source weather APIs. No API key required.

<br>

## ><> License

[MIT](LICENSE)

<br>

---

<p align="center">

```
        .  o    .  O   .   o   .
   <><     ><>     <><     ><>     <><
  ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
```

_swim.today -- go swim._

</p>
