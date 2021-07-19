import boto3
import pandas as pd
import time
import requests
import xml.etree.ElementTree as ET


RSS_LINK = "https://www.upwork.com/ab/feed/jobs/rss?proposals=0-4%2C5-9&q=C%2B%2B&sort=recency&paging=0%3B10&api_params=1&securityToken=f160ff1404d69ab4e525aac0df57c1f1be77dd596f1575b82e66c5f80af4c1febcaf6aa7eac6fe3e1496a452504364c6464574b886519e5b7b93f0c3d31bcae4&userUid=842901675834527744&orgUid=842901675834527746"


def send_sms(new_job_links):
    '''
    Sends out a text to the specified phone number
    through AWS SNS

    '''
    AWS_KEY_ID = "AKIA2FBDENHD273W4LVU"
    AWS_SECRET = "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"

    sns = boto3.client("sns", 
                       region_name="eu-north-1", 
                       aws_access_key_id=AWS_KEY_ID, 
                       aws_secret_access_key=AWS_SECRET)


    # Send a single SMS (no topic, no subscription needed)
    for link in new_job_links:
        sns.publish(PhoneNumber="+36205825865", 
                Message=link)

    print("SMS sent")


def watch_upwork():
    '''
    Queries upwork every 2 seconds for the newest
    listings with some search terms and
    sends an sms notification if a new listing
    comes up
    '''



    # the list of jobs the script is aware of
    current_jobs = []

    # starting values
    response = requests.get(RSS_LINK)    
    current_jobs = set([i.text for i in ET.fromstring(response.content).findall(".//link")])

    while 1:

        response = requests.get(RSS_LINK)    
        refreshed_jobs = set([i.text for i in ET.fromstring(response.content).findall(".//link")])
        
        if len(refreshed_jobs.symmetric_difference(current_jobs)) > 0:

            print("Found new jobs!!")
            send_sms(refreshed_jobs.symmetric_difference(current_jobs))
            current_jobs = refreshed_jobs

        time.sleep(5)        

watch_upwork()
