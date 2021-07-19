import os
from datetime import datetime
from urllib.request import Request, urlopen
import boto3
import time
import requests
import xml.etree.ElementTree as ET

PHONE_NUMBER = os.environ['PHONE_NUMBER']  
AWS_KEY_ID = os.environ['AWS_KEY_ID'] 
AWS_SECRET = os.environ['AWS_SECRET']
RSS_LINK = os.environ['RSS_LINK']
REGION_NAME = os.environ['REGION_NAME']

LOCAL_FILE_URL = "/tmp/upwork_link_list.txt"
BUCKET_NAME = "upworknotifs"
S3_FILE_NAME = "upwork_link_list.txt"

def download_from_aws(local_file, bucket, s3_file):
    '''
    Downloads a file from S3 to /tmp
    '''
    
    s3 = boto3.client('s3', aws_access_key_id=AWS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET)

    try:
        s3.download_file(bucket,s3_file,local_file)
        print("Download Successful")
        return True
    except:

        # file was not found - in our case lets just write
        # an empty file to disk.
        with open(LOCAL_FILE_URL,'w') as f:
            f.write("")
        return True


def upload_to_aws(local_file, bucket, s3_file):
    '''
    Uploads a file to S3
    '''
    
    s3 = boto3.client('s3', aws_access_key_id=AWS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET)
    try:
        s3.upload_file(local_file, bucket, s3_file )
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("File upload not successful")
        return False




def send_sms(new_job_links):
    '''
    Sends out a text to the specified phone number
    through AWS SNS
    '''

    sns = boto3.client("sns", 
                       region_name=REGION_NAME, 
                       aws_access_key_id=AWS_KEY_ID, 
                       aws_secret_access_key=AWS_SECRET)


    # Send a single SMS (no topic, no subscription needed)
    for link in new_job_links:
        sns.publish(PhoneNumber=PHONE_NUMBER, 
                Message=link)




def watch_upwork():
    '''
    Queries upwork for the newest
    listings with some search terms and
    sends an sms notification if a new listing
    comes up compared to previous results
    '''

    # get the previous list of jobs on S3(empty if this is just the startup)
    response = download_from_aws(LOCAL_FILE_URL,BUCKET_NAME,S3_FILE_NAME)   
   
   
    if not response: 
        raise

    
    with open(LOCAL_FILE_URL,'r') as f:
        # file has comma delimiter
        current_jobs = f.read().split(",")
    
    # get previously watched items from S3
    response = requests.get(RSS_LINK)    
    refreshed_jobs = set([i.text for i in ET.fromstring(response.content).findall(".//link")])
    if len(refreshed_jobs.symmetric_difference(current_jobs)) > 0:

        print(refreshed_jobs)
        send_sms(refreshed_jobs.symmetric_difference(current_jobs))
        
        # refresh local copy of file
        with open(LOCAL_FILE_URL,'w') as f:
            # file has comma delimiter
            f.write(",".join(list(refreshed_jobs)))
        
        # upload new version of job links
        response = upload_to_aws(LOCAL_FILE_URL,BUCKET_NAME,S3_FILE_NAME)
        
        # in case the upload couldn't be done
        if not response:
            raise
        
    else:
        print("No new jobs found")

def lambda_handler(event, context):
    try:
        watch_upwork()
       
    except:
        print('Check failed!')
        raise
    else:
        print('Check passed!')
    finally:
        print('Check complete at {}'.format(str(datetime.now())))
