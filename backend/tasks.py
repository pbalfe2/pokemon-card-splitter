import asyncio
from backend.state import load_job, save_job
from backend.services.card_splitter import split_cards
from backend.services.card_matcher import match_cards
from backend.services.openai_vision import identify_card
from backend.services.condition_grader import grade_condition
from backend.services.ebay_pricing import price_card


async def enqueue_job(job_id):
    asyncio.create_task(process(job_id))

async def process(job_id):
    job = load_job(job_id)

    fronts = await split_cards(job["front"], job_id)
    backs = await split_cards(job["back"], job_id)

    pairs = match_cards(fronts, backs)
    cards = []

    for pair in pairs:
        identity = await identify_card(pair["front"])
        condition = await grade_condition(pair["front"], pair["back"])
        price = await price_card(identity, condition)

        cards.append({
            "identity": identity,
            "condition": condition,
            "price": price,
            "front": pair["front"],
            "back": pair["back"]
        })

    job["status"] = "completed"
    job["cards"] = cards
    save_job(job_id, job)
