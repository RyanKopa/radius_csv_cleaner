CSV Cleaner
----------

At Radius we often get poorly formatted CSVs that cannot be uploaded to our application.  

Common issues include:
- A row with the wrong number of fields
- Blank lines
- New line characters
- Unclosed quotes: ex: “Bob”s pizzeria”
- Invalid encoding: Odd characters that cause encoding errors
- Duplicate column names
- Duplicate IDs (every record must have a unique ID)

The challenge is to build an internal tool that can be used to scrub CSVs before they are uploaded to the app. It does not have to have a sophisticated interface: a simple command-line interface is fine. No solution is going to be completely generalizable, but the goal is to make the process as automatic as possible. Include a brief description of how your process should work, and what (if any) manual work still has to be done. You can use the file ‘example.csv’ to test.

Set up and Running
-----------------
To set up CSV Cleaner, simply install the dependencies using:
```bash
pip install -r requirements.txt
```
The only outside package used in this program is [chardet](https://chardet.readthedocs.io/en/latest/usage.html) which is used to detect the encoding of a file.

To run the program, simply put all the delimited files into the 'data' directory and run in the parent directory:
```bash
python csv_cleaner.py
```
The cleaned files will be outputted into the 'processed_data/cleaned_files/' directory.  Any rows of data that couldn't be cleaned will be put into the 'processed_data/dirty_files/' directory.

The rules engine for executing data quality checks specific to the data are listed in the utils.data_type_checks function.  This function will need to be changed when the structure of the data changes.  This is the only manual change necessary for this program; data quality fixes including empty rows, handling line breaks inside rows, encoding issues, duplicate ids, and unmatched quotations are handled outside of utils.data_type_checks and don't need to be adjusted.  Ideally, this program will clean a delimited file enough for it to be properly loaded into a database or another program.

Testing
-------
I created a test case for this program by manually cleaning example.csv and comparing it to the output of csv_cleaner.py.  The manually cleaned file is called example_clean.csv and is stored in the processed_data/cleaned_files directory.  To repeat the test, run:
```bash
python -m unittest test_clean_csv.py
```

A successful test case will look like:
```bash
True
.
----------------------------------------------------------------------
Ran 1 test in 0.032s

OK

```
If the test case fails, it will show the part of the file where the difference occurs.
