import boto3
import json
import sys
import traceback

if len(sys.argv) != 2:
    print('USAGE: check_user_info.py path/to/config')
    exit()

endpoint_url = ''
users_table = ''

try:
    # Load data from config
    config = open(sys.argv[1])
    config_json = json.load(config)

    endpoint_url = config_json['dynamodb_endpoint']
    users_table = config_json['users_table']

    dynamodb = boto3.resource("dynamodb", region_name = "us-west-1", endpoint_url = endpoint_url)
    table = dynamodb.Table(users_table)

    # Get all users
    response = table.scan()
    users = response["Items"]

    # Print user id and last_pack_opened
    for user in users:
        print('User: ' + user['user_id'] + ', ' + user['last_pack_opened'])
except Exception as e:
    print(e)
    exit()
