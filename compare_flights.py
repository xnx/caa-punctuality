import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 5000)

# The local directory in which the downloaded CSV files are saved.
DATA_DIR = Path("data")

# Get all data for dates 2022 – 2023.
years = range(2022, 2024)
csv_files = [f for year in years 
               for f in DATA_DIR.glob(f"{year}/{year}*.csv")]

# Read all the CSV data into a single DataFrame.
df = pd.concat(pd.read_csv(csv_file) for csv_file in csv_files)
print(f"{len(df)} rows read in.")

# Drop every row apart from scheduled (S) departures (D).
df = df[df['arrival_departure']=='D']
df = df[df['scheduled_charter']=='S']
# Drop rows if there are no matched flights for that month.
df = df[df['number_flights_matched']>0]
print(f"{len(df)} rows for scheduled departures.")

# Drop some columns we don't care about.
df.drop(["ï»¿run_date",
         "previous_year_month_flights_matched",
         "previous_year_month_early_to_15_mins_late_percent",
         "previous_year_month_average_delay",
        ], axis=1, inplace=True)

# Total number of flights for the whole data set.
print(df['number_flights_matched'].sum(), f"flights in data set.")

df['date'] = pd.to_datetime(df['reporting_period'], format="%Y%m")

df1 = df[(df["reporting_airport"]=="HEATHROW") & (df["origin_destination"]=="VIENNA")]
df1 = df1[["airline_name", "average_delay_mins"]]
df1 = df1.groupby("airline_name").mean()
print(df1)

df2 = df[(df["reporting_airport"]=="HEATHROW") & (df["origin_destination"]=="LOS ANGELES INTERNATIONAL")]
df2 = df2[["airline_name", "average_delay_mins"]]
df2 = df2.groupby("airline_name").mean()
print(df2)
