#!/usr/bin/env python3
import argparse
import docker
from botocore.exceptions import ClientError
import base64
import subprocess32 as subprocess

module_info = {
    'name': 'my_module',
    'author': 'David Fentz',
    'category': 'ENUM',
    'one_liner': 'Does this thing.',
    'description': 'This module does this thing by using xyz and outputs info to abc. Here is a note also.',
    'services': ['ECS'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}

# Every module must include an ArgumentParser named "parser", even if it
# doesn't use any additional arguments.
parser = argparse.ArgumentParser(add_help=False, description=module_info['description'])

# The two add_argument calls are placeholders for arguments. Change as needed.
# Arguments that accept multiple options, such as --usernames, should be
# comma-separated. For example:
#     --usernames user_a,userb,UserC
# Arguments that are region-specific, such as --instance-ids, should use
# an @ symbol to separate the data and its region; for example:
#     --instance-ids 123@us-west-1,54252@us-east-1,9999@ap-south-1
# Make sure to add all arguments to module_info['arguments_to_autocomplete']
# parser.add_argument('', help='')
# parser.add_argument('', required=False, default=None, help='')


# Main is the first function that is called when this module is executed.
def main(args, pacu_main):
    pacu_main.update_regions() # apparently we can't trust pacu to run this on boot, seems odd. 
    session = pacu_main.get_active_session()

    
    print = pacu_main.print
    input = pacu_main.input
    key_info = pacu_main.key_info
    fetch_data = pacu_main.fetch_data
    get_regions = pacu_main.get_regions
    
    user = key_info()
    print(user)

    data = {}
    
    for region in pacu_main.get_regions('eks'):
        eks_client = pacu_main.get_boto3_client('eks', region)
        clusters = eks_client.list_clusters()["clusters"]
        print(f"clusters in {region}: {clusters}")
        
    
    data["summary"] = "all good!"
    return data


def summary(data, pacu_main):
    return str(data)
