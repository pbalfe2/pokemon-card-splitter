from backend.services.filesystem import duplicate_as_card

async def split_cards(image_path: str, job_id: str):
    """
    MVP card splitter.
    Assumes one Pokémon card per image.
    Later upgrade: GPT-5.2 bounding boxes + cropping.
    """

    card_image_path = duplicate_as_card(image_path, job_id)

    return [
        {
            "card_image": card_image_path
        }
    ]
