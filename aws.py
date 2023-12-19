import base64
import datetime
import os

import boto3
from dash import html
from dash.exceptions import PreventUpdate

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION')
)
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION')
)
metadata_table = dynamodb.Table('WoodudFileUploadMetadata')


def upload_file_to_s3_logic(list_of_contents, list_of_names):
    if list_of_contents is None:
        raise PreventUpdate
    messages = []  # To store messages for each file upload
    for contents, filename in zip(list_of_contents, list_of_names):
        # Decode the file content from base64
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            # Upload the file to the S3 bucket
            s3_client.put_object(
                Bucket='woodud',
                Key=filename,
                Body=decoded
            )

            # Store metadata in DynamoDB
            metadata_table.put_item(
                Item={
                    'filename': filename,
                    'uploadTime': str(datetime.datetime.now()),
                    'user': 'user-identifier'  # You can modify this based on your app's user system
                }
            )

            messages.append(html.Div(f'Successfully uploaded {filename} to S3 and recorded metadata.'))
        except Exception as e:
            messages.append(html.Div(f'Failed to upload {filename}. Error: {e}'))
    return messages