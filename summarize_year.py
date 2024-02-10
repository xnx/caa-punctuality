import sys
from pathlib import Path
import pandas as pd

year = sys.argv[1]

# The local directory in which the downloaded CSV files are saved.
DATA_DIR = Path("data")
csv_files = DATA_DIR.glob(f"{year}/*.csv")

# Read all the CSV data into a single DataFrame.
df = pd.concat(pd.read_csv(csv_file) for csv_file in csv_files)
print(f"{len(df)} rows read in.")

# Drop some columns we don't care about.
df.drop(["ï»¿run_date",
         "previous_year_month_flights_matched",
         "previous_year_month_early_to_15_mins_late_percent",
         "previous_year_month_average_delay",
        ], axis=1, inplace=True)

# Total number of flights reported for this year:
print(df['number_flights_matched'].sum(), f"flights in {year}")

# Analysis of flights handled by each UK airport:
grouped_by_airport = df.groupby("reporting_airport")
nflights_by_airport = grouped_by_airport[
        "number_flights_matched"].sum().sort_values()
print(nflights_by_airport)

busiest_airports = nflights_by_airport[nflights_by_airport >= 10000]
# Output the list of busiest airports in descending order of
# number of flights.
busiest_airports.iloc[::-1].to_csv('busiest_airports.txt', columns=[], header=False)

# Analysis of the number of flights operated by each airline:
grouped_by_airline = df.groupby("airline_name")
nflights_by_airline = grouped_by_airline [
        "number_flights_matched"].sum().sort_values()
print(nflights_by_airline)

biggest_airlines = nflights_by_airline[nflights_by_airline >= 1000]
# Output the list of biggest airlines in descending order of
# number of flights.
biggest_airlines.iloc[::-1].to_csv('biggest_airlines.txt', columns=[], header=False)

delay_by_airport = grouped_by_airport["average_delay_mins"].mean().sort_values()
delay_by_busy_airport = delay_by_airport[
        delay_by_airport.index.isin(busiest_airports.index)]
print(delay_by_busy_airport.iloc[::-1])

delay_by_airline = grouped_by_airline["average_delay_mins"].mean().sort_values()
delay_by_biggest_airline = delay_by_airline[
        delay_by_airline.index.isin(biggest_airlines.index)]
# To output more rows if necessary, use:
#pd.set_option('display.max_rows', 500)

# Output the top 20 most delayed airlines:
print(delay_by_biggest_airline.iloc[:-20:-1])


