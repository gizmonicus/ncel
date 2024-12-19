#!/bin/env python
import re

import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

pd.set_option('display.min_rows', 20)
pd.set_option('display.max_rows', None)
def header_print(string):
    """Make a nice box around a single line of text"""
    print("\n+" + "-" * (len(string) + 2) + "+")
    print("| " + string + " |")
    print("+" + "-" * (len(string) + 2) + "+")

def convert_currency(value):
    """Converts a currency string to a float."""
    try:
        value = str(value)
        value = re.sub(r'[$,]', '', value)  # Remove '$' and commas
        return float(value)
    except (ValueError, TypeError):
        return None

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
        number = game.find(class_="gamenumber").text.split(':')[1].lstrip()

        # Start printing individual game information
        header_print("{} ({}) - ${:0.0f}".format(name, number, val))

        # Parse table data into a DataFrame
        df = pd.read_html(
            StringIO(str(game)),
            header=1,
            converters={'Value': convert_currency}
        )[0].dropna()

        # Calculate total number of tickets
        total_tickets = df.values[0][1] * df.values[0][2]  # Calculate total tickets

        # Calculate expected values
        oev = 0
        original_count = 0
        current_count = 0

        print("\nOriginal E[x]\n-------------")

        for row in df.values:
            e = row[0] / row[1]
            original_count += row[2]
            current_count += row[3]
            print("${:,.0f} (1:{:,.0f}) -> ${:.2f}".format(row[0],row[1],e))
            oev += e

        # Calculate extrapolated number of tickets remaining
        extrapolated_total = total_tickets * (current_count / original_count)

        # Calculate original expected value ratio
        odr = oev / val

        # Calculate the adjusted expected value based on remaining prizes.
        aev = 0

        print("\nAdjusted E[x]\n-------------")
        for row in df.values:
            e = row[0] * (row[3] / extrapolated_total)
            aev += e
            if row[3] == 0:
                print("${:,.0f} (INF) -> ${:.2f}".format(row[0],e))
            else:
                print("${:,.0f} (1:{:,.0f}) -> ${:.2f}".format(row[0],extrapolated_total / row[3],e))

        # Calculate the adjusted ratio
        adr = aev / val

        pc = aev / oev

        results.append({
            "Actual": "${:0.0f}".format(val),
            "Expected": "${:0.2f}".format(oev),
            "Ratio": "{:0.3f}".format(odr),
            "Adj. Expected": "${:0.2f}".format(aev),
            "Adj. Ratio": "{:0.3f}".format(adr),
            "% Chg.": "{:0.1f}%".format(pc * 100),
            "Printed": "{0:,.0f}".format(total_tickets),
            "% Left": "{:0.0f}%".format((extrapolated_total / total_tickets) * 100),
            "Name": "{} ({})".format(name,number)
        })

    header_print("Overall results sorted by best current ratio")
    res_df = pd.DataFrame(results).sort_values("Adj. Ratio", ascending=False)
    print(res_df)

if __name__ == "__main__":
    main()
