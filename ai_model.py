def classify_tender(text):
    """
    Simple free AI filter based on keywords.
    """
    text = text.lower()

    keywords = [
        "transport",
        "consulting",
        "infrastructure",
        "planung",
        "engineering",
        "verkehr",
        "infrastruktur"
    ]

    return any(word in text for word in keywords)
