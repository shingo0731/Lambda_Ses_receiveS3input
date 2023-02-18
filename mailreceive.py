import boto3
import base64
import email
import urllib.parse
import json
from logging import getLogger, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    print("--------- logger.info の出力 ---------")
    logger.info(json.dumps(event))
    
    # S3のデータ取得
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    messageid = key.split("/")[1]
    
    try:
        response = s3.meta.client.get_object(Bucket=bucket, Key=key)
        email_body = response['Body'].read().decode('utf-8')
        email_object = email.message_from_string(email_body)

        #メールから添付ファイルを抜き出す
        for part in email_object.walk():
            print("maintype : " + part.get_content_maintype())
            if part.get_content_maintype() == 'multipart':
                continue
            # ファイル名の取得
            attach_fname = part.get_filename()
            print(attach_fname)

            # ファイルの場合
            if attach_fname:
                # fileに添付ファイルを保存する
                attach_data = part.get_payload(decode=True)
                bucket_source = s3.Bucket(bucket)
                bucket_source.put_object(ACL='private', Body=attach_data,
                                         Key='file' + "/" + attach_fname, ContentType='text/plain')

        return 'end'
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e