from pathlib import Path
import glob
import pandas as pd

# The local directory in which the downloaded CSV files are saved.
DATA_DIR = Path("data")
csv_files = DATA_DIR.glob("*/*.csv")
csv_files = DATA_DIR.glob("2020/*.csv")

# Read all the CSV data into a single DataFrame.
df = pd.concat(pd.read_csv(csv_file) for csv_file in csv_files)
print(f"{len(df)} rows read in.")

# Drop some columns we don't care about.
df.drop(["ï»¿run_date",
         "previous_year_month_flights_matched",
         "previous_year_month_early_to_15_mins_late_percent",
         "previous_year_month_average_delay",
        ], axis=1, inplace=True)
# Turn reporting_period (an integer: YYYYMM) into year and month
# columns:
df['month'] = df['reporting_period'] % 100
df['year'] = (df['reporting_period']  - df['month']) // 100

def get_monthly_delays(airline_name):
    df2 = df[df['airline_name']==airline_name]
    grouped_by_month = df2.groupby('month')
    print(grouped_by_month['average_delay_mins'].mean())
    print(grouped_by_month['number_flights_matched'].sum())

grouped_by_airline = df.groupby("airline_name")
airline_flights = grouped_by_airline["number_flights_matched"].sum()
airline_flights = airline_flights[airline_flights >= 10000]
#print(airline_flights)
#for i, e in airline_flights.items():
#    print(i, e)

df = df[df['airline_name'].isin(airline_flights.index)]
get_monthly_delays("BRITISH AIRWAYS PLC")
import sys; sys.exit()

grouped_by_airline = df.groupby("airline_name")
delay_by_airline = grouped_by_airline["average_delay_mins"].mean()
print(delay_by_airline)
print(delay_by_airline.mean())
print(df)
