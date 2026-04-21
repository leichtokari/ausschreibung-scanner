import re

###########################################
# 1. Keywords — 3 layers
###########################################

# Layer 1 — your exact domain terms (highest weight)
KEYWORDS_STRONG = [
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
    "haltestellenqualität",
    "radverkehr",
    "radwegenetz",
    "fußverkehr",
    "nahmobilität",
    "schulwegsicherung",
    "barrierefreiheit",
    "verkehrsmodell"
]

# Layer 2 — broader German transport infrastructure terms
KEYWORDS_GENERAL_DE = [
    "verkehr",
    "verkehrsplanung",
    "verkehrsanlagen",
    "verkehrsstudie",
    "verkehrssysteme",
    "verkehrsleitsystem",
    "mobilität",
    "öpnv",
    "spnv",
    "gutachten",
    "studie",
    "planungsleistung",
    "ingenieurleistung",
    "projektsteuerung",
    "bauüberwachung",
    "generalplanung",
    "infrastruktur",
    "straßenplanung"
]

# Layer 3 — EU/English domain terms
KEYWORDS_GENERAL_EN = [
    "transport",
    "mobility",
    "infrastructure",
    "public transport",
    "urban planning",
    "traffic planning",
    "transport modeling",
    "civil engineering",
    "consulting services",
    "planning services",
    "construction supervision"
]


###########################################
# Normalize text
###########################################
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    repl = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss"
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    return text


###########################################
# Smart scoring-based classifier
###########################################
def classify_tender(title, description=""):
    text = normalize(title + " " + description)

    score = 0

    # Strong matches (your exact domain)
    for kw in KEYWORDS_STRONG:
        if normalize(kw) in text:
            score += 50

    # German general mobility/verkehr
    for kw in KEYWORDS_GENERAL_DE:
        if normalize(kw) in text:
            score += 25

    # English general
    for kw in KEYWORDS_GENERAL_EN:
        if normalize(kw) in text:
            score += 15

    # Reward multiple hits
    score += text.count("verkehr") * 3
    score += text.count("mobil") * 3
    score += text.count("planung") * 3

    # Reward description presence
    if len(description) > 50:
        score += 10

    # Final decision
    return score >= 40
