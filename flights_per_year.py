from pathlib import Path
import glob
import pandas as pd

# The local directory in which the downloaded CSV files are saved.
DATA_DIR = Path("data")
csv_files = DATA_DIR.glob("*/*.csv")
csv_files = [DATA_DIR / f"{year}/{year}{month:02d}.csv" for month in range(1, 13) for year in range(2023, 2024)][:-1]

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
df['date'] = pd.to_datetime(df['reporting_period'], format="%Y%m")

grouped_by_month = df.groupby('reporting_period')
grouped_by_month = df.groupby('date')
flights_per_month = grouped_by_month['number_flights_matched'].sum()
print(flights_per_month)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.bar(flights_per_month.index, flights_per_month.values, width=20)
ax.xaxis_date()
plt.show()


