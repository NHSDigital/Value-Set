
import sys

from fhir.resources.R4B.bundle import Bundle

########################
# parse_bundle_message #
########################

def parse_bundle_message(filename=None):
    if len(filename)>=6 and filename[-5:]==".json":
        file_type="json"
    elif len(filename)>=5 and filename[-4:]==".xml":
        file_type="xml"
    else:
        print("Unknown filetype: must be .json or .xml")
        sys.exit()

    string_data=open(filename).read()

    if file_type=="xml": # clean out whole line comments which seem to cause fhir.resources parser a problem
                        # comment line before the id line yields error about disallowed field id__ext
        cleaned_string_data_list=[]
        for line in string_data.split('\n'):
            if line.strip()[:4]!="<!--":
                cleaned_string_data_list.append(line)
        string_data="\n".join(cleaned_string_data_list)

    bundle=Bundle.parse_raw(string_data, content_type=file_type)

    resources_by_type={}
    resources_by_id={}
    for be in bundle.entry:
        r=be.resource
        r_type=r.resource_type
        if r_type not in resources_by_type:
            resources_by_type[r_type]=[]
        resources_by_type[r_type].append(r)
        resources_by_id[r.id]=r

    return resources_by_id, resources_by_type