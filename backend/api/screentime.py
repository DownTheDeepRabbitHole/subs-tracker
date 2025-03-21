import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO
import requests


def fetch_data(api_key, start_date, end_date):
    """
    Fetch RescueTime's summary data analytics from start_date and end_date.
    Dates is in YYYY-MM-DD form.
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

    # Format url with query params
    full_url = url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    response = requests.get(url, params=params)
    print(response.text)
    if response.ok:
        data = StringIO(response.text) # converts response character stream into a file-object
        df = pd.read_csv(data) # parses file as a csv dataframe

        # Preprocess data
        df["Date"] = pd.to_datetime(df["Date"]) # convert date strings to datetime type
        df = df.rename(columns={"Time Spent (seconds)": "Time"})
        df = df.groupby(["Date", "Activity"])["Time"].sum().reset_index() # merge duplicates
        df = df.pivot(index="Date", columns="Activity", values="Time") # organize by date
        df = df.fillna(0) # assume 0 for missing cells

        return df
    else:
        response.raise_for_status()

def _calculate_moving_average(data, window_size):
    """
    Calculates the moving average for a given list of data using a rolling window.
    """
    moving_averages = []
    current_sum = 0  # sum of the current window
    
    for i in range(len(data)):
        current_sum += data[i]
        
        # If boundary is hit, subtract the element that's leaving the window
        if i >= window_size:
            current_sum -= data[i - window_size]
        
        # Calculate the moving average (for windows that have full window size)
        moving_avg = current_sum / min(i + 1, window_size)  # adjust for the first few elements
        moving_averages.append(moving_avg)
    
    return moving_averages


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

    # Call to calculate the moving average with an internal method
    df[f"{subscription_name}_MA"] = _calculate_moving_average(df[subscription_name], window_size)

    # Get the most recent and older moving averages
    recent_ma = df[f"{subscription_name}_MA"].iloc[-1]  # most recent moving average
    older_ma = df[f"{subscription_name}_MA"].iloc[-trend_period]  # moving average for trend_period days ago

    # Calculate the base score (0 to 10) based on the moving average and threshold
    if recent_ma >= threshold:
        base_score = 10  # well above the threshold
    else:
        base_score = (recent_ma / threshold) * 10  # normalize to 0-10

    # Reduce score if the subscription is trending downward
    if recent_ma < older_ma * trend_threshold:
        penalty = (1 - (recent_ma / older_ma)) * 5  # deduct up to 5 points
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
