"""csv_cleaner.py takes in all the csvs in the data/ directory and parses them to:
    1) write the good quality rows of data to an output file in the
    processed_data/fixed_files/ directory.
    2) fix any rows of data that have correctable errors to the same directory.
    3) write and bad rows of data to a second output file in the
    processed_data/bad_files/ directory for outside/manual reivew.
This script uses the functions in utils.py to execute changes on the raw data.
In my case, I've loaded the entire file in memory for faster processing speeds
since the test file provided was very small.  If larger data is being procesed,
moving to reading line by line is possible by changing the main function.
The only outside package that needs to be installed to run csv_cleaner.py
is chardet, which can be installed with 'pip intall chardet'.
"""

import os
import utils

def main():
    """Main function that executes all of the data alterations and checks
    against the input data.
    First, the function iterates through all of the files in the data directory,
    and creates a dictionary object containing the file name in file_name and
    file contents in file.
    Afterwards, we check the encoding of the file
    with utils.process_encoding, and attempt to force convert the file to
    UTF-8 if it is not in that format already.
    Then, the delimiter of the file is taken from utils.get_file_delim.
    Next, utils.replace_newline is used to make the new line/line breaks to
    '\n'
    Finally, utils.row_by_row_check is run to parse each row and fix any
    common data issues.

    Args:
        There are no arguments as the program parses all the files in the
        data directory.

    Returns:
        None. For each file in the data director, a copy of its cleaned data
        is saved to the processed_data/cleaned_files directory, and a copy of
        its dirty data is saved to the processed_data/dirty_files directory.
    """
    for filename in os.listdir('data'):
        with open('data/' + filename) as raw_data:

            data_file = utils.get_file_metaddata(raw_data, filename)

            utf_encoding, data_file['file'] = utils.process_encoding(data_file['file'])
            if not utf_encoding:
                utils.save_to_csv(data_file, data_file['file'], 'bad_files')
                continue

            has_delim, delimiter = utils.get_file_delim(data_file['file'])
            if not has_delim:
                utils.save_to_csv(data_file, data_file['file'], 'bad_files')
                continue

            data_file['file'] = utils.replace_newline(data_file['file'])
            header = data_file['file'].pop(0)
            header_length = len(header.split(','))

            cleaned_data, dirty_data = utils.row_by_row_check(data_file['file'],
                                                              delimiter,
                                                              header_length)
            if cleaned_data:
                utils.save_to_csv(data_file,
                                  header+'\n'+cleaned_data,
                                  'cleaned_files')
            if dirty_data:
                utils.save_to_csv(data_file,
                                  header+'\n'+dirty_data,
                                  'dirty_files')

if __name__ == "__main__":
    main()
