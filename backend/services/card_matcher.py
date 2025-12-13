def match_cards(fronts, backs):
    """
    MVP card matcher.
    Pairs front and back cards by index.

    fronts: list of dicts with key 'card_image'
    backs:  list of dicts with key 'card_image'
    """

    pairs = []

    count = min(len(fronts), len(backs))

    for i in range(count):
        pairs.append({
            "front": fronts[i]["card_image"],
            "back": backs[i]["card_image"]
        })

    return pairs
