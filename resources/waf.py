import urllib
import boto3
import gzip

IP_SET_ID = '367b0a8c-9b0d-4828-aa26-b6b53ec68bfb'
REQUEST_LIMIT = 100
ACCESS_LOG_LINE_SEPARATOR = ' '
ACCESS_LOG_CLIENT_IP_PORT_POSITION = 3

def process_event(event):

    s3 = boto3.client('s3')
    waf = boto3.client('waf-regional')

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    print ('Procession event from bucket %s, file: %s' % (bucket_name, file_name))

    file = s3.download_file(bucket_name, file_name, '/tmp/' + file_name.split('/')[-1])

    requests = {}

    with gzip.open(file, 'r') as content:
        for line in content:
            ip = line.split(ACCESS_LOG_LINE_SEPARATOR)[ACCESS_LOG_CLIENT_IP_PORT_POSITION].split(':')[0]

            if ip in requests.keys():
                requests[ip] += 1
            else:
                requests[ip] = 1

    updates_list = []

    for ip, number_requests in requests:
        if number_requests > REQUEST_LIMIT:
            print ('Adding %s to IP set. Requests number: %s' % (ip, number_requests))
            updates_list.append({
                'Action': 'INSERT',
                'IPSetDescriptor': {
                    'Type': 'IPV4',
                    'Value': "%s/32" % ip
                }
            })

    waf.update_ip_set(
        IPSetId=IP_SET_ID,
        ChangeToken=waf.get_change_token()['ChangeToken'],
        Updates=updates_list
    )