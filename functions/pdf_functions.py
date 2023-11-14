import re
import pandas as pd
from PyPDF2 import PdfReader

# The start of page 0
rgx_page0_start = re.compile('TOTAL PAYMENTS RECEIVED')

# unique reference number
rgx_urn = re.compile("999008")

# The start of page 1 plus
rgx_page1_plus_start =re.compile("Page \d+ of \d+")

# Regex - date (doesn't check for invalid dates)
rgx_date = re.compile("(?<=\\n)\d{2}\/\d{2}\/\d{2}")

def get_next_date(text, rgx_date):

    """ Returns subset of input text,   
        starting at the next 'date' in format set
        by rgx_date (regex)
    
    """
    startPoint = rgx_date.search(text).span()[0]
    return text[startPoint:]

def process_chunk(text, rgx_date):

    """ Returns list containing the following details of each transaction
        Date
        Description (1 and 2)
        Total amount
        Share
        Actual amount

        :params
        text (str) - the full text
        rgx_date (compiled regex) for date format

        
    """
    
    # 6 lines of data in each chunk
    chunk = text.split('\n')[:6]

    # If index 0 is not in regex date format - then return None
    if rgx_date.search("\n" + chunk[0]) is None: chunk = None

    return chunk
    
def get_start_next_chunk(text, regex):

    """ Returns subset of input text 
        starting at the next chunk of statement

        regex: compiled regex - used to identify the start of the chunk
    """


    startPoint = regex.search(text).span()[1]+1
    return text[startPoint:]

def get_reader_object(file_path):

    """
        Returns a class 'PyPDF2._reader.PdfReader'
        
        Parameters

        file_path (str): Full file path of a single pdf
    """

    # Reader
    reader = PdfReader(file_path)
    return reader

def get_text_from_pages(reader):

    """
        Returns a list of strings 
        Length of list matches number of pages in pdf

        Parameters

        reader (class 'PyPDF2._reader.PdfReader')

    """

    # List of pages (text content)
    pages = [page.extract_text() for page in reader.pages]

    # Remove blank lines
    pages = [re.sub('\n \n', '\n', text) for text in pages]

    return pages

def get_next_entry(page_rem, rgx_page_start, rgx_date):

    """
        Returns string, with remainder of page
        
        Parameters

        page_rem (str): String containing remainder (rem) of page
        rgx_page_start (compiled regex)
        rgx_date

    """

    # Get start of next chunk
    page_rem = get_start_next_chunk(page_rem, rgx_page_start)

    # Get next date
    page_rem = get_next_date(page_rem, rgx_date)

    return page_rem

def process_page_0(page_rem, rgx_date, rgx_urn):

    """

        Parameters

        page_rem (str)
        chunks (list)
        rgx_date
        rgx_urn

    """

    # Init as not None to start process
    chunk = ''

    chunks = []

    while chunk is not None:

        # Page - remainder
        page_rem = get_start_next_chunk(page_rem, rgx_urn)
        #page0_rem = get_next_date(page0_rem, rgx_date)

        # Get chunk
        chunk = process_chunk(page_rem, rgx_date)
        if chunk is not None: chunks.append(chunk) 
    return page_rem, chunks

def process_all_page_0(page_rem, rgx_page0_start, rgx_date):

    """
        Process all of the first page of a PDF
    """

    # Get start page of page
    page_rem = get_next_entry(page_rem, rgx_page0_start, rgx_date)

    # Get first chunk
    chunks = [process_chunk(page_rem, rgx_date)]

    # Process remainder of page
    page_rem, new_chunks = process_page_0(page_rem, rgx_date, rgx_urn)

    # Add new chunks
    chunks.extend(new_chunks)

    return chunks

def process_all_other_pages(page, rgx_page1_plus_start, rgx_urn):

    """
        Processes pages 1+
    """

    # init empty list
    chunks = []

    # Copy page to remainder object
    page_rem = page

    # Init page_start (boolean) and chunk as not None
    page_start = True
    chunk = ''

    while chunk is not None:

        # If start of page then we use the page x of y logic
        if page_start:
            page_rem = get_start_next_chunk(page_rem, rgx_page1_plus_start)
            page_start = False # Set to False for remainder of page
        else:

            # For other parts of page we need to use URN
            page_rem = get_start_next_chunk(page_rem, rgx_urn)

        # Process chunk
        chunk = process_chunk(page_rem, rgx_date)

        # Add to list if there's data
        if chunk is not None: chunks.append(chunk)

    return chunks

def get_dataframe(chunks):

    """

    """
    # Column names
    columns = ["date", "description_1", "description_2", "txn_amount", "txn_share", "txn_actual"]
    df = pd.DataFrame(data=chunks, columns=columns)
    return df

def process_single_pdf(file_path):

    """

        Parameters:

        file_path (str): Full file path of a single pdf

    """
    print(f"Processing: {file_path}")
    # Get reader object
    reader = get_reader_object(file_path)

    # Pages (text content)
    pages = get_text_from_pages(reader)

    # Process each page in single pdf
    for page_num in range(len(pages)):

        # Current page
        page = pages[page_num]

        if page_num == 0:

            # Process all of page 0
            chunks = process_all_page_0(page, rgx_page0_start, rgx_date)

        else:

            # Get new chunks
            new_chunks = process_all_other_pages(page, rgx_page1_plus_start, rgx_urn)
            chunks.extend(new_chunks)

    df = get_dataframe(chunks)
    
    # Add source
    df['source'] = file_path
    return df
