from botocore import credentials
import boto3
from botocore.session import get_session
import os
import time
import datetime


def refresh_credentials():
    client = boto3.client('sts')
    cred = client.assume_role(
            RoleArn=roleArn,
            RoleSessionName="foo",
            DurationSeconds=3600
            ).get("Credentials")
    return {
            "access_key":   cred.get('AccessKeyId'),
            "secret_key":   cred.get('SecretAccessKey'),
            "token":        cred.get('SessionToken'),
            "expiry_time":  cred.get('Expiration').isoformat()
            }


if __name__ == "__main__":
    roleArn = os.environ['ROLEARN']
    bucket = os.environ['BUCKET']
    session_credentials = credentials.RefreshableCredentials.\
        create_from_metadata(
            metadata=refresh_credentials(),
            refresh_using=refresh_credentials,
            method="sts-assume-role")
    session = get_session()
    session._credentials = session_credentials
    autorefresh_session = boto3.Session(botocore_session=session)
    c = autorefresh_session.client('s3')
    while True:
        for key in c.list_objects(Bucket=bucket)['Contents']:
            now = datetime.datetime.now().replace(microsecond=0).isoformat()
            print(now + ": " + key['Key'])
        time.sleep(60)
