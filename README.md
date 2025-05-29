# File-Organizer-using-Python
## Overview
A Python script that organizes files in a specified folder by type (Images, Documents, Others) and metadata. It detects and prevents duplicate files using MD5 hashing, moves files to appropriate subfolders, and logs all operations to a timestamped log file and console.

## Features
1. File Type Sorting: Organizes files into "Images," "Documents," or "Others" based on file extensions.
2. Metadata-Based Organization: Uses metadata like EXIF dates for images, author/date for PDFs, and creation dates for DOCX, XLSX, and TXT files to create subfolders.
3. Duplicate Detection: Identifies duplicates using MD5 hashing to avoid redundant files.
4. Logging: Records all operations in a timestamped log file and console.
5. Command-Line Interface: Accepts folder paths via CLI arguments for easy use.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/nehatabassum572/File-Organizer-using-Python
   ```
2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```
## Usage
1. Run the `organize.py` script: 
```bash
   python organize.py --folder /path/to/your/folder
```
## Project Structure
1. `organize.py`: Contains the main script .
2. `requirements.txt`: List of required Python packages.

