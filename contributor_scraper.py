from datetime import date, timedelta
import pandas as pd
from datetime import datetime

# Timer
# ----------------------------------------------------------------------------
start_time = datetime.now()
print("Program start at {}".format(start_time))
timer = 0
# ----------------------------------------------------------------------------

start_date = date(2012, 1, 1)
end_date = date(2021, 12, 31)
delta = timedelta(days=1)


base_url = "https://osmstats.neis-one.org/?item=countries&date="
df = pd.read_csv('edits_per_country.csv') # Table of all the countries.
df['Total_Contributors'] = 0

# In order to get the total OSM per country over a time period, this code
# interates through each day between start_date and end_date goes to the respective
# url from osmstats.org. A cummulative daily sum is then created for the number of 
# contributors from each country. 
while start_date <= end_date:

    # Timer
    # ----------------------------------------------------------------------------
    if timer % 365 == 0:
        print(str(timer / 36.5) + "%")
        print("Time Elapsed: {}".format(datetime.now()-start_time))
    timer += 1
    # ----------------------------------------------------------------------------

    start_date += delta

    url_with_date = base_url + start_date.strftime("%d-%m-%Y")

    tables = pd.read_html(url_with_date)
    country_table = tables[0]
    df2 = pd.DataFrame(data=country_table)

    df2 = df2[['Country', 'Contributors']]

    # merge the two dataframes on the shared index column
    df = pd.merge(df, df2, on='Country', how='outer')
    df = df.fillna(0)

    df['Total_Contributors'] = df['Total_Contributors'] + df['Contributors']

    # drop the redundant columns
    df = df.drop(['Contributors'], axis=1)


df.to_csv('edits_per_country.csv', index=False)
print("All finished. Final time: {}".format(datetime.now()-start_time))