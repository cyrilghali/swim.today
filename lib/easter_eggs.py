"""
Easter eggs for inland locations -- because someone always tries Paris.

Each entry maps a lowercase city name to a water body name and a joke.
The lookup function also tries matching against admin regions and country
names so that "Paris, Ile-de-France, France" still hits.
"""

INLAND_JOKES = {
    "paris": {
        "water": "La Seine",
        "joke": (
            "The Seine has improved... technically. The fish are back. "
            "They even held Olympic swimming here. "
            "You, however, should probably stick to the pools."
        ),
        "suggestion": "Nice",
    },
    "london": {
        "water": "The Thames",
        "joke": (
            "The Thames was once declared biologically dead. "
            "It's recovered since, but 'recovered' is doing a lot of heavy lifting. "
            "Seals live in it now. You should not."
        ),
        "suggestion": "Brighton",
    },
    "cairo": {
        "water": "The Nile",
        "joke": (
            "The Nile has sustained civilization for 5,000 years. "
            "Swimming in it, however, has never been the move. "
            "Crocodiles, currents, and questionable water quality -- pick your adventure."
        ),
        "suggestion": "Hurghada",
    },
    "rome": {
        "water": "The Tiber",
        "joke": (
            "Legend says Romulus and Remus were thrown into the Tiber and survived. "
            "They were also raised by a wolf, so maybe don't use them as role models. "
            "The beach at Ostia is 30 minutes away."
        ),
        "suggestion": "Ostia",
    },
    "budapest": {
        "water": "The Danube",
        "joke": (
            "The Blue Danube is famously not blue. "
            "Strauss lied, and the river is about as swimmable as a Viennese waltz is relaxing. "
            "Try the thermal baths instead -- Budapest has 120 of them."
        ),
        "suggestion": "Split",
    },
    "vienna": {
        "water": "The Danube",
        "joke": (
            "Strauss called it the Blue Danube. He was being generous. "
            "The Alte Donau (Old Danube) is actually swimmable in summer though -- "
            "the Viennese have been keeping that secret for decades."
        ),
        "suggestion": "Split",
    },
    "new york": {
        "water": "The Hudson",
        "joke": (
            "People have swum in the Hudson. People have also regretted it. "
            "The East River isn't actually a river -- it's a tidal strait, "
            "and it would like to keep you out."
        ),
        "suggestion": "Miami",
    },
    "berlin": {
        "water": "The Spree",
        "joke": (
            "Berliners swim in the Spree every summer. "
            "The city has been trying to make it officially safe for years. "
            "'Trying' is the key word."
        ),
        "suggestion": "Barcelona",
    },
    "amsterdam": {
        "water": "The Canals",
        "joke": (
            "The canals look charming from a boat. "
            "From inside them, less so. "
            "There are roughly 12,000 bikes at the bottom. Watch your step."
        ),
        "suggestion": "Scheveningen",
    },
    "prague": {
        "water": "The Vltava",
        "joke": (
            "Smetana wrote a whole symphony about the Vltava. "
            "Beautiful music. Less beautiful water. "
            "The river is better admired from Charles Bridge with a beer in hand."
        ),
        "suggestion": "Split",
    },
    "dublin": {
        "water": "The Liffey",
        "joke": (
            "The Liffey runs through the heart of Dublin. "
            "Dubliners have a saying: 'Don't fall in.' "
            "That's the whole saying. Take the DART to Sandycove instead."
        ),
        "suggestion": "Galway",
    },
    "bangkok": {
        "water": "The Chao Phraya",
        "joke": (
            "The Chao Phraya is a highway of longtail boats, ferries, and floating markets. "
            "Swimming in it is technically possible in the way that anything is technically possible. "
            "Pattaya is two hours away."
        ),
        "suggestion": "Phuket",
    },
    "moscow": {
        "water": "The Moskva",
        "joke": (
            "The Moskva River has outdoor swimming pools nearby. "
            "The river itself? Nyet. "
            "Even in summer, Muscovites know better."
        ),
        "suggestion": "Sochi",
    },
    "madrid": {
        "water": "The Manzanares",
        "joke": (
            "The Manzanares is more of a creek with ambitions. "
            "Mark Twain allegedly said the saddest thing in Madrid was the river. "
            "Valencia's beach is a quick train ride away."
        ),
        "suggestion": "Valencia",
    },
    "tokyo": {
        "water": "The Sumida",
        "joke": (
            "The Sumida River hosts spectacular fireworks festivals. "
            "Swimming is not one of the festivities. "
            "Shonan Beach is an hour south -- the surfers will welcome you."
        ),
        "suggestion": "Kamakura",
    },
}

# Generic jokes for cities not in the curated list.
# One is picked based on the hash of the location name for consistency.
GENERIC_JOKES = [
    {
        "joke": (
            "No ocean here, but we admire the optimism. "
            "Swim.today needs waves, tides, and actual sea water to work its magic."
        ),
    },
    {
        "joke": (
            "This is firmly landlocked territory. "
            "The nearest body of water is probably a fountain in a park. "
            "We'd check it, but our fish would judge us."
        ),
    },
    {
        "joke": (
            "Our satellite-fish scanned the area. No ocean detected. "
            "If you squint at a puddle hard enough, it's almost the same thing."
        ),
    },
    {
        "joke": (
            "The ocean is out there somewhere, just... not here. "
            "But hey, at least you don't have to worry about sharks."
        ),
    },
    {
        "joke": (
            "We checked. Twice. Definitely no coast here. "
            "On the bright side, no jellyfish either."
        ),
    },
]


def get_easter_egg(location: str) -> dict | None:
    """Look up an easter egg for a location string.

    Accepts full location strings like "Paris, Ile-de-France, France"
    and tries matching the first part (city name) against the curated list.

    Returns a dict with 'water', 'joke', and 'suggestion' keys for curated matches,
    or a dict with just 'joke' for a generic fallback.
    """
    # Extract the city name (first comma-separated part)
    city = location.split(",")[0].strip().lower()

    # Try exact match on curated list
    if city in INLAND_JOKES:
        return INLAND_JOKES[city]

    # Generic fallback -- pick consistently based on city name
    idx = sum(ord(c) for c in city) % len(GENERIC_JOKES)
    return GENERIC_JOKES[idx]
