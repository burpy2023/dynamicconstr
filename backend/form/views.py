import pandas as pd
from django.http import JsonResponse
from pathlib import Path
import logging

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
        if df.empty:
            return JsonResponse({'error': 'Internal server error.'}, status=500)

        # Start filtering
        filtered = df.copy()
        for key, val in request.GET.items():
            if key in df.columns:
                filtered = filtered[filtered[key] == val]
            else:
                return JsonResponse({'error': f"Invalid filter: {key}"}, status=400)

        # Build price_breakdown
        price_breakdown = {}
        for key, val in request.GET.items():
            subset = df[df[key] == val]
            if not subset.empty:
                try:
                    price_breakdown[key] = float(round(subset['Total Price'].iloc[0], 2))
                except Exception:
                    pass

        # Find next question
        remaining = [
            col for col in df.columns
            if col not in request.GET and col not in NUMBER_COLUMNS
        ]
        for col in remaining:
            # Drop NaNs, empty strings, and literal 'nan'
            raw = filtered[col].dropna().unique().tolist()
            opts = [o for o in raw if str(o).strip().lower() not in ('', 'nan')]
            if opts:
                return JsonResponse({
                    'next': col,
                    'options': opts,
                    'price_breakdown': price_breakdown
                }, status=200)

        # Final result
        if not filtered.empty:
            total = float(round(filtered['Total Price'].iloc[0], 2))
            return JsonResponse({
                'next': None,
                'construction_number': filtered['Extended Construction Numbers'].iloc[0],
                'price_breakdown': price_breakdown,
                'price': total,
            }, status=200)

        # No matches
        return JsonResponse({
            'next': None,
            'construction_number': None,
            'price': None,
            'price_breakdown': price_breakdown
        }, status=200)

    except Exception as e:
        logger.exception(f"Unexpected error in get_next_options: {e}")
        return JsonResponse({'error': 'Internal server error.'}, status=500)
