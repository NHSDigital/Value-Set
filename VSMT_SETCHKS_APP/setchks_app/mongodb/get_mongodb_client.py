""" make mongodb connection according to whether LOCAL, AWS etc """

import os

import json
import boto3

from flask import current_app

import logging
logger=logging.getLogger()

from pymongo import MongoClient

def get_documentdb_endpoint():
    client=boto3.client('docdb')
    env_tag=os.environ["ENV"]
    response=client.describe_db_clusters(DBClusterIdentifier=f'vsmt-docdb-cluster-{env_tag}')
    # response=client.describe_db_clusters(DBClusterIdentifier='vsmt-docdb-cluster')
    logger.debug(f"response={response}")
    endpoint=response['DBClusters'][0]['Endpoint']
    return endpoint

def get_mongodb_client():
    logger.debug("Getting mongodb client..")
    if os.environ["DEPLOYMENT_ENV"]=="AWS":
        logger.debug("Configuring mongodb to connect to DocumentDB")
        endpoint=get_documentdb_endpoint()
        url_root=f'mongodb://{os.environ["DOCUMENTDB_USERNAME"]}:{os.environ["DOCUMENTDB_PASSWORD"]}@{endpoint}:27017/'
        arguments='?tls=true&tlsCAFile=/tmp/global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
        connection_string=url_root+arguments
        logger.debug(f"Connection string to mongodb is {connection_string}")
        mongodb_client=MongoClient(connection_string)
    else:
        if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
            # Test for if WSL (above) comes from 
            # https://superuser.com/questions/1749781/how-can-i-check-if-the-environment-is-wsl-from-a-shell-script
            # Also for bits below follwed everything in: 
            # https://github.com/microsoft/WSL/issues/5486 sylvix Mar 31 2021:
            # """Yet another solution, more in one place:
            # While installing MongoDB on Windows, make sure you enable Windows service, otherwise you'll have to run it manually.
            # After installation edit mongod.cfg and set bindIp to 0.0.0.0 (see previous post by @MKrupauskas, thank you, BTW)
            # Go to Firewall and Network protection in Windows settings (Start -> type "Firewall" -> Enter)
            # Click "Allow an app through firewall" link in bottom part of the window
            # Click "Change settings", then button "Allow another app" will be enabled. Click it. Browse for "mongod.exe" executable (in %Program Files%\MongoDB\Server\X.Y\bin. Then click "Network types" and select both types. Then click "Add".
            # It will add a set of rules to Defender Firewall that didn't work for some reason when added manually.
            # In WSL find host IP. On my machine cat /etc/resolv.conf works, after "nameserver" part. Or google for "wsl find host ip" there are plenty of solutions there.
            # mongo %INSERT_HOST_IP_HERE%"""
            IP_HOST=open('/etc/resolv.conf').readlines()[-1].split()[1]
            logger.debug(f"Configuring mongodb to connect from WSL2 to {IP_HOST}")
            mongodb_client=MongoClient(f'mongodb://{IP_HOST}:27017/')
        else:
            if "SETCHKS_APP_IN_DOCKER" in os.environ: # this env var must be set in docker-compose.yaml
                logger.debug("Configuring mongodb to connect to host.docker.internal")
                mongodb_client=MongoClient('host.docker.internal',27017)
            else:
                logger.debug("Configuring mongodb to connect to localhost")
                mongodb_client=MongoClient()   
    return mongodb_client