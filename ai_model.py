import re

# All your keywords combined and normalized
KEYWORDS = [
    "gender mobility planning",
    "gender mainstreaming",
    "gender mainstreaming verkehrsplanung",
    "nachhaltige mobilität",
    "verkehrskonzept",
    "mobilitätskonzept",
    "integriertes handlungskonzept",
    "maßnahmenkonzept",
    "verkehrsmanagement",
    "verkehrssteuerung",
    "stadtentwicklung",
    "regionalplanung",
    "strukturwandel",
    "kfz-verkehr",
    "ruhender verkehr",
    "parkraummanagement",
    "parkraumkonzept",
    "parkleitsystem",
    "belegungsgrad",
    "stellplatzbilanz",
    "elektromobilität",
    "ladeinfrastruktur",
    "e-ladestationen",
    "mobilpunkte",
    "p+r",
    "b+r",
    "k+r",
    "öpnv",
    "spnv",
    "haltestellenqualität",
    "radverkehr",
    "radwegenetz",
    "fußverkehr",
    "nahmobilität",
    "schulwegsicherung",
    "barrierefreiheit",
    "güterverkehr",
    "lkw-verkehr",
    "verkehrsmodell",
    "transport planning",
    "mobility planning",
    "urban planning",
    "sustainable mobility",
    "infrastructure planning",
    "transport infrastructure",
    "consulting services",
    "planning services",
    "construction supervision"
]

def normalize(text):
    """Lowercase and remove accents for easier matching."""
    if not text:
        return ""
    text = text.lower()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def classify_tender(title, description=""):
    """True if ANY keyword appears in title or description."""
    text = normalize(title) + " " + normalize(description)

    for kw in KEYWORDS:
        kw_norm = normalize(kw)
        if kw_norm in text:
            return True

    return False

