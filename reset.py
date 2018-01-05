from logdna import LogDNAHandler

import boto3
import json
import logging
import sys
import traceback

# 2017-12-23 21:25:31.998380

# Check if path to config and new time provided
if len(sys.argv) != 4:
    print('USAGE: reset.py path/to/config YYYY-MM-DD HH:MM:SS.SSSSSS')
    exit()

ingestion_key = ''
hostname = ''
endpoint_url = ''
users_table = ''

# Load data from config
try:
    config = open(sys.argv[1])
    config_json = json.load(config)

    ingestion_key = config_json['ingestion_key']
    hostname = config_json['hostname']
    endpoint_url = config_json['dynamodb_endpoint']
    users_table = config_json['users_table']
except Exception as e:
    print(e)
    exit()

# Set up logging to LogDNA
log = logging.getLogger('logdna')
log.setLevel(logging.INFO)
options = {
    'app': 'Discord Gacha Reset',
    'hostname': hostname,
    'index_meta': True
}
handler = LogDNAHandler(ingestion_key, options)
log.addHandler(handler)

# Also log to stdout
log.addHandler(logging.StreamHandler())

# Reset all last_pack_opened to the specified time
new_time = sys.argv[2] + ' ' + sys.argv[3]

try:
    dynamodb = boto3.resource("dynamodb", region_name = "us-west-1", endpoint_url = endpoint_url)
    table = dynamodb.Table(users_table)

    # Get all users
    response = table.scan()
    users = response["Items"]

    # Replace all users' last pull time and re add to database
    for user in users:
        user["last_pack_opened"] = new_time
        table.put_item(Item=user)

        meta = {
            'id': user['user_id'],
        }
        log.info('Changed draw time for ' + user['user_id'], { 'meta': meta })
except Exception as e:
    meta = {
        'message': str(e),
        'stacktrace': traceback.format_exc()
    }
    log.info('Unable to reset draw time', { 'level': 'Error', 'meta': meta })
    exit()
