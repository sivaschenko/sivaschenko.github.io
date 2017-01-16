---
layout:     post
title:      AWS WAF bots and DDoS protection setup
date:       2017-02-10 08:30:06
summary:    Amazon Web Services Web Application Firewall bots and DDoS protection configuration ...
categories: aws,waf,elb,ddos,bots,python
---

# Approach Overview

Currently there are two Amazon Web Services (AWS) resources that can be protected by Web Application Firewall (WAF). These are CloudFront and Application Load Balancer (ELB).

The algorithm is the same for CloudFront and ELB:
 - **CloudFront** or **ELB** are saving access logs to **S3** bucket
 - Saving access log to **S3** bucket is triggering a **Lambda** function
 - **Lambda** function is analyzing access logs and managing IP lists blocked by **WAF** that is assigned to **CloudFront** or **ELB**
 
![CloudWatch or Application Load Balancer (ELB), S3 bucket, Lambda function and Web Application Firewall (WAF) bots and DDoS protection]({{ site.url }}/images/cloudwatch-elb-waf-s3-lambda-protection.png)

This apporach allows to block IPs based on access log analysis. The decision to block particular IPs based on access log information is a responsibility of Lambda script

# AWS resources

So here is a sequence of AWS resources that should be created (present):
 - **S3 bucket** for storing access logs and lambda function info
 - **WAF IP addresses condition** that will be updated by lambda function
 - **WAF rule** that match requests IPs against the condition
 - **WAF Web ACL** blocking requests based on the rule
 - **CloudFront** or **Application Load Balancer** that are saving access logs to the S3 bucket and have WAF Web ACL assigned
 - **IAM Role** for lambda function (providing access to S3 and WAF resources)
 - **Lambda function** responsible for parsing access logs and managing WAF IP Sets

Pay attention that all WAF resources should be created in the same region as Application Load Balancer or in global region, if you go with CloudFront.

# Step by step

For sure the fastest way to create any infrastructure in AWS is using CloudFormation template. However using CloudFormation will not help to learn and understand infrastructure. That's why I am providing manual setup steps.

# Lambda function

```python
import urllib
import boto3
import gzip
```

```python
IP_SET_ID = 'id_of_ip_set_to_add_ips'
REQUEST_LIMIT = 100
ACCESS_LOG_LINE_SEPARATOR = ' '
ACCESS_LOG_CLIENT_IP_PORT_POSITION = 3
```

```python
def process_event(event):
```

```python
    s3 = boto3.client('s3')
    waf = boto3.client('waf-regional')
```

```python
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
```


```python
    file = s3.download_file(bucket_name, file_name, '/tmp/' + file_name.split('/')[-1])
```


```python
    requests = {}

    with gzip.open(file, 'r') as content:
        for line in content:
            ip = line.split(ACCESS_LOG_LINE_SEPARATOR)[ACCESS_LOG_CLIENT_IP_PORT_POSITION].split(':')[0]

            if ip in requests.keys():
                requests[ip] += 1
            else:
                requests[ip] = 1
```


```python
    updates_list = []

    for ip, number_requests in requests:
        if number_requests > REQUEST_LIMIT:
            updates_list.append({
                'Action': 'INSERT',
                'IPSetDescriptor': {
                    'Type': 'IPV4',
                    'Value': "%s/32" % ip
                }
            })
```


```python
    waf.update_ip_set(
        IPSetId=IP_SET_ID,
        ChangeToken=waf.get_change_token()['ChangeToken'],
        Updates=updates_list
    )
```