"""
This module instantiates a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier

"""

from .setchk import Setchk
from .individual_setchk_functions import CHK01_APPROP_SCTID
from .individual_setchk_functions import CHK02_IDS_IN_RELEASE
from .individual_setchk_functions import CHK04_INACTIVES_ENTRY
from .individual_setchk_functions import CHK05_UNRECC_HIERARCH
from .individual_setchk_functions import CHK06_DEF_EXCL_FILTER
from .individual_setchk_functions import CHK10_MISSING_CONCEPTS
from .individual_setchk_functions import CHK14_MANY_CLAUSES
from .individual_setchk_functions import CHK20_INCORR_FMT_SCTID

setchks={}


# there is a lot of repetition below so this can probably be generalised into a loop in due course
# once naming conventions in various parts of the code have bedded in

setchks['CHK01_APPROP_SCTID']=Setchk(
    setchk_code='CHK01_APPROP_SCTID',
    setchk_short_name='CHK01 Appropriate SNOMED CT identifiers for value set members', 
    setchk_function=CHK01_APPROP_SCTID.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    )

setchks['CHK02_IDS_IN_RELEASE']=Setchk(
    setchk_code='CHK02_IDS_IN_RELEASE',
    setchk_short_name='CHK02 Identifiers are in selected the SNOMED CT release.', 
    setchk_function=CHK02_IDS_IN_RELEASE.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )

setchks['CHK04_INACTIVES_ENTRY']=Setchk(
    setchk_code='CHK04_INACTIVES_ENTRY',
    setchk_short_name='CHK04 Inactive content in sets for data entry', 
    setchk_function=CHK04_INACTIVES_ENTRY.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY","ENTRY_OTHER"],
    )

setchks['CHK05_UNRECC_HIERARCH']=Setchk(
    setchk_code='CHK05_UNRECC_HIERARCH',
    setchk_short_name='CHK05 Prohibited hierarchies for collating into a value set for clinical data entry.', 
    setchk_function=CHK05_UNRECC_HIERARCH.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    )

setchks['CHK06_DEF_EXCL_FILTER']=Setchk(
    setchk_code='CHK06_DEF_EXCL_FILTER', 
    setchk_short_name='CHK06 Inclusion of not recommended concepts', 
    setchk_function=CHK06_DEF_EXCL_FILTER.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    )

setchks['CHK10_MISSING_CONCEPTS']=Setchk(
    setchk_code='CHK10_MISSING_CONCEPTS', 
    setchk_short_name='CHK10 Check for omitted descendants from a specific region of the hierarchy', 
    setchk_function=CHK10_MISSING_CONCEPTS.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )

setchks['CHK14_MANY_CLAUSES']=Setchk(
    setchk_code='CHK14_MANY_CLAUSES',
    setchk_short_name='CHK14 Value Set membership expression requires 30-40 clauses', 
    setchk_function=CHK14_MANY_CLAUSES.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )

setchks['CHK20_INCORR_FMT_SCTID']=Setchk(
    setchk_code='CHK20_INCORR_FMT_SCTID',
    setchk_short_name='CHK20 Incorrectly formatted SNOMED CT identifiers', 
    setchk_function=CHK20_INCORR_FMT_SCTID.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )