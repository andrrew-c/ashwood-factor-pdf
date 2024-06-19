import os
import argparse

import pandas as pd

from functions.general_functions import get_statement_paths
from functions.pdf_functions import process_single_pdf

""" 
Get command line arguments
"""

# Init parser
parser = argparse.ArgumentParser(description="Process PDF statements")

# Set up arguments

parser.add_argument('--parent_folder', type=str, help='Full path where statements are held')
parser.add_argument('--write_out',
                        help='Writes out with name statements.xlsx if True',
                        action='store_true')

# Get command line arguments
args = parser.parse_args()


if __name__ == "__main__":

    # Get paths (or path if single file passed)
    paths = get_statement_paths(args.parent_folder)

    # Get df (list of dataframes)
    df = pd.concat([process_single_pdf(path) for path in paths])

    if args.write_out:
        df.to_excel(os.path.join(args.parent_folder,'factor_statements.xlsx'))
    