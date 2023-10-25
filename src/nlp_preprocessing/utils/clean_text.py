import os
import re

# Specify the directory containing the files
directory = "psychometrika/txt/"

# Loop through each file in the directory
for file in os.listdir(directory):
    # Construct the file path
    file_path = os.path.join(directory, file)
    # Check if the file is a regular file
    if os.path.isfile(file_path):
        # Read the file content
        with open(file_path, "r") as f:
            content = f.read()

        # Remove control characters such as:
        #  - the carriage return chars (`\r` in Python and `^M` in text files)
        #  - backspace chars (`\x08` in Python and `^B` in text files)

        # Remove control characters
        content = content.replace('\r', '') \
                         .replace('\x0B', '') \
                         .replace('\x0C', '') \
                         .replace('\x01', '') \
                         .replace('\x02', '') \
                         .replace('\x03', '') \
                         .replace('\x04', '') \
                         .replace('\x05', '') \
                         .replace('\x06', '') \
                         .replace('\x07', '') \
                         .replace('\x08', '') \
                         .replace('\x0E', '') \
                         .replace('\x0F', '') \
                         .replace('\x10', '') \
                         .replace('\x11', '') \
                         .replace('\x12', '') \
                         .replace('\x13', '') \
                         .replace('\x14', '') \
                         .replace('\x15', '') \
                         .replace('\x16', '') \
                         .replace('\x17', '') \
                         .replace('\x18', '') \
                         .replace('\x19', '') \
                         .replace('\x1A', '') \
                         .replace('\x1B', '') \
                         .replace('\x1C', '') \
                         .replace('\x1D', '') \
                         .replace('\x1E', '') \
                         .replace('\x1F', '')

        # Write the modified content back to the file
        with open(file_path, "w") as f:
            f.write(content)
