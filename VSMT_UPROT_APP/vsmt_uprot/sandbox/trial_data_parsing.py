#!/usr/bin/env python
import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP/')

import vsmt_uprot.setchks.setchk_definitions 
from vsmt_uprot.setchks.setchks_session import SetchksSession
from vsmt_uprot.terminology_server_module import TerminologyServer

from vsmt_uprot.setchks.data_as_matrix.data_cell_contents import DataCellContents


setchks_session=SetchksSession()

###########################################################
#                                                         #
#  Set up connection to appropriate release in ontoserver #
#                                                         #
setchks_session.terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])
release_label="20230412"
setchks_session.sct_version="http://snomed.info/sct/83821000000107/version/" + release_label
#                                                         #
###########################################################


################################################
#                                              #
#  Load value set that checks should be run on #
#                                              #
fh=open('trial2.tsv')
setchks_session.load_data_into_matrix(data=fh, upload_method="from_text_file", table_has_header=True)
setchks_session.cid_col=0
#                                              #
################################################

print(setchks_session)
print("DCC:")
dcc=DataCellContents(cell_contents='1048521000000109')

print(dcc)