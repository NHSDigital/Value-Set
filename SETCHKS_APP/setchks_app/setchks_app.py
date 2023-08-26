import os
import os.path
import sys

location=os.path.abspath(os.getcwd())
print(location)
sys.path.append(location+"/../VSMT_UPROT_APP/")

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils

import vsmt_uprot.terminology_server_module
import vsmt_uprot.vsmt_valueset
import vsmt_uprot.setchks.setchks_session
import vsmt_uprot.setchks.setchk_definitions 


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.exceptions import abort

bp = Blueprint('setchks_app', __name__)


from pymongo import MongoClient

# Consider this section again if and when hook up to mongodb
# if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
#     print("Configuring mongodb to connect to mongo-server docker")
#     client=MongoClient('mongo-server',27017)
# else:
#     print("Configuring mongodb to connect to localhost")
#     client=MongoClient()

# db=client['setchks_app']


################################
################################
# Simple health check endpoint #
################################
################################

@bp.route("/healthy")
def health_check():
    return "Healthy"

#####################################
#####################################
##     data upload endpoint        ##
#####################################
#####################################

@bp.route('/data_upload', methods=['GET','POST'])
def data_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 

    breadcrumb_styles={"data_upload":"strong", 
                       "upload_check":"weak", 
                       "columns_check":"weak",
                       "set_metadata":"weak",
                       "run_setchecks":"weak"}

    return render_template('data_upload.html',
                           file_data=setchks_session.data_as_matrix,
                           breadcrumb_styles=breadcrumb_styles,
                            )

#####################################
#####################################
##     confirm upload endpoint     ##
#####################################
#####################################


@bp.route('/confirm_upload', methods=['GET','POST'])
def confirm_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 

    # if reach here via file upload, load the data into matrix
    if 'uploaded_file' in request.files:
        setchks_session.load_data_into_matrix(data=request.files['uploaded_file'], upload_method='from_text_file', table_has_header=True)
        # print(setchks_session)
        session['setchks_session']=setchks_session # save updated setchks_session to the session variable
    else:
        pass

    breadcrumb_styles={"data_upload":"weak", 
                       "upload_check":"strong", 
                       "columns_check":"weak",
                       "set_metadata":"weak",
                       "run_setchecks":"weak",
                       }

    return render_template('confirm_upload.html',
                           file_data=setchks_session.data_as_matrix,
                           filename=setchks_session.filename,
                           breadcrumb_styles=breadcrumb_styles,
                            )

#####################################
#####################################
##    column identities endpoint   ##
#####################################
#####################################

@bp.route('/column_identities', methods=['GET','POST'])
def column_identities():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 

    breadcrumb_styles={"data_upload":"weak", 
                       "upload_check":"weak", 
                       "columns_check":"strong",
                       "set_metadata":"weak",
                       "run_setchecks":"weak",
                       }

    return render_template('column_identities.html',
                           file_data=setchks_session.data_as_matrix,
                           filename=setchks_session.filename,
                           breadcrumb_styles=breadcrumb_styles,
                            )
