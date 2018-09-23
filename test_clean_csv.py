"""This script contains the unit tests for csv_cleaner.py
We compare the output of csv_cleaner.py's example.csv test to a manually
parsed file to compare if the fixes the program makes are the same as
the manual ones.
After running csv_cleaner.py, make sure example_clean.csv is in the
fixed_files directory.  Then run test_clean_csv.py in the parent directory
and observe the test case in the command line.
"""
import unittest

class CleanCSVTest(unittest.TestCase):
    """CleanCSVTest is the class which contains the unittest cases.
    For now, there is only one test case of example.csv, but other tests
    can be created by comparing other output files.
    """
    def test_example_csv(self):
        """test_example_csv simply opens the programmatically cleaned
        example.csv and the manually cleaned example_clean.csv.  Then, the
        function simply asserts if the two outputs are equal.  If the test
        case fails, the difference is printed to the command line.

        Args:
            There are no arguments the files being compared in this unit test
            are predetermined as processed_data/cleaned_files/example.csv and
            processed_data/cleaned_files/example_clean.csv.

        Returns:
            Prints to the command line either the success of the test or
            the line in each file that differs.
        """
        with open('processed_data/cleaned_files/example.csv') as prog_output:
            my_output = prog_output.read()
        with open('processed_data/cleaned_files/example_clean.csv') \
            as manual_output:
            manual_output = manual_output.read()
        if my_output == manual_output:
            print(True)
        self.assertEqual(my_output, manual_output)
