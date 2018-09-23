"""Util functions used in csv_cleaner.py
The only outside package that needs to be installed is chardet, which can
be installed with 'pip intall chardet'.  chardet is used to determine the
file encoding.
"""
import csv
import chardet

def get_file_metaddata(file, filename):
    """This function creates a dictionary to store the filename and file
    contents.  It is designed to be expanded upon in the future for logging
    other information like AWS S3 source bucket / destination bucket if using
    cloud storage.

    Args:
        file: contents of the file whose metadata is being stored.
        filename: name of the file being processed.

    Returns:
        metadata: a dictionary object containing the metadata for the file.
    """
    metadata = {}
    metadata['file_name'] = filename
    metadata['file'] = file.read()
    return metadata

def process_encoding(data_file_str):
    """Determine the encoding of a file using chardet.  If the encoding is
    not utf-8 or ascii, try to force decode the file to utf-8.

    Args:
        data_file_str: the file contents stored as a string.

    Returns:
        Boolean: if encoding is utf-8/ascii or force decode to utf-8 is
        successful, then True.  Else, return False.
        data_file_str: return the file contents having an encoding of utf-8.
        If the encoding isn't utf-8, return None.
    """
    encoding = chardet.detect(data_file_str.encode())['encoding']
    if encoding is None:
        return False, None
    else:
        encoding = encoding.lower()
        if encoding != 'ascii' and encoding != 'utf-8':
            try:
                data_file_str = data_file_str.decode(encoding)
                return True, data_file_str
            except ValueError:
                return False, None
        return True, data_file_str

def get_file_delim(delimited_data):
    """Determine the delimiter in the file.  A common problem I've
    experienced in the past is that csv files sometimes have tab delimiters
    (sigh), so you can't simply rely on the file name.  This would also let
    anyone using the program parse any file type (csv, tsv, txt...) without
    relying on the file name or assuming the delimiter.

    Args:
        delimited_data: data from the file as a string with some unknown
        delimiter.

    Returns:
        Boolean: if delimiter can be found, return True.  Else, return False.
        dialect.delimiter: delimiter of the file.  If none is found,
        return None.
    """
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(delimited_data)
        return True, dialect.delimiter
    except ValueError:
        return False, None

def replace_newline(data_str):
    """Used to replace '\r\n' line breaks used in windows with '\n' which is
    used in unix\linux.  This is to make re-stiching the file back together
    easier.

    Args:
        data_str: data of the file that's being processed.

    Returns:
        data_str: data of the file with any '\r\n' line breaks replaced with
        '\n'.
    """
    return data_str.replace('\r\n', '\n').split('\n')

def check_id(row, id_set):
    """Business Logic Rule for ID column, ID must be an INTEGER and not
    be a duplicate in the set.  In this case, its assumed to keep the first
    occurence of the ID.  This check exists outside of the data_type_checks
    as this rule is applicable to data sets outside of example.csv.

    Args:
        row: the current row of data from the file that's having it's id checked.
        id_set: the set of ids that have previously been processed to avoid
        writing duplicates to the clean file.

    Returns:
        Boolean: if the id of the row hasn't been processed yet, return True.
        If the id isn't an integer, or if it has been processed already, return
        False.
    """
    try:
        row_id = int(row[0])
    except ValueError:
        return False
    if row_id in id_set:
        return False
    else:
        id_set.add(row_id)
        return True

def data_type_checks(row):
    """Hard coded rules to check the data types of each row
    and enforce business logic rules.  This is a custom function designed
    to find generalized errors specifically for the example.csv dataset.
    For example, the state two letter codes is hard coded here to check this
    column against a known set of values.  Another rule is checking the length
    of the zip code column, as we will know its always a five digit integer.
    For each row, both the state code and zip code columns are checked against
    the above rules.  For the state code, if it isn't in the state_codes set,
    we merge values into the address column and check again.  This is similarly
    done for the zip code column where we add values to the zip code field and
    check to make sure it is an integer.
    Additional rules can be added to this function, and this is the function
    that would change between different datasets.

    Args:
        row: the current row of data from the file that's having it's id
        checked.

    Returns:
        row: returns the cleaned row of data, or None if the data can't be
        cleaned.
    """
    state_codes = ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT',
                   'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
                   'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
                   'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
                   'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH',
                   'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
                   'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI',
                   'WY')
    # state code check
    if row[3] in state_codes:
        pass
    else:
        # we know that no values after the State column will be a state code,
        # merge data on address
        # assuming business name is not the same as a state code
        row = [row[0]] + [' '.join(row[1:-4])] + row[-4:]
        if row[3] in state_codes:
            pass
        else:
            return None
    # zip code check
    if len(row[4]) == 5: # first check the length
        try:
            int(row[4]) # test if its an integer
        except ValueError:
            return None
    elif len(row[4]) < 5:
        row = row[0:4] + [''.join(row[4:-1])] + [row[-1]]
        if len(row[4]) == 5:
            try:
                int(row[4]) # test if its an integer
            except ValueError:
                return None
        else:
            return None
    else:
        return None
    return row

def row_by_row_check(data_file, delimiter, header_len):
    """This function executes the row level checks for csv_cleaner.  For
    each row, it checks to see if the row has the right length as compared
    to the header of the file. If the row is too short, the data is added
    to a cache as there is probably an improper line break in the file.
    The cache is reset if it reaches a row with a length greater than or
    equal to the header length as this means that the cache is filled with
    an incomplete row of data.
    Once the cache is filled or a row with a length greater than or equal to
    the header is found, the data cleaning functions (check_id and
    data_type_checks) are called to check if the row of data is clean or
    can be cleaned.  If the row is successfully cleaned, it is added to
    output_clean_data, else the dirty rows are added to output_dirty_data.

    Args:
        data_file: contents of the file that are inspected row by row.
        delimiter: the delimiter of the file determined by get_file_delim.
        header_len: the length of the header file.

    Returns:
        output_clean_data: a string of cleaned data from the file.
        output_dirty_data: a string of dirty data from the file.
    """
    output_clean_data = []
    output_dirty_data = []
    cache_prev_row = []
    set_of_ids = set()
    for line in data_file:
        row = line.split(delimiter)
        if header_len > len(row):
            cache_prev_row += row
            ### attempt to fix cache if another short row occurs
            if len(cache_prev_row) >= header_len:
                id_check = check_id(cache_prev_row, set_of_ids)
                data_check = data_type_checks(cache_prev_row)
                if id_check and data_check:
                    output_clean_data.append(','.join(data_check))
                else:
                    output_dirty_data.append(','.join(cache_prev_row))
                cache_prev_row = []
        else:
            if cache_prev_row != []:
                output_dirty_data.append(','.join(cache_prev_row))
                cache_prev_row = [] # cache refreshes since it is apparent
                                    # that previous row is bad
            id_check = check_id(row, set_of_ids)
            data_check = data_type_checks(row)
            if id_check and data_check:
                output_clean_data.append(','.join(data_check))
            else:
                output_dirty_data.append(','.join(row))
    return '\n'.join(output_clean_data), '\n'.join(output_dirty_data)

def save_to_csv(metadata, data, path):
    """A function to save a string to a file in the specified path.

    Args:
        metadata: metadata of the file being processed, which comes from
        get_file_metaddata.
        data: the data of the file stored as a string which will be saved.
        path: path to where the data will be saved too.

    Returns:
        None, a file is saved to the specified directory.
    """
    with open('processed_data/' + path + '/' +
              metadata['file_name'], 'w') as output_file:
        output_file.write(data)
        output_file.close()
