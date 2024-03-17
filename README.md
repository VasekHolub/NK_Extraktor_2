**Reference Marks Extractor**

This Python script extracts reference marks from text documents written in different languages such as English, German, and Czech. It utilizes language-specific models for processing and extracting reference marks.
**
Setup and Requirements**

To run this script, ensure you have the following installed:

  Python 3.x
  
  Required Python packages: spacy, stanza

Additionally, the script requires language models for English, German, and Czech. These models are automatically loaded by the script when needed. Ensure you have a stable internet connection for loading the models if they are not already installed.

**Usage**

1. Place the text document you want to process named "patent.txt" in the same directory as the script.
2. Follow the prompts to select the language and extraction mode:
For language selection, enter either "cs" for Czech, "en" for English, or "de" for German.
Choose between Broad (b) or Precision (p) mode for extraction. Broad mode returns more hits but might include duplicates, while Precision mode returns unique hits but may miss some references and return false positives instead.
3. Once the extraction is complete, a CSV file named "Vztah_znacky_b.csv" or "Vztah_znacky_p.csv"  will be generated in the same directory, containing the extracted reference marks.

**Functionality**

The script loads language models based on the selected language (English, German, or Czech).
It processes the text document and extracts reference marks based on linguistic patterns specific to each language.
The user can choose between Broad or Precision mode for extraction, which affects the number of hits returned.
Extracted reference marks are exported to a CSV file for further analysis.

**Note**

Ensure the text document "patent.txt" exists in the same directory as the script.
A blacklist file named "blacklist.txt" is used to filter out unwanted reference marks. Make sure to populate this file if necessary.
This script is designed for processing patent documents but can be adapted for other types of text documents with appropriate modifications.
