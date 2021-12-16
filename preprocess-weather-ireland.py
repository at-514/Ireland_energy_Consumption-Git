#!/usr/bin/env python3
import pandas as pd
import sys

# Column names
COUNTY = "county"
STATION = "station"
DATE = "date"
RAIN = "rain"
TEMP = "temp"
TIME = "time"

# "h" - hourly.
# "D" - daily.
FREQ = "D"


def eprint(*args, **kwargs):
    # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)


def read(filename):
    """Read an Ireland weather csv data."""
    # https://stackoverflow.com/questions/24251219/pandas-read-csv-low-memory-and-dtype-options
    df = pd.read_csv(filename,
                     dtype={COUNTY: "string", STATION: "string", RAIN: float, TEMP: float},
                     parse_dates=[DATE],
                     na_values=' ')
    df.rename(columns={DATE: TIME}, inplace=True)
    return df


def print_missing_time(time, freq):
    """Print missing time."""
    # https://stackoverflow.com/questions/54039062/pandas-check-time-series-continuity
    s = pd.Series([1] * time.size, index=time).asfreq(freq=freq)
    s_null = pd.Series(s[s.isnull()].index)
    eprint("Missing dates:")
    eprint(s_null.to_string())
    eprint()


def is_valid():
    """Check if arguments are valid."""
    if len(sys.argv) != 3:
        eprint("Argument must be 2: The input and output files.")
        eprint("'./preprocess-weather-ireland.py input_file output_file'")
        eprint("e.g. './preprocess-weather-ireland.py hrly_Irish_weather.csv ireland-daily-weather.csv'")
        eprint()
        eprint("This script aggregates the given Ireland weather data into daily average.")
        eprint("Input file is an Ireland weather data from 'https://www.kaggle.com/conorrot/irish-weather-hourly-data'")
        return False
    return True


def read_args():
    """Read arguments. This function assumes that there are at least 3 command line arguments."""
    return sys.argv[1], sys.argv[2]


def to_hourly_average(df):
    """Aggregate to hourly average."""
    return df.groupby(TIME).mean()


def agg(df, freq):
    """Aggregate to a given frequency."""
    return df.groupby(pd.Grouper(freq=freq)).mean()


def print_missing_value(df):
    """Print rows with missing value."""

    # https://stackoverflow.com/questions/14247586/how-to-select-rows-with-one-or-more-nulls-from-a-pandas-dataframe-without-listin
    df_null = df[df.isnull().any(axis=1)]

    if df_null.empty:
        # No missing values.
        return

    eprint("Missing values:")
    eprint(df[df.isnull().any(axis=1)].to_markdown())
    eprint()


def to_csv(df, filename):
    """Print the given dataframe to a file. Floats are rounded to one decimal place."""
    df.to_csv(filename, float_format='%.1f')


def main():

    if not is_valid():
        return

    filename_in, filename_out = read_args()

    # Read csv.
    df = read(filename_in)

    # Convert to hourly. Then to daily.
    df_hourly = to_hourly_average(df)
    df_agg = agg(df_hourly, FREQ)

    # Print missing values if any.
    print_missing_value(df_agg)

    to_csv(df_agg, filename_out)


if __name__ == "__main__":
    main()
