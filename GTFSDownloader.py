import pprint
import requests     # 2.18.4
import json         # 2.0.9
import pandas as pd # 0.23.0


def main(packages):


    # Make the HTTP request
    response = requests.get(packages)

    # Use the json module to load CKAN's response into a dictionary
    response_dict = json.loads(response.content)

    # Check the contents of the response
    assert response_dict['success'] is True  # make sure if response is OK


    # Specify the package you are interested in:
    package = 'soll-fahrplandaten-vrr'

    # Base url for package information. This is always the same.
    base_url = 'https://opendata.ruhr/api/3/action/package_show?id='

    # Construct the url for the package of interest
    package_information_url = base_url + package

    print(package_information_url)

    # Make the HTTP request
    package_information = requests.get(package_information_url)

    # Use the json module to load CKAN's response into a dictionary
    package_dict = json.loads(package_information.content)

    # Check the contents of the response.
    assert package_dict['success'] is True  # again make sure if response is OK
    package_dict = package_dict['result']  # we only need the 'result' part from the dictionary

    # Get the url for the data from the dictionary
    data_name = package_dict['resources'][-1]['name']
    print('Data url:     ' + data_name)

    data_url = package_dict['resources'][-1]['url']
    print('Data url:     ' + data_url)

    # Print the data format
    data_format = package_dict['resources'][-1]['format']
    print('Data format:  ' + data_format)



if __name__ == '__main__':
    packages = 'https://opendata.ruhr/api/3/action/package_list'
    print("start")
    main(packages)

