import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO
import requests


def fetch_data(api_key, start_date, end_date):
    """
    Fetch RescueTime's summary data analytics from start_date and end_date.
    Dates *should be* in YYYY-MM-DD form.
    """
    url = "https://www.rescuetime.com/anapi/data"
    params = {
        "key": api_key,
        "perspective": "interval",
        "resolution_time": "day",
        "restrict_begin": start_date,
        "restrict_end": end_date,
        "format": "csv",
    }

    full_url = url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    print(full_url)

    # https://stackoverflow.com/questions/32400867/pandas-read-csv-from-url
    response = requests.get(url, params=params)
    if response.ok:
        data = StringIO(response.text)

        df = pd.read_csv(data)
        # Preprocess data
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.rename(columns={"Time Spent (seconds)": "Time"})
        df = df.groupby(["Date", "Activity"])["Time"].sum().reset_index()
        df = df.pivot(index="Date", columns="Activity", values="Time")
        df = df.fillna(0)

        return df
    else:
        response.raise_for_status()

def calculate_usage(subscription_name, df, threshold=300, window_size=7, trend_period=14, trend_threshold=0.8):
    """
    Grades a subscription's usage from 1 to 10 based on screentime data.
    It analyzes usage patterns over time, including a moving average
    for more stable results and compares with trends in historical data to detect if it's downward.
    """

    if subscription_name not in df.columns:
        print(f"Warning: '{subscription_name}' not found in the data.")
        return 0
    
    if len(df) < trend_period:
        print(f"Warning: Not enough data to calculate the moving average for {subscription_name}.")
        return 0

    # Calculate the moving average using the rolling window
    df[f"{subscription_name}_MA"] = df[subscription_name].rolling(window=window_size, min_periods=1).mean()

    # Get the most recent and older moving averages
    recent_ma = df[f"{subscription_name}_MA"].iloc[-1]  # Most recent moving average
    older_ma = df[f"{subscription_name}_MA"].iloc[-trend_period]  # Moving average for trend_period days ago

    # Calculate the base score (0 to 10) based on the moving average and threshold
    if recent_ma >= threshold:
        base_score = 10  # Well above the threshold
    else:
        base_score = (recent_ma / threshold) * 10  # Normalize to 0-10

    # Reduce score if the subscription is trending downward
    if recent_ma < older_ma * trend_threshold:
        penalty = (1 - (recent_ma / older_ma)) * 5  # Deduct up to 5 points
        base_score -= penalty

    # Final clipping between 1 and 10
    usage_score = max(1, min(10, round(base_score)))
    
    return usage_score

def display_data(df): # Maintenance function: Plots usage data for all subscriptions
    plt.plot(df)
    plt.show()

def display_subscriptions(subscription_name, df): # Maintenance function: Plots usage data for one subscription
    if subscription_name in df.columns:
        # Use a dataframe with only subscription related column
        plot_df = df[[subscription_name, f"{subscription_name}_MA"]]

        # Plot the data
        plt.figure(figsize=(12, 6))
        plt.plot(
            plot_df.index,
            plot_df[subscription_name],
            label=f"{subscription_name} Usage",
        )
        plt.plot(
            plot_df.index,
            plot_df[f"{subscription_name}_MA"],
            label=f"{subscription_name} Moving Average",
            linestyle="--",
        )

        # Display title, legends, etc, etc.
        plt.title(f"Usage and Moving Average for {subscription_name}")
        plt.xlabel("Date")
        plt.ylabel("Time Spent (seconds)")
        plt.legend()
        plt.show()
    else:
        print(f"Warning: '{subscription_name}' not found in the data. Skipping plot.")
