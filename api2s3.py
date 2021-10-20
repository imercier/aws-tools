from boto3 import client
from time import time
from os import getenv
from json import dumps
import requests

if __name__ == "__main__":
    bucket = getenv('BUCKET')
    api_url = getenv('API_URL')
    timeout = getenv('TIMEOUT', 1)
    getTime = round(time() * 1000)
    response = requests.get(api_url, timeout=timeout)
    s3Save = {'time': getTime,
              'url': api_url,
              'responseCode': response.status_code}
    if response.ok:
        s3Save['responseData'] = response.json()
    else:
        s3Save['responseData'] = None
    s3 = client('s3')
    s3.put_object(
         Body=dumps(s3Save),
         Bucket=bucket,
         Key=str(getTime) + '.json')
