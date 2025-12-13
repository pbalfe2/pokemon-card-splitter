import asyncio
from backend.state import load_job, save_job
from backend.services.card_splitter import split_cards
from backend.services.card_matcher import match_cards
from backend.services.openai_vision import identify_card
from backend.services.condition_grader import grade_condition
from backend.services.ebay_pricing import price_card


async def enqueue_job(job_id: str):
    """
    Enqueue a background processing task.
    Fire-and-forget, but internally guarded.
    """
    asyncio.create_task(process(job_id))


async def process(job_id: str):
    """
    Main processing pipeline:
    - Split cards
    - Match front/back
    - Identify card
    - Grade condition
    - Fetch eBay pricing
    - Persist results to job JSON

    This function NEVER raises uncaught exceptions.
    """

    try:
        job = load_job(job_id)
        job["status"] = "processing"
        save_job(job_id, job)

        # --- Split images into cards (MVP = 1 card) ---
        fronts = await split_cards(job["front"], job_id)
        backs = await split_cards(job["back"], job_id)

        pairs = match_cards(fronts, backs)
        results = []

        for idx, pair in enumerate(pairs, start=1):
            card_result = {
                "index": idx,
                "front": pair["front"],
                "back": pair["back"],
                "identity": None,
                "condition": None,
                "price": None,
                "errors": []
            }

            # --- Identify card ---
            try:
                card_result["identity"] = await identify_card(pair["front"])
            except Exception as e:
                card_result["errors"].append(
                    f"identify_card failed: {str(e)}"
                )

            # --- Grade condition ---
            try:
                card_result["condition"] = await grade_condition(
                    pair["front"], pair["back"]
                )
            except Exception as e:
                card_result["errors"].append(
                    f"grade_condition failed: {str(e)}"
                )

            # --- Price lookup ---
            try:
                if card_result["identity"] and card_result["condition"]:
                    card_result["price"] = await price_card(
                        card_result["identity"],
                        card_result["condition"]
                    )
                else:
                    card_result["price"] = {
                        "estimated_price": None,
                        "confidence": "unknown"
                    }
            except Exception as e:
                card_result["errors"].append(
                    f"price_card failed: {str(e)}"
                )

            results.append(card_result)

        # --- Finalize job ---
        job["status"] = "completed"
        job["cards"] = results
        save_job(job_id, job)

    except Exception as fatal:
        # Absolute last-resort safety net
        job = {
            "status": "failed",
            "error": str(fatal)
        }
        save_job(job_id, job)
