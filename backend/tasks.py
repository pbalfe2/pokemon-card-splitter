import asyncio
from backend.state import load_job, save_job
from backend.services.card_splitter import split_cards
from backend.services.card_matcher import match_cards
from backend.services.openai_vision import identify_card
from backend.services.condition_grader import grade_condition
from backend.services.condition_normalizer import normalize_condition
from backend.services.ebay_pricing import price_card


async def enqueue_job(job_id: str):
    asyncio.create_task(process(job_id))


async def process(job_id: str):
    try:
        job = load_job(job_id)
        job["status"] = "processing"
        save_job(job_id, job)

        fronts = await split_cards(job["front"], job_id)
        backs = await split_cards(job["back"], job_id) if job.get("back") else []

        pairs = match_cards(fronts, backs) if backs else [
            {"front": f["card_image"], "back": None} for f in fronts
        ]

        results = []

        for pair in pairs:
            card = {
                "identity": None,
                "condition": None,
                "price": None,
                "warnings": [],
                "errors": []
            }

            try:
                card["identity"] = await identify_card(
                    pair["front"], pair.get("back")
                )
            except Exception as e:
                card["errors"].append(str(e))

            try:
                raw_condition = await grade_condition(
                    pair["front"], pair.get("back")
                )
                card["condition"] = normalize_condition(raw_condition)
            except Exception as e:
                card["errors"].append(str(e))

            try:
                if card["identity"] and card["condition"]:
                    card["price"] = await price_card(
                        card["identity"], card["condition"]
                    )
            except Exception as e:
                card["errors"].append(str(e))

            results.append(card)

        job["status"] = "completed"
        job["cards"] = results
        save_job(job_id, job)

    except Exception as fatal:
        save_job(job_id, {"status": "failed", "error": str(fatal)})
