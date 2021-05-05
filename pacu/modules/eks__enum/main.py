#!/usr/bin/env python3
import argparse
from botocore.exceptions import ClientError
import base64

module_info = {
    'name': 'eks_enum',
    'author': 'David Fentz',
    'category': 'ENUM',
    'one_liner': 'This module enumerates over EKS resources.',
    'description': 'This module enumerates over EKS resources.',
    'services': ['ECS'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


parser = argparse.ArgumentParser(add_help=False, description=module_info['description'])
parser.add_argument('--regions', required=False, default=None, help='One or more (comma separated) AWS regions in the format "us-east-1". Defaults to all session regions.')
parser.add_argument('--verbose', required=False, action='store_true', default=False, help='Enable verbose output')
parser.add_argument('--addons', required=False, action='store_true', default=False, help='Enumerate EKS addons')
parser.add_argument('--identity_provider_configs', required=False, action='store_true', default=False, help='Enumerate EKS identity provider configs')
parser.add_argument('--fargate_profiles', required=False, action='store_true', default=False, help='Enumerate EKS fargate profiles')

def build_summary_message(cluster_count):
    return f"Found {cluster_count} clusters in total.\nTo see EKS data, run \"data EKS\","

def main(args, pacu_main):
    args = parser.parse_args(args)
    print = pacu_main.print
    session = pacu_main.get_active_session()
    get_regions = pacu_main.get_regions
    data = {}
    cluster_count = 0

    if args.regions is None:
        regions = get_regions('eks')
        if regions is None or regions == [] or regions == '' or regions == {}:
            print('This module is not supported in any regions specified in the current sessions region set. Exiting...')
            return
    else:
        regions = args.regions.split(',')
    for region in regions:
        eks_client = pacu_main.get_boto3_client('eks', region)
        clusters = eks_client.list_clusters()["clusters"]
        print(f"clusters in {region}: {clusters}")
        if len(clusters) > 0:
            cluster_count += len(clusters)
            data[region] = {
            "clusters": []
            }
            for cluster in clusters:
                if args.verbose:
                    data[region]['clusters'].append({ 
                        "cluster_name": cluster,
                        "data": {
                        "cluster_description": eks_client.describe_cluster(name=cluster)["cluster"],
                        "nodegroups": eks_client.list_nodegroups(clusterName=cluster)["nodegroups"]
                        }
                    })
                    if args.addons:
                        data[region]['clusters'][cluster]['data']["addons"] = eks_client.list_addons(clusterName=cluster)["addons"]
                    if args.fargate_profiles:
                        data[region]['clusters'][cluster]['data']["fargate_profiles"] = eks_client.list_fargate_profiles(clusterName=cluster)["fargateProfileNames"]
                    if args.identity_provider_configs:
                        data[region]['clusters'][cluster]['data']["identity_provider_configs"] = eks_client.list_identity_provider_configs(clusterName=cluster)["identityProviderConfigs"]
                    # "addons": eks_client.list_addons(clusterName=cluster)["addons"]
                    # "fargate_profiles": eks_client.list_fargate_profiles(clusterName=cluster)["fargateProfileNames"]
                    # "identity_provider_configs": eks_client.list_identity_provider_configs(clusterName=cluster)["identityProviderConfigs"]
                else:
                    data[region]['clusters'].append({
                        "cluster_name": cluster,
                        "data": {
                        "nodegroups": eks_client.list_nodegroups(clusterName=cluster)['nodegroups']
                        }
                    })
                    # "addons": eks_client.list_addons(clusterName=cluster)["addons"],
                    # "fargate_profiles": eks_client.list_fargate_profiles(clusterName=cluster)["fargateProfileNames"],
                    # "identity_provider_configs": eks_client.list_identity_provider_configs(clusterName=cluster)["identityProviderConfigs"],
    session.update(pacu_main.database, EKS=data) 
    return build_summary_message(cluster_count)


def summary(data, pacu_main):
    return str(data)
