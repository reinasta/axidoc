import sys
import logging
import pypdfium2 as pdfium  # type: ignore
from pathlib import Path

from constants import DOWNLOAD_DIR, DOWNLOAD_DIR_TEXT

#DOWNLOAD_DIR = Path('tests/pdf')
#DOWNLOAD_DIR_TEXT = Path('tests/txt')


# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a file handler and set the log file path
log_file = "logs/log_doi2pdf.txt"
file_handler = logging.FileHandler(log_file)

# Configure the file handler
file_handler.setLevel(logging.INFO)  # Set the desired log level
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the file handler to the logger
logger.addHandler(file_handler)


# store pdf files whose conversion to text failed or succeeded
EXCEPTIONS:list[str] = []
SUCCESSES:list[str] = []


def convert(data):
    text = ""
    try:
        pdf = pdfium.PdfDocument(data)
    except Exception as e:
        logger.error(f"Error loading pdf data.")
        logger.exception(e)
        return None
    for i in range(len(pdf)):
        page = pdf.get_page(i)
        textpage = page.get_textpage()
        text += textpage.get_text()
        text += "\n"
        # Close the resources
        textpage.close()
        page.close()
    pdf.close()
    return text

# Get all the PDF files in the DOWNLOAD_DIR
pdf_files = DOWNLOAD_DIR.glob("*.pdf")

# Iterate over the PDF files and convert them to text
for pdf_path in pdf_files:
    txt_path = DOWNLOAD_DIR_TEXT / (pdf_path.stem + ".txt")

    try:
        # Read the PDF file as bytes
        with open(pdf_path, "rb") as file:
            pdf_data = file.read()
    except Exception as e:
        logger.error(f"Error reading the pdf file at {pdf_path}.")
        EXCEPTIONS.append(str(pdf_path))
        continue

    try:
        # Convert the PDF to text
        text = convert(pdf_data)
    except Exception as e:
        logger.error(f"Error converting {pdf_path}.")
        logger.exception(e)
        EXCEPTIONS.append(str(pdf_path))
        continue

    try:
        # Write the text to the corresponding text file
        with open(txt_path, "w") as file:  # type: ignore
            file.write(text)
    except Exception as e:
        logger.error(f"Error writing the pdf file to text at {txt_path}.")
        EXCEPTIONS.append(str(pdf_path))
        continue

    logger.info(f"Converted {pdf_path.stem}.pdf to {txt_path.stem}.txt")
    SUCCESSES.append(str(pdf_path))

## Successes

if len(SUCCESSES) > 0:
    if len(EXCEPTIONS) == 0:
        logger.info(f"  # *All* files have been converted!")
    logger.info(f"  # Successfully converted {len(SUCCESSES)} pdf files to text:")
    for s in SUCCESSES:
        logger.info(s)


## Exceptions

if len(EXCEPTIONS) > 0:
    logger.info(f"  # Pdf-to-text conversion failed for {len(EXCEPTIONS)} files")
    for exc in EXCEPTIONS:
        logger.info(f"      + {exc}")
