
import os
import re

def get_statement_paths(parent_folder):

    """ Return list of absolute paths"""

    if os.path.isdir(parent_folder):
                     
        # Get files
        files = os.listdir(parent_folder)

        # Keep only pdfs
        pdfs = [file for file in files if re.search('.pdf$', file) is not None]
        
        # Now get absolute paths
        pdf_paths = [f"{parent_folder}/{pdf}" for pdf in pdfs]
    else:
        pdf_paths = [parent_folder]

    return pdf_paths