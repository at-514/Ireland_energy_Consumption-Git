#!/usr/bin/env python3
import pandas as pd
import sys

START = "start"
END = "end"
TIME = "time"

# "h" - hourly.
# "D" - daily.
FREQ = "D"


def eprint(*args, **kwargs):
    # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)


def read(filename):
    """Read an electricity csv data."""
    # https://pandas.pydata.org/docs/getting_started/intro_tutorials/09_timeseries.html
    return pd.read_csv(filename, parse_dates=[START, END])


def print_missing_time(time, freq):
    """Print missing time."""
    # https://stackoverflow.com/questions/54039062/pandas-check-time-series-continuity
    s = pd.Series([1] * time.size, index=time).asfreq(freq=freq)
    s_null = pd.Series(s[s.isnull()].index)
    eprint("Missing dates:")
    eprint(s_null.to_string())
    eprint()


def print_interval(df):
    """Print the interval. Used to check if all the readings have uniform interval."""
    diff = df[END] - df[START]
    eprint("Start and end date interval(s): {}".format(diff.unique()))
    eprint()


def preprocess(df):
    """Remove timezone. Drop 'end' column. Set 'start' column as index. Name index as 'time'."""

    # https://stackoverflow.com/questions/49198068/how-to-remove-timezone-from-a-timestamp-column-in-a-pandas-dataframe
    df[START] = df[START].dt.tz_localize(None)

    df = df.drop(columns=END).set_index(START)
    df.index.name = TIME

    return df


def agg(df, freq):
    """Aggregate data to a given frequency."""
    # https://www.kaggle.com/francoisraucent/forecasting-hourly-electricity-consumption-of-ge
    return df.groupby(pd.Grouper(freq=freq)).mean()


def print_missing_value(df):
    """Print rows with missing value."""

    # https://stackoverflow.com/questions/14247586/how-to-select-rows-with-one-or-more-nulls-from-a-pandas-dataframe-without-listin
    df_null = df[df.isnull().any(axis=1)]

    if df_null.empty:
        return

    eprint("Missing values:")
    eprint(df[df.isnull().any(axis=1)].to_markdown())
    eprint()


def impute(df):
    # https://www.geeksforgeeks.org/python-pandas-dataframe-interpolate/
    # Use 'time', but since the measurement interval are equal, this is basically the same as 'linear'.
    # https://stackoverflow.com/questions/54985896/pandas-interpolate-time-vs-linear
    df_imputed = df.interpolate(method='time')
    return df_imputed


def to_csv(df, filename):
    """Print the given dataframe to a file. Floats are rounded to the nearest integer."""
    df.to_csv(filename, float_format='%.0f')


def is_valid():
    """Check if arguments are valid."""
    if len(sys.argv) != 3:
        eprint("Argument must be 2: The input and output files.")
        eprint("'./preprocess-electricity.py input_file output_file'")
        eprint("e.g. './preprocess-electricity.py Ireland.csv ireland-daily-electricity.csv'")
        eprint()
        eprint("This script aggregates the given electricity data into daily average.")
        eprint("Input file must be an electricity data from 'https://www.kaggle.com/francoisraucent/western-europe-power-consumption?select=de.csv'")
        eprint("This script assumes that the measurements in the input file have 30 minutes interval.")
        return False
    return True


def read_args():
    """Read arguments. This function assumes that there are at least 3 command line arguments."""
    return sys.argv[1], sys.argv[2]


def main():

    if not is_valid():
        return

    filename_in, filename_out = read_args()

    # Read csv and check for missing times.
    df = read(filename_in)
    print_missing_time(df[START], "30min")
    print_interval(df)

    # Convert to hourly and check for missing values.
    df_preprocessed = preprocess(df)
    df_agg = agg(df_preprocessed, FREQ)
    print_missing_value(df_agg)

    df_imputed = impute(df_agg)

    to_csv(df_imputed, filename_out)


if __name__ == "__main__":
    main()
