import os

from flask import Flask
import flask_session
import boto3
import json

import logging
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
logger=logging.getLogger(__name__)

from redis import from_url

from setchks_app.redis.get_redis_client import get_redis_string
from setchks_app.redis.rq_utils import (
    start_rq_worker_if_none_running, 
    kill_all_rq_workers,
    start_specific_rq_worker,
    )
    
def create_app():

    app = Flask(__name__, instance_relative_config=True)
    

    app.config["REDIS_STRING"]=get_redis_string()

    flask_session_type="redis" # "redis" or "mongodb"
    # flask_session_type="mongodb" # "redis" or "mongodb"

    if flask_session_type=="redis":
        import redis
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        redis_connection=from_url(app.config["REDIS_STRING"])
        app.config['SESSION_REDIS'] = redis_connection
        


    # get secrets if necessary (but why not test DEPLYOMENT_ENV?)
    logger.debug("About to see if need to get secrets")
    if 'ONTOSERVER_USERNAME' not in os.environ:

    # get CA file for DocumentDB (moved inside this block mar 25)) 
        import requests
        logger.debug(f'About to grab global-bundle-pem')
        r=requests.get("https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem")
        filename="/tmp/global-bundle.pem"
        ofh=open(filename,'w')
        byes_written=ofh.write(r.text)
        logger.debug(f'Wrote {byes_written} bytes to {filename}')

        logger.debug("getting secrets")
        sm_client = boto3.client('secretsmanager', region_name='eu-west-2')
        pw_response = sm_client.get_secret_value(SecretId='vsmt-ontoserver-access')
        passwords = pw_response['SecretString']
        dictionary_pw = json.loads(passwords)
        os.environ['ONTOSERVER_USERNAME']=dictionary_pw['ONTOSERVER_USERNAME']
        os.environ['ONTOSERVER_SECRET']=dictionary_pw['ONTOSERVER_SECRET']
        os.environ['TRUDAPIKEY']=dictionary_pw['TRUDAPIKEY']
        os.environ['DOCUMENTDB_USERNAME']=dictionary_pw['DOCUMENTDB_USERNAME']
        os.environ['DOCUMENTDB_PASSWORD']=dictionary_pw['DOCUMENTDB_PASSWORD']
        os.environ['COGNITO_CLIENT_ID']=dictionary_pw['COGNITO_CLIENT_ID']
        os.environ['COGNITO_CLIENT_SECRET']=dictionary_pw['COGNITO_CLIENT_SECRET']
        os.environ['FLASK_APP_SECRET']=dictionary_pw['FLASK_APP_SECRET']
        logger.debug("got secrets")
    else:
        logger.debug("no need to get secrets")

    app.secret_key = os.environ['FLASK_APP_SECRET']
    
    # these os.environ elements would need to be passed to an process running via redis queue
    # ['DEPLOYMENT_ENV', 'ONTOSERVER_INSTANCE', 'ONTOAUTH_INSTANCE', 'ONTOSERVER_USERNAME', 'ONTOSERVER_SECRET', 
    # 'TRUDAPIKEY', 
    # 'DOCUMENTDB_USERNAME', 'DOCUMENTDB_PASSWORD'] 

    if flask_session_type=="mongodb":   # STILL NEED TO CHANGE THIS IF WANT  ATTACH TO DOCUMENTDB!!!
        # currently requires pymngo <v4 see:
        # https://stackoverflow.com/questions/72025723/how-to-configure-mongodb-for-flask-session
        from pymongo import MongoClient
        print(app.config.keys())
        app.config['SESSION_TYPE'] = 'mongodb'
        app.config['SESSION_PERMANENT'] = True  # this seems to get round bug:
                                                # TypeError: '<=' not supported between instances of 'NoneType' and 'datetime.datetime'

        app.config['SESSION_USE_SIGNER'] = True
        if "SETCHKS_APP_IN_DOCKER" in os.environ: # this env var must be set in docker-compose.yaml
            print("Configuring mongodb to connect to mongo-server docker")
            app.config['SESSION_MONGODB']=MongoClient('host.docker.internal',27017) 
        else:
            print("Configuring mongodb to connect to localhost")
            app.config['SESSION_MONGODB']=MongoClient()

   
    kill_all_rq_workers()
    # start_rq_worker_if_none_running()
    start_specific_rq_worker(worker_name="worker_long_jobs")
    start_specific_rq_worker(worker_name="worker_short_jobs")

    server_session = flask_session.Session(app) # resets session variable behaviour so uses redis
    
    from . import setchks_app
    app.register_blueprint(setchks_app.bp)

    if "VERSION" in os.environ:
        app.config["VERSION"]=os.environ["VERSION"]
    else:
        app.config["VERSION"]="local"
    
    if os.environ["DEPLOYMENT_ENV"]=="AWS": # This is currently just used in a jinja template
                                            # I could not get the rest of the app to access it without a context error
        # app.config["ENVIRONMENT"]=os.environ["DEPLOYMENT_AWSENV"].upper()
        app.config["ENVIRONMENT"]=os.environ["ENV"].upper()
    else:
        app.config["ENVIRONMENT"]="LOCAL"
    return app

