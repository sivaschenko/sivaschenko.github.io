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
 - **WAF rule** that match requests IPs agains the condition
 - **WAF Web ACL** blocking reqests based on the rule
 - **CloudFront** or **Application Load Balancer** that are saving access logs to the S3 bucket and have WAF Web ACL assigned
 
Pay attention that all WAF resources should be created in the same region as Application Load Balancer or in global region, if you go with CloudFront.

# Step by step

Now you

# Lambda function



# Enable Access Logs

It is possible to create S3 bucket during elb access logs configuration. If you are going to create S3 bucket in advance, make sure to grant permissions for elb to save to that S3 bucket

Go to AWS Console
EC2
Load Balancing -> Load Balancers
Select Load balancer
Scroll Description tab down and find "Attributes" section.
Click "Configure Access Logs" button
Check Enable Access Logs checkbox
Enter unique name or S3 bucket
Check "Create S3 bucket" checkbox
Click Save button

After this you should see new S3 bucket containing AWSLogs dirctory (and a test file inside).

# Create WAF ACL