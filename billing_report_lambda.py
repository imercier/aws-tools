import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import os
from boto3.session import Session
import json

def jTree(jsonObject, id):
        return [obj for obj in jsonObject if obj['Id']==id][0]['Name']

def lambda_handler(event, context):
    now = datetime.utcnow()
    start = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    accountTree = json.loads(os.environ.get('ACCOUNT'))

    sts_connection = boto3.client('sts')
    stsConnection = sts_connection.assume_role(
        RoleArn=os.environ.get('STSROLEARN'),
        RoleSessionName="fooRoleSessionName",
        ExternalId=os.environ.get('STSEXTERNALID')
    )
    session = Session(aws_access_key_id=stsConnection['Credentials']['AccessKeyId'],
                  aws_secret_access_key=stsConnection['Credentials']['SecretAccessKey'],
                  aws_session_token=stsConnection['Credentials']['SessionToken'])

    costExlorerClient = session.client('ce')
    costType= 'BlendedCost'
    response = costExlorerClient.get_cost_and_usage(
            TimePeriod={'Start': start, 'End':  end},
            Granularity='DAILY', Metrics=[costType],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
            Filter={"Not": {"Dimensions": {"Key": "RECORD_TYPE","Values": ["Credit",]}}}
            )

    output = ''
    total = 0
    for result_by_time in response['ResultsByTime']:
        for group in result_by_time['Groups']:
            amount = float(group['Metrics']['BlendedCost']['Amount'])
            total += amount
            roundAmount = round(amount, 2)
            if roundAmount == 0:
                continue
            account = group['Keys'][0]
            accountName = jTree(accountTree['Accounts'], account)
            service = group['Keys'][1]
            output +=(account + "\t" + str(roundAmount) + "$\t" + service + "\t\t [" + accountName + "]\n")

    output += ("\nTotal blended cost (credits not deducted): " + str(round(total, 2)) + "$")

    total = 0
    response = costExlorerClient.get_cost_and_usage(
        TimePeriod={'Start': start, 'End':  end},
        Granularity='DAILY', Metrics=[costType],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}])
    for result_by_time in response['ResultsByTime']:
        for group in result_by_time['Groups']:
            amount = float(group['Metrics']['BlendedCost']['Amount'])
            total += amount
    output += ("\nTotal blended cost (credits deducted): " + str(round(total, 2)) + "$")

    SUBJECT = "[CloudLab] aws daily billing report " + start
    mailclient = boto3.client('ses', region_name=os.environ.get('AWS_REGION'))
    try:
        response = mailclient.send_email(
            Destination={
                'ToAddresses': os.environ.get('RECIPIENT').split(";")
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': output,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': SUBJECT,
                },
            },
            Source= os.environ.get('SENDER'),
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return -1
    else:
        return 0
