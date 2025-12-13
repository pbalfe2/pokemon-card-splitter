def normalize_condition(text: str):
    t = text.lower()

    if "mint" in t and "near" not in t:
        return "Mint"
    if "near" in t:
        return "Near Mint"
    if "light" in t:
        return "Lightly Played"
    if "moderate" in t:
        return "Moderately Played"
    if "heavy" in t:
        return "Heavily Played"

    return "Unknown"
