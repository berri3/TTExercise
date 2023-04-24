import requests
from datetime import datetime, timedelta
from http import HTTPStatus

# Probably not the best idea to hardcode API key in application code but oh well :)
API_KEY = "REDACTED"


def display_asteroid_information(start_date: str, end_date: str) -> None:
    """
    This function displays the name, ID, and close approach date of all asteroids which fall within
    the timeframe given by `start_date` and `end_date`.

    It calls NASA's NeoWs (Near Earth Object Web Service) RESTful web service
    https://api.nasa.gov/#:~:text=Object%20Web%20Service-,Asteroids%20%2D%20NeoWs,-NeoWs%20(Near%20Earth

    :param start_date: inclusive start date of the range we wish to query
    :param end_date: inclusive end date of the range we wish to query
    :return:
    """
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code == HTTPStatus.OK:
        # the returned data has two top-level elements: `links` and `near_earth_objects`
        # we will work with the latter
        data = response.json()
        near_earth_objects = data["near_earth_objects"]
        for date in near_earth_objects:
            print(f"---------- Asteroids approach date: {date} ----------")
            for asteroid in near_earth_objects[date]:
                print(" ---------- ")
                print(f"Name: {asteroid['name']}")
                print(f"ID: {asteroid['id']}")
                # it seems that `close_approach_data` is a list which only contains a single element
                # but just in case we will iterate through them
                for close_approach_data in asteroid["close_approach_data"]:
                    print(
                        f"Close approach date (full): {close_approach_data['close_approach_date_full']}")
            print()

    else:
        raise Exception(f"Error {response.status_code}: {response.reason}")


def display_asteroid_properties(start_date: str, end_date: str) -> None:
    """
    This function displays the following information for all asteroids which fall within
    the timeframe given by `start_date` and `end_date`.

    The velocity, in kilometers_per_second, of the fastest asteroid for the period.
    The velocity, in kilometers_per_second, of the slowest asteroid for the period
    The mean velocity (in kilometers_per_second) of all asteroids in the period.
    The median velocity (in kilometers_per_second) of all asteroids in the period.

    It calls NASA's NeoWs (Near Earth Object Web Service) RESTful web service
    https://api.nasa.gov/#:~:text=Object%20Web%20Service-,Asteroids%20%2D%20NeoWs,-NeoWs%20(Near%20Earth

    :param start_date: inclusive start date of the range we wish to query
    :param end_date: inclusive end date of the range we wish to query
    :return:
    """
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code == HTTPStatus.OK:
        data = response.json()
        near_earth_objects = data['near_earth_objects']

        velocities = []

        # we know that for each asteroid for a specific date, we can obtain its relative velocity.
        # we assume this is the value (in km/s) which we want to obtain the required info
        for date in near_earth_objects:
            for asteroid in near_earth_objects[date]:
                relative_velocity = float(asteroid['close_approach_data'][0]['relative_velocity']
                                          ['kilometers_per_second'])
                velocities.append(relative_velocity)

        fastest_velocity = max(velocities)
        slowest_velocity = min(velocities)

        # average velocity is the sum of all velocities divided by the magnitude
        mean_velocity = sum(velocities) / len(velocities)

        sorted_velocities = sorted(velocities)
        # to determine the median, we first determine if the velocities contain an even or
        # odd number of values
        if len(sorted_velocities) % 2 != 0:
            median_velocity = sorted_velocities[len(sorted_velocities) // 2]
        else:
            # in case of odd number of values, take the average of the two middle elements.
            median_velocity = (sorted_velocities[len(sorted_velocities) // 2] +
                               sorted_velocities[len(sorted_velocities) // 2 - 1]) / 2

        print(f'Fastest velocity: {fastest_velocity:.2f} kilometers_per_second')
        print(f'Slowest velocity: {slowest_velocity:.2f} kilometers_per_second')
        print(f'Mean velocity: {mean_velocity:.2f} kilometers_per_second')
        print(f'Median velocity: {median_velocity:.2f} kilometers_per_second')
    else:
        raise Exception(f"Error {response.status_code}: {response.reason}")


def display_recent_hazardous_asteroids() -> None:
    """
    This function makes uses of the NASA's NeoWs API to query the three most recent asteroids based
    on today's date and displays them if their `is_potentially_hazardous_asteroid` is set to true

    :return:
    """
    url = 'https://api.nasa.gov/neo/rest/v1/feed'

    # Set up start and end dates
    # We start by querying a single day, then incrementally add days if needed
    end_date = datetime.today()
    start_date = end_date - timedelta(days=1)

    hazardous_asteroids = []

    # Query data until we have at least 3 hazardous asteroids or if we're reach a full month
    while len(hazardous_asteroids) < 3 and start_date > end_date - timedelta(days=30):
        # Set up date range parameters
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        params = {'start_date': start_str, 'end_date': end_str, 'api_key': API_KEY}

        # Query the API
        response = requests.get(url, params=params)
        data = response.json()

        # Extract hazardous asteroids
        for date in data['near_earth_objects']:
            for asteroid in data['near_earth_objects'][date]:
                if asteroid['is_potentially_hazardous_asteroid']:
                    hazardous_asteroids.append((date, asteroid['name']))

            # Stop querying if we have 3 hazardous asteroids
            if len(hazardous_asteroids) >= 3:
                break

        # Move the date range back one day
        end_date -= timedelta(days=1)
        start_date -= timedelta(days=1)

    # Print the results
    print(f"The three most recent hazardous asteroids As of today {datetime.today().strftime('%Y-%m-%d')} are:")
    for date, name in hazardous_asteroids:
        print(f"{date}: {name}")


if __name__ == "__main__":
    # Q1: Retrieve and display the following information about asteroids with approach dates
    # between October 31st 2019 and November 2nd 2019 (inclusive):
    start_date_q1 = "2019-10-31"
    end_date_q1 = "2019-11-02"
    display_asteroid_information(start_date_q1, end_date_q1)

    # Q2: For asteroids with approach dates between
    # September 10th 2020 and September 17th 2020 (inclusive) calculate:
    start_date_q2 = "2020-09-10"
    end_date_q2 = "2020-09-17"
    display_asteroid_properties(start_date_q2, start_date_q2)

    # Q3: Find the three most recent asteroid approaches where the
    # is_potentially_hazardous_asteroid flag is set to true.
    display_recent_hazardous_asteroids()

