import requests
from datetime import datetime


def process_request(request_name, request_uri, timeout):
    try:
        start_time = datetime.now()
        resp = requests.get(request_uri, timeout=timeout)
        if resp.status_code == 200:
            print('{} request processed'.format(request_name))
            end_time = datetime.now()
            print('Duration: {}'.format(end_time - start_time))
            return resp
        else:
            print("Error: {} job response: {}".format(request_name, resp.status_code))
            return None
    except Exception as ex:
        print("{} job failed:".format(request_name))
        print(ex)
        return None
