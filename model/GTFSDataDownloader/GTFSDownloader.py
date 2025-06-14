import requests
import json
from datetime import datetime
import json
from datetime import datetime
import requests


def main(packages):

    if packages == 'vrr':
        response = requests.get(packages)
        response_dict = json.loads(response.content)
        assert response_dict['success'] is True

        package = 'soll-fahrplandaten-vrr'
        base_url = 'https://opendata.ruhr/api/3/action/package_show?id='
        package_information_url = base_url + package
        print(package_information_url)

        package_information = requests.get(package_information_url)
        package_dict = json.loads(package_information.content)
        assert package_dict['success'] is True

        package_dict = package_dict['result']

        data_name = package_dict['resources'][-1]['name']
        print('Data url:     ' + data_name)

        data_url = package_dict['resources'][-1]['url']
        print('Data url:     ' + data_url)

        data_format = package_dict['resources'][-1]['format']
        print('Data format:  ' + data_format)

    elif 'vbb':
        url = 'https://vbb.de/vbbgtfs'
        r = requests.get(url, allow_redirects=True)

        now = datetime.now()
        now = now.strftime("%Y_%m_%d_%H_%M_%S")
        with open('C:/Tmp/VBB_{}_GTFS.zip'.format(now), 'wb') as file:
            file.write(r.content)


if __name__ == '__main__':
    packages = 'vbb'
    print("start")
    main(packages)

