import boto3
from botocore.exceptions import ClientError
import os
import sys

if __name__ == "__main__":
    bucket = os.environ['BUCKET']
    role_arn = os.environ['ROLEARN']
    myFile = sys.argv[1]
    mySession = boto3.Session()
    sts_connection = mySession.client('sts')
    assume_role_object = sts_connection.assume_role(
        RoleArn=role_arn, RoleSessionName='foo')
    tmpCred = assume_role_object['Credentials']
    s3Session = boto3.Session(aws_access_key_id=tmpCred['AccessKeyId'],
                              aws_secret_access_key=tmpCred['SecretAccessKey'],
                              aws_session_token=tmpCred['SessionToken'])
    print('Uploading %s to bucket s3://%s' % (myFile, bucket))
    c = s3Session.client('s3')
    try:
        c.upload_file(myFile,
                      bucket,
                      os.path.basename(myFile))
    except ClientError as e:
        print(e)
        sys.exit(1)
    print('Uploading %s successful' % (myFile))
