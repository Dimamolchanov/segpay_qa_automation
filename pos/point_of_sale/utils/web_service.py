import requests

def process_request(request_name, request_uri, timeout):
    try:
        resp = requests.get(request_uri, timeout=timeout)
        if resp.status_code == 200:
            print('{} request processed'.format(request_name))
            return resp
        else:
            print("Error: {} job response: {}".format(request_name, resp.status_code))
            return None
    except Exception as ex:
        print("{} job failed:".format(request_name))
        print(ex)
        return None
