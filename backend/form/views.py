import pandas as pd
from django.http import JsonResponse
from pathlib import Path
import logging
import openai
import os

# logging
logger = logging.getLogger(__name__)

# load the CSV data once at module load
CSV_PATH = Path(__file__).resolve().parent / 'priced_ceiling_construction.csv'

try:
    # Read the CSV
    df = pd.read_csv(CSV_PATH)

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from all text columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    logger.info("Loaded and cleaned ceiling construction CSV successfully.")
except Exception as e:
    logger.error(f"Error loading CSV file: {e}")
    df = pd.DataFrame()

NUMBER_COLUMNS = [
    'Extended Construction Numbers',
    'Look-Up Construction Number',
    'Total Price'
]

def get_next_options(request):
    try:
        logger.info("Incoming request params: %s", request.GET.dict())

        if df.empty:
            logger.error("CSV data not loaded.")
            return JsonResponse({'error': 'Internal server error.'}, status=500)

        # filtering
        filtered = df.copy()
        for key, val in request.GET.items():
            if key in df.columns:
                logger.info("Trying to filter %s == %s", key, val)
                match_count = filtered[filtered[key] == val].shape[0]
                logger.info("Matches found: %d", match_count)
                filtered = filtered[filtered[key].str.contains(val, case=False, na=False)]

            else:
                logger.warning("Invalid filter key: %s", key)
                return JsonResponse({'error': f"Invalid filter: {key}"}, status=400)

        # Build price_breakdown
        price_breakdown = {}
        for key, val in request.GET.items():
            subset = df[df[key] == val]
            if not subset.empty:
                try:
                    price = float(round(subset['Total Price'].iloc[0], 2))
                    price_breakdown[key] = price
                    logger.info("Price for %s = %s is %.2f", key, val, price)
                except Exception as e:
                    logger.warning("Could not extract price for %s = %s: %s", key, val, e)

        # Find next question
        remaining = [
            col for col in df.columns
            if col not in request.GET and col not in NUMBER_COLUMNS
        ]
        logger.info("Remaining columns to ask: %s", remaining)

        for col in remaining:
            raw = filtered[col].dropna().unique().tolist()
            opts = [o for o in raw if str(o).strip().lower() not in ('', 'nan')]
            logger.info("Options for %s: %s", col, opts)

            if len(opts) > 0:
                return JsonResponse({
                    'next': col,
                    'options': opts,
                    'price_breakdown': price_breakdown
                }, status=200)

        # Final result
        if not filtered.empty:
            total = float(round(filtered['Total Price'].iloc[0], 2))
            logger.info("No more questions. Final price: %.2f", total)
            ai_fact = get_ai_tip(request.GET)
            return JsonResponse({
                'next': None,
                'construction_number': filtered['Extended Construction Numbers'].iloc[0],
                'price_breakdown': price_breakdown,
                'price': total,
                'ai_fact': ai_fact
            }, status=200)

        # No matches
        logger.warning("No matching data found after filtering.")
        return JsonResponse({
            'next': None,
            'construction_number': None,
            'price': None,
            'price_breakdown': price_breakdown
        }, status=200)

    except Exception as e:
        logger.exception("Unexpected error in get_next_options: %s", e)
        return JsonResponse({'error': 'Internal server error.'}, status=500)
    

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_tip(selections):
    prompt = f"The user selected:\n" + "\n".join(
        f"- {k}: {v}" for k, v in selections.items()
    ) + "\nGive a 1-sentence helpful tip related to this configuration."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message['content']
    except Exception as e:
        logger.warning(f"OpenAI error: {e}")
        return "No Expert tip available at the moment."
