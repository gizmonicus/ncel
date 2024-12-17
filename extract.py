#!/bin/env python
import pandas as pd
import re
from bs4 import BeautifulSoup
from io import StringIO
pd.set_option('display.min_rows', 20)

def convert_currency(value):
    try:
        value = str(value)
        value = re.sub(r'[$,]','', value)  # Remove $, €, and commas
        return float(value)
    except (ValueError, TypeError):
        return None  # Or handle the error as needed

with open("lottery-main.html","r") as f:

    html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    results = []

    for game in soup.find_all(class_=re.compile("box cloudfx databox price_.+")):

        # Get the value of the ticket from the class name
        val = int(game['class'][3].split('_')[1])

        # Lets get the game name for our output
        name = BeautifulSoup.find(game, class_="gamename").text

        print("N: {}, V: {}".format(name,val))

        df = pd.read_html(
            StringIO(str(game)),
            header=1,
            converters={
                'Value': convert_currency
            }
        )[0].dropna()

        print(df)

        # Calculate original expected value
        oev = 0
        for row in df.values:
            oev += row[0] / row[1]

        odv = oev / val

        # Calculate adjusted expected value

        # first we need the actual ticket counts. Multiply odds in 1 * total. We can just select the first row because they all
        # add up the same
        tot = df.values[0][1] * df.values[0][2]

        # Before we calculate the odds, we have to estimate how many tickets remain. We can estimate this from the number of prizes remaining of the total
        original_count = 0
        current_count = 0
        for row in df.values:
            original_count += row[2]
            current_count += row[3]

        extrapolated_total = tot * (current_count / original_count)        

        # Now we can get the expected value
        aev = 0

        for row in df.values:
            aev += row[0] * (row[3]/extrapolated_total)

        adv = aev / val

        results.append({"Actual": val, "Orig. Expected": oev, "Orig. Ratio": odv, "Adj. Expected": aev, "Adj. Ratio": adv, "Name": name})

    print("\n" + "#" * 50 + "\n")
    # Print the results

    print("---\nSorted by best current ratio\n---")
    res_df = pd.DataFrame(results).sort_values("Adj. Ratio", ascending=False)
    print(res_df)

    print("---\nSorted by best original ratio\n---")
    res_df = pd.DataFrame(results).sort_values("Orig. Ratio", ascending=False)
    print(res_df)

    print("---\nSorted by highest expected value\n---")
    res_df = pd.DataFrame(results).sort_values("Orig. Expected", ascending=False)
    print(res_df)
