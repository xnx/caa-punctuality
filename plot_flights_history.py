import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# The local directory in which the downloaded CSV files are saved.
DATA_DIR = Path("data")

# Get all data for dates 2015 – 2023.
years = range(2015, 2024)
csv_files = [f for year in years for f in DATA_DIR.glob(f"{year}/{year}*.csv")]

# Read all the CSV data into a single DataFrame.
df = pd.concat(pd.read_csv(csv_file) for csv_file in csv_files)
print(f"{len(df)} rows read in.")

# Drop some columns we don't care about.
df.drop(
    [
        "ï»¿run_date",
        "previous_year_month_flights_matched",
        "previous_year_month_early_to_15_mins_late_percent",
        "previous_year_month_average_delay",
    ],
    axis=1,
    inplace=True,
)

# Total number of flights for the whole data set.
print(df["number_flights_matched"].sum(), f"flights in data set.")

df["date"] = pd.to_datetime(df["reporting_period"], format="%Y%m")

biggest_airlines = ["EASYJET UK LTD", "RYANAIR", "BRITISH AIRWAYS PLC"]

# Annoyingly, the way EasyJet is referred to changed in the
# data sets at some point.
df["airline_name"] = [
    "EASYJET UK LTD" if airline_name == "EASYJET AIRLINE COMPANY LTD"
                   else airline_name
    for airline_name in df["airline_name"]
]

df["airline_name"] = [
    airline_name if airline_name in biggest_airlines else "Other"
    for airline_name in df["airline_name"]
]
grouped_by_airline = df.groupby("airline_name")
nflights_by_airline = grouped_by_airline["number_flights_matched"].sum().sort_values()
print(nflights_by_airline)


# Colours to identify different airlines.
colours = {
    "Other": "#666666",
    "BRITISH AIRWAYS PLC": "#395b95",
    "EASYJET UK LTD": "#ec5f2a",
    "RYANAIR": "#d8ba4d",
}


##### Number of flights each month ######
grouped_by_month = df.groupby(["airline_name", "date"])
flights_per_month = grouped_by_month["number_flights_matched"].sum()

DPI = 100
WIDTH, HEIGHT = 1000, 800
fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI))
ax.set_axisbelow(True)

# To build a stacked bar chart, keep track of the height of the
# previous bars in the array last_values.
last_values = np.array(
    [0] * (len(flights_per_month.index) // (len(biggest_airlines) + 1))
)
for airline_name in ["Other"] + biggest_airlines:
    nflights = flights_per_month[airline_name].values
    ax.bar(
        flights_per_month[airline_name].index,
        nflights,
        bottom=last_values,
        width=20,
        fc=colours[airline_name],
        label=airline_name,
    )
    last_values += nflights
ax.xaxis_date()

yticks = np.arange(0, 201, 50)
ax.set_yticks(yticks * 1000)
ax.set_yticklabels([str(e) for e in yticks])
ax.set_ylabel("Number of flights (1000s)")
plt.legend(reverse=True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")
ax.spines["left"].set_visible(False)
ax.grid(axis="y", color="#cccccc", linewidth=1)
ax.yaxis.set_tick_params(length=0)
plt.savefig("flights_history.png", dpi=DPI)
plt.show()


##### Delay of flights each month #####
grouped_by_month = df.groupby(["airline_name", "date"])
delay_per_month = grouped_by_month["average_delay_mins"].mean()
average_delay_per_month = delay_per_month.groupby("date").mean()

DPI = 100
WIDTH, HEIGHT = 1000, 800
fig, ax = plt.subplots(figsize=(WIDTH / DPI, HEIGHT / DPI))
for airline_name in biggest_airlines:
    dates = delay_per_month[airline_name].index
    delay = delay_per_month[airline_name].values
    colour = colours[airline_name]
    ax.plot(
        dates,
        delay - average_delay_per_month,
        label=airline_name,
        lw=2,
        c=colour,
    )
plt.legend(reverse=True)
ax.set_ylabel("Delay - Average Delay (mins)")
plt.legend(reverse=True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")
ax.spines["left"].set_visible(False)
ax.grid(axis="y", color="#cccccc", linewidth=1)
ax.yaxis.set_tick_params(length=0)
plt.savefig("flight_delay_history.png", dpi=DPI)
plt.show()
