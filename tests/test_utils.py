import os

def read_test_file(filename):
    """Reads a text file and returns its content as a string."""
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    #test_data_dir = "/home/and/Dropbox/computing-msc-uea/nlp/axidoc/tests/test_data"
    with open(os.path.join(test_data_dir, filename), 'r') as file:
        return file.read()

# Read files to strings
text_with_values = read_test_file('text_with_values.txt')
text_wo_values = read_test_file('text_wo_values.txt')
