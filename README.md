# upwork-sms-notification

A simple script for AWS lambda that parses a custom RSS feed from Upwork, and sends you a text message using AWS SNS if there is a new job that pops up in your feed. 
You can get one by going to your jobs feed and adding some filters, like keywords, the clicking on the rss icon below the search bar.

To get this to work, you will need to set the env variables in the lambda function to your API keys, region names, the phone number you want to use, and the custom RSS feed you want to use.

All the lib dependencies should already be available in the default aws lambda function, but you can use the "canary" AWS lambda template to automatically set up a 1 minute cloudwatch trigger for your AWS lambda function.
