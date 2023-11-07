import os 
import re
from PyPDF2 import PdfReader
import pandas as pd
#from pdfreader import PDFDocument, SimplePDFViewer


"""
Define constants, incl. regular expressions
"""

# Parent folder
parent_path = "/Users/andrew.craik/Nextcloud/Renting-Andrew/Ashwood Gait/"

# Financial year we're processing
finyear = "2022-23"

# Folder where statements are§
folder_statement = "Factor-statements"

# Single statement
file = "2022-05.pdf"

# unique reference number
urn = re.compile("999008")

# The start of page 0
page0_start = re.compile('TOTAL PAYMENTS RECEIVED')

# The start of page 1 plus
page1plus_start =re.compile("Page \d+ of \d+")

# Regex - date (doesn't check for invalid dates)
re_date = re.compile("(?<=\\n)\d{2}\/\d{2}\/\d{2}")

# Full path (single file)
fname = os.path.join(parent_path, finyear, folder_statement, file)

""" 
Open up PDF and extract text
"""

# Reader
reader = PdfReader(fname)

# List of texts
texts = [page.extract_text() for page in reader.pages]

# Remove blank lines
texts = [re.sub('\n \n', '\n', text) for text in texts]

"""
To help debug - write out to text file
"""

# Output to individual text files
for i in range(len(texts)):
    file = open(f'blah_{i}.txt', 'wt') 
    file.write(texts[i])
    file.close()

"""
Define functions
"""

def get_next_date(text, re_date):

    """ Returns subset of input text,   
        starting at the next 'date' in format set
        by re_date (regex)
    
    """
    startPoint = re_date.search(text).span()[0]
    return text[startPoint:]


def processChunk(text, re_date):

    """ Returns list containing the following details of each transaction
        Date
        Description (1 and 2)
        Total amount
        Share
        Actual amount

        :params
        text (str) - the full text
        re_date (compiled regex) for date format

        
    """
    
    # 6 lines of data in each chunk
    chunk = text.split('\n')[:6]

    # If index 0 is not in regex date format - then return None
    if re_date.search("\n" + chunk[0]) is None: chunk = None

    return chunk
    
def get_start_next_chunk(text, regex):

    """ Returns subset of input text 
        starting at the next chunk of statement

        regex: compiled regex - used to identify the start of the chunk
    """


    startPoint = regex.search(text).span()[1]+1
    return text[startPoint:]


""" 
Page 1 - find the start of the actual statement
"""

# Get first page
page0 = texts[0]

# Get start of next chunk
page0_rem = get_start_next_chunk(page0, page0_start)

# Get next date
page0_rem = get_next_date(page0_rem, re_date)

chunk = processChunk(page0_rem, re_date)
chunk

"""
Page 1 - get next chunk
Repeat this until......
"""
chunks = [chunk]

while chunk is not None:

    # First page - remainder
    page0_rem = get_start_next_chunk(page0_rem, urn)
    #page0_rem = get_next_date(page0_rem, re_date)

    # Get chunk
    chunk = processChunk(page0_rem, re_date)
    if chunk is not None: chunks.append(chunk) 

print(len(chunks))

""" 
Page 2+ 
Get to first bit that says "page x of y"
"""

# For remainder of pages
for page in texts[1:]:

    # Copy page to remainder object
    page_rem = page

    # Init firstPage (boolean) and chunk as not None
    firstPage = True
    chunk = ''

    while chunk is not None:

        # If first page then we use the page x of y logic
        if firstPage:
            page_rem = get_start_next_chunk(page_rem, page1plus_start)
            firstPage = False # Set to False for remainder of page
        else:

            # For other parts of page we need to use URN
            page_rem = get_start_next_chunk(page_rem, urn)

        # Process chunk
        chunk = processChunk(page_rem, re_date)

        # Add to list if there's data
        if chunk is not None: chunks.append(chunk)

print(len(chunks))

"""
With chunks - create dataframe
"""
columns = ["date", "description_1", "description_2", "txn_amount", "txn_share", "txn_actual"]
df = pd.DataFrame(data=chunks, columns=columns)

df.to_csv('blah.csv')