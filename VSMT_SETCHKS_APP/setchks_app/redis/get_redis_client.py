
import os
import json

import logging
logger=logging.getLogger()

from flask import current_app

import redis
import boto3

def get_elasticache_endpoint():
    client=boto3.client('elasticache')
    # propose:
    # env_tag=os.environ["WHATEVER"]
    env_tag=os.environ["ENV"]
    response=client.describe_replication_groups(ReplicationGroupId=f'vsmt-redis-replication-group-{env_tag}')
    # response=client.describe_replication_groups(ReplicationGroupId='vsmt-redis-replication-group')
    logger.debug(f"response={response}")
    endpoint=response['ReplicationGroups'][0]['NodeGroups'][0]['PrimaryEndpoint']['Address']
    return endpoint

def get_redis_string():
    if os.environ["DEPLOYMENT_ENV"]=="AWS":
        logger.debug("Configuring redis to connect to elsticache")
        endpoint=get_elasticache_endpoint()
        redis_string=f'rediss://{endpoint}:6379'
        logger.debug(f'redis_string={redis_string}')
    else:
        if "SETCHKS_APP_IN_DOCKER" in os.environ: # this env var must be set in docker-compose.yaml
            logger.debug("Configuring redis to connect to host.docker.internal")
            redis_string='redis://host.docker.internal:6379'
        else:
            logger.debug("Configuring redis to connect to localhost")
            redis_string='redis://localhost:6379'
        
    return redis_string

def get_redis_client():
    return redis.from_url(get_redis_string())