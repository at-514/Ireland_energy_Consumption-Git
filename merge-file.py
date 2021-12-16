#!/usr/bin/env python3
from datetime import datetime
import sys
import numpy as np
import pandas as pd

# Column name
TIME = "time"


def eprint(*args, **kwargs):
    # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)


# Not used.
def read_electricity(filename):
    """Read an electricity csv data."""
    # https://stackoverflow.com/questions/17465045/can-pandas-automatically-recognize-dates
    def date_parser(x): return datetime.strptime(x, "%d-%m-%y")
    return pd.read_csv(filename, parse_dates=[TIME], date_parser=date_parser)


def read(filename):
    """Read a csv data and parse the 'time' column as dates."""
    return pd.read_csv(filename, parse_dates=[TIME])


def merge(df_electricity, df_weather):
    """Do an inner join on 'time' column."""
    # https://stackoverflow.com/questions/18792918/combine-two-pandas-data-frames-join-on-a-common-column
    return pd.merge(df_electricity, df_weather, on=TIME, how='inner')


def to_day_type(dt):
    """Get the day type info (weekday or weekend)."""
    # https://stackoverflow.com/questions/32278728/convert-dataframe-date-row-to-a-weekend-not-weekend-value
    return np.where(dt.dayofweek < 5, "weekday", "weekend")


def add_date_columns(df):
    """Add date-related columns."""

    # https://stackoverflow.com/questions/57767968/split-date-in-formatyyyy-mm-dd-into-3-new-columns-in-dataframe-as-year-month
    df["year"] = df[TIME].dt.year
    df["month"] = df[TIME].dt.month
    df["day"] = df[TIME].dt.day

    df["day_of_week"] = df[TIME].dt.dayofweek
    df["day_type"] = to_day_type(df[TIME].dt)


def is_valid():
    """Check if arguments are valid."""
    if len(sys.argv) != 4:
        eprint("Argument must be 3: The electricity, weather, and output file.")
        eprint("'./merge-file.py input_electricity_file input_weather_file output_file'")
        eprint(
            "e.g. './merge-file.py ireland-daily-electricity.csv ireland-daily-weather.csv ireland-merged.csv'")
        eprint()
        eprint("This script merges the given electricity and weather files (using their 'time' columns).")
        eprint("input_electricity_file date format must be in 'dd-mm-yy' e.g. '01-01-15'")
        return False
    return True


def read_args():
    """Read arguments. This function assumes that there are at least 4 command line arguments."""
    return sys.argv[1], sys.argv[2], sys.argv[3]


def to_csv(df, filename):
    """Print the given dataframe to a file. Floats are rounded to one decimal place."""
    df.to_csv(filename, float_format='%.1f', index=False)


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


def main():
    if not is_valid():
        return

    filename_electricity, filename_weather, filename_out = read_args()

    # Read the two csvs.
    df_electricity = read(filename_electricity)
    df_weather = read(filename_weather)

    df_merged = merge(df_electricity, df_weather)

    add_date_columns(df_merged)

    print_missing_value(df_merged)

    to_csv(df_merged, filename_out)


if __name__ == "__main__":
    main()
