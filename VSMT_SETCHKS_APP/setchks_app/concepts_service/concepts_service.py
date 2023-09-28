"""Definition of interface class to database of concept_id, description_id, decription_term tuples"""

import os
import requests
import shutil
import glob
import json

import logging
logger=logging.getLogger()

from pymongo import MongoClient

from setchks_app.sct_versions import get_sct_versions
from . import pull_concepts_from_ontoserver

class ConceptsService():

    __slots__=["db"]

    def __init__(self):
        self.db=MongoClient()["concepts_service"]
        # self.db=MongoClient()["VSMT_uprot_app"]
    
    
    
    def get_list_of_releases_on_ontoserver(self):
        return [x.date_string for x in get_sct_versions.get_sct_versions()]
    
    def check_have_sct_version_collection_in_db(self, sct_version=None):
        collection_name=f"concepts_{sct_version}"
        return collection_name in self.db.list_collection_names()
    
    def make_missing_collections(self):
        existence_data=self.check_whether_releases_on_ontoserver_have_collections()
        for date_string, existence in existence_data.items():
            if not existence:
                print(f"==============\nMaking collection for {date_string}\n==============")
                self.create_collection_from_ontoserver(sct_version=date_string)
            else:
                print("==============\nCollection already exists for %s\n==============" % date_string)

    def check_whether_releases_on_ontoserver_have_collections(self):
        return_data={}
        for sct_version in self.get_list_of_releases_on_ontoserver():
            # print("%s : %s" % (sct_version, self.check_have_sct_version_collection_in_db(sct_version=sct_version)))
            return_data[sct_version]=self.check_have_sct_version_collection_in_db(sct_version=sct_version)
        return return_data
    
    # def get_data_about_description_id(self, description_id=None, sct_version=None):
    #     """ returns the information associated with a particular description id in a particular release"""
    #     collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
    #     data_found=list(self.db[collection_name].find({"desc_id":str(description_id)}))
    #     if data_found==[]:
    #         return None
    #     else:
    #         assert(len(data_found)==1)
    #         return data_found[0]
        
    # def get_data_about_concept_id(self, concept_id=None, sct_version=None):
    #     """ returns the information associated with a particular concept id in a particular release"""
    #     collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
    #     data_found=list(self.db[collection_name].find({"concept_id":str(concept_id)}))
    #     return data_found

    def create_collection_from_ontoserver(self, sct_version=None, delete_if_exists=False):
        sct_version=sct_version

        # NEED TO IMPLEMENT DELETE IF EXISTS

        root_id=138875005
        # root_id=280115004

        concepts=pull_concepts_from_ontoserver.download_limited_concept_data_from_ontoserver(
            sct_version=sct_version, 
            root_id=root_id,
            )

        pull_concepts_from_ontoserver.transitive_closure(root_id, concepts, {})

        for code, concept in concepts.items():
            concept['ancestors']=list(concept['ancestors'])
            concept['descendants']=list(concept['descendants'])

        db_collection=self.db['concepts_' + sct_version]

        n_documents_per_chunk=100000
        i_document=0
        documents=[]
        for code, concept in concepts.items():
            i_document+=1
            documents.append(concept)
            if i_document%n_documents_per_chunk==0:
                logger.debug("Have sent %s documents to mongodb" % i_document)
                db_collection.insert_many(documents)
                documents=[]
        db_collection.insert_many(documents) # insert any left in the last set
        logger.debug("Finished sending %s documents to mongodb" % i_document)
        logger.debug("Creating indexes..")
        db_collection.create_index("code", unique=False)
        logger.debug(".. finished creating indexes..")

        # for code, concept in concepts.items():
        #     populate_collection.add_concept_to_db(concept=concept, db_document=db_document)
