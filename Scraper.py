import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime


def get_tide_data(station_id, start_date, end_date):
    """
    Fetches high/low tide predictions from the NOAA Tides and Currents API for a given station and date range.

    Args:
        station_id (str): The unique ID of the tide station.
        start_date (str): The start date in 'YYYYMMDD' format.
        end_date (str): The end date in 'YYYYMMDD' format.

    Returns:
        pd.DataFrame: A DataFrame containing the tide data, or an empty DataFrame if an error occurs.
    """
    # The base URL for the NOAA CO-OPS API for Data Retrieval
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    # Define the parameters for the API request
    params = {
        'product': 'predictions',  # Requesting tide predictions
        'station': station_id,
        'begin_date': start_date,
        'end_date': end_date,
        'datum': 'MLLW',  # Mean Lower Low Water, a common tidal datum
        'units': 'english',  # You can also use 'metric'
        'time_zone': 'lst_ldt',  # Local time, including daylight saving time
        'format': 'json',  # Requesting JSON format for easy parsing
        'application': 'tide-visualizer-script'  # Your application name
    }

    try:
        print(f"Fetching data for station ID: {station_id} from {start_date} to {end_date}...")
        # Make the GET request to the API
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the JSON response
        data = response.json()

        # Check if the 'predictions' key exists in the response
        if 'predictions' in data:
            predictions = data['predictions']
            # Create a DataFrame from the list of dictionaries
            df = pd.DataFrame(predictions)

            # Convert 't' (time) column to datetime objects
            df['t'] = pd.to_datetime(df['t'])

            # Convert 'v' (value) column to a numeric type
            df['v'] = pd.to_numeric(df['v'])

            print("Data successfully fetched and prepared.")
            return df
        else:
            print("No prediction data found in the API response. Check your parameters.")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from NOAA API: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


def plot_tide_data(df, station_name="Tide Station"):
    """
    Creates a line plot of tide levels over time.

    Args:
        df (pd.DataFrame): The DataFrame containing the tide data.
        station_name (str): The name of the station for the plot title.
    """
    if df.empty:
        print("Cannot plot an empty DataFrame.")
        return

    print("Generating plot...")
    plt.style.use('seaborn-v0_8-whitegrid')  # A professional and clean style for the plot

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df['t'], df['v'], color='royalblue', linewidth=2.5, label='Predicted Tide Height')

    # Add high and low tide markers
    # Find the local peaks and troughs in the data
    high_tides = df[df['v'] == df['v'].rolling(window=5, center=True).max()]
    low_tides = df[df['v'] == df['v'].rolling(window=5, center=True).min()]

    # Plot markers for high tides
    ax.scatter(high_tides['t'], high_tides['v'], color='red', s=100, zorder=5, label='High Tide')
    for _, row in high_tides.iterrows():
        ax.annotate(f"{row['v']:.2f} ft", (row['t'], row['v']), textcoords="offset points", xytext=(0, 10), ha='center',
                     fontsize=9)

    # Plot markers for low tides
    ax.scatter(low_tides['t'], low_tides['v'], color='green', s=100, zorder=5, label='Low Tide')
    for _, row in low_tides.iterrows():
        ax.annotate(f"{row['v']:.2f} ft", (row['t'], row['v']), textcoords="offset points", xytext=(0, -15),
                     ha='center', fontsize=9)

    # Set the title and labels
    ax.set_title(f'Tide Predictions for {station_name}', fontsize=20, pad=20)
    ax.set_xlabel('Date and Time (Local)', fontsize=14)
    ax.set_ylabel('Tide Height (feet)', fontsize=14)

    # Customize the x-axis for better readability
    plt.xticks(rotation=45, ha='right', fontsize=10)

    # Add a legend and grid
    ax.legend(loc='upper right', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Use tight_layout to ensure all labels and titles fit
    plt.tight_layout()
    plt.show()


# Main execution block
if __name__ == "__main__":
    # Define your station ID and date range here
    # You can find station IDs on the NOAA Tides and Currents website
    # Example: Station ID for Montauk, NY is 8510560
    my_station_id = '8510560'
    my_station_name = 'Montauk, NY'

    # Get today's date and the date for a week from now
    today = datetime.date.today()
    one_week_later = today + datetime.timedelta(days=7)

    # Format dates as required by the API
    start_date_str = today.strftime('%Y%m%d')
    end_date_str = one_week_later.strftime('%Y%m%d')

    # Get the tide data
    tide_df = get_tide_data(my_station_id, start_date_str, end_date_str)

    # Plot the data if the DataFrame is not empty
    if not tide_df.empty:
        plot_tide_data(tide_df, my_station_name)
    else:
        print("Data could not be retrieved. Please check your station ID and date range.")

