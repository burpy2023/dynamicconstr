import pandas as pd
from django.http import JsonResponse
from pathlib import Path

# load CSV once
CSV_PATH = Path(__file__).resolve().parent / 'ceiling-construction.csv'
df = pd.read_csv(CSV_PATH)

# these are your numeric columns in the CSV
NUMBER_COLUMNS = ['Extended Construction Numbers', 'Look-Up Construction Number']

def get_next_options(request):
    filtered = df.copy()

    # filter on every query-param
    for key, val in request.GET.items():
        if key in filtered.columns:
            filtered = filtered[filtered[key] == val]

    # build a list of columns to ask, skipping both number cols
    remaining = [
        col for col in df.columns
        if col not in request.GET
           and col not in NUMBER_COLUMNS
    ]

    # find the very next nonempty column
    while remaining:
        col = remaining.pop(0)
        opts = filtered[col].dropna().unique().tolist()
        if opts:
            return JsonResponse({'next': col, 'options': opts})

    # no more questions → return the Extended Construction Numbers
    if not filtered.empty:
        return JsonResponse({
            'next': None,
            'construction_number': filtered['Extended Construction Numbers'].iloc[0]
        })

    # nothing matched
    return JsonResponse({'next': None, 'construction_number': None})
