# aws python tools

## s3-upload-sts.py
This program does:
1. iam authenfication with credentials provided by env variable
2. assume a role to another aws account, retrieve temporary credentials
3. use these credentials to upload a file on a S3 bucket

```bash
AWS_ACCESS_KEY_ID="" \
AWS_SECRET_ACCESS_KEY="" \
BUCKET="" \
ROLEARN="arn:aws:iam::124356789:role/mysuperrole" \
python3 s3-upload-sts.py tmp/myfile
```
