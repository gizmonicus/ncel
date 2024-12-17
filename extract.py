#!/bin/env python
import re

import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

pd.set_option('display.min_rows', 20)
pd.set_option('display.max_rows', None)
def header_print(string):
    """Make a nice box around a single line of text"""
    print("\n/" + "*" * (len(string) + 2) + "\\")
    print("| " + string + " |")
    print("\\" + "*" * (len(string) + 2) + "/\n")

def convert_currency(value):
    """Converts a currency string to a float."""
    try:
        value = str(value)
        value = re.sub(r'[$,]', '', value)  # Remove '$' and commas
        return float(value)
    except (ValueError, TypeError):
        return None

def calculate_expected_value(df):
    """Calculates the expected value from a DataFrame of lottery data."""
    ev = 0
    for row in df.values:
        ev += row[0] / row[1]
    return ev

def calculate_adjusted_expected_value(df, total_tickets):
    """Calculates the adjusted expected value based on remaining prizes."""
    aev = 0
    original_count = 0
    current_count = 0
    for row in df.values:
        original_count += row[2]
        current_count += row[3]

    extrapolated_total = total_tickets * (current_count / original_count)
    for row in df.values:
        aev += row[0] * (row[3] / extrapolated_total)
    return aev

def main():
    """Parses lottery data, calculates expected values, and prints results."""
    with open("lottery-main.html", "r") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")

    results = []
    for game in soup.find_all(class_=re.compile("box cloudfx databox price_.+")):
        # Extract ticket value and game name
        val = int(game['class'][3].split('_')[1])
        name = game.find(class_="gamename").text

        # Parse table data into a DataFrame
        df = pd.read_html(
            StringIO(str(game)),
            header=1,
            converters={'Value': convert_currency}
        )[0].dropna()

        # Calculate expected values
        oev = calculate_expected_value(df)
        odv = oev / val

        # Calculate adjusted expected value
        total_tickets = df.values[0][1] * df.values[0][2]  # Calculate total tickets
        aev = calculate_adjusted_expected_value(df, total_tickets)
        adv = aev / val

        results.append({
            "Actual": val,
            "Orig. Expected": oev,
            "Orig. Ratio": odv,
            "Adj. Expected": aev,
            "Adj. Ratio": adv,
            "Name": name
        })

    header_print("Just the data")
    res_df = pd.DataFrame(results)
    print(res_df)

    header_print("Sorted by best current ratio")
    res_df = pd.DataFrame(results).sort_values("Adj. Ratio", ascending=False)
    print(res_df)

    header_print("Sorted by best original ratio")
    res_df = pd.DataFrame(results).sort_values("Orig. Ratio", ascending=False)
    print(res_df)

    header_print("Sorted by highest expected value")
    res_df = pd.DataFrame(results).sort_values("Orig. Expected", ascending=False)
    print(res_df)

if __name__ == "__main__":
    main()
