import os
import shutil
from PIL import Image
import hashlib
import argparse
import PyPDF2
from docx import Document
import openpyxl
from datetime import datetime
import logging

# Configure logging
def setup_logging():
    log_file = f"file_organizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # This keeps console output
        ]
    )
    return logging.getLogger()

EXTENSIONS = {
    "Images": [".jpg", ".jpeg", ".png"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Others": []
}

# To get the (meta data) from the images
def get_exif_date(file_path):
    """Extract EXIF date from image."""
    try:
        img = Image.open(file_path)
        exif = img._getexif()
        if exif and 36867 in exif:  # 36867 EXIF tag ID for "DateTimeOriginal"
            return exif[36867].split(" ")[0].replace(":", "-")
    except Exception as e:
        logger.error(f"Failed to get EXIF date for {file_path}: {e}")
    return None

# To extract the (meta data) from pdf
def get_pdf_metadata(file_path):
    """Extract author and creation date from PDF."""
    try:
        reader = PyPDF2.PdfReader(file_path)
        info = reader.metadata
        author = info.author if info.author else "Unknown"
        created = info.creation_date
        date = created.strftime("%Y-%m") if created else None
        return {"author": author, "date": date}
    except Exception as e:
        logger.error(f"Failed to get PDF metadata for {file_path}: {e}")
        return {"author": "Unknown", "date": None}

# To extract the meta data from docx
def get_docx_metadata(file_path):
    """Extract creation date from DOCX."""
    try:
        doc = Document(file_path)
        created = doc.core_properties.created
        date = created.strftime("%Y-%m") if created else None
        return {"date": date}
    except Exception as e:
        logger.error(f"Failed to get DOCX metadata for {file_path}: {e}")
        return {"date": None}

# To extract the meta data from excel
def get_excel_metadata(file_path):
    """Extract title and creation date from Excel."""
    try:
        wb = openpyxl.load_workbook(file_path)
        props = wb.properties
        title = props.title if props.title else "Untitled"
        created = props.created
        date = created.strftime("%Y-%m") if created else None
        return {"title": title, "date": date}
    except Exception as e:
        logger.error(f"Failed to get Excel metadata for {file_path}: {e}")
        return {"title": "Untitled", "date": None}

# To extract the meta data from txt
def get_txt_metadata(file_path):
    """Extract modification date from TXT file."""
    try:
        stat = os.stat(file_path)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        return {"date": mtime.strftime("%Y-%m")}
    except Exception as e:
        logger.error(f"Failed to get TXT metadata for {file_path}: {e}")
        return {"date": None}

# To detect duplicate files
def get_file_hash(file_path):
    """Compute MD5 hash of file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Dictionary mapping extensions to (metadata_function, folder_function)
FILE_HANDLERS = {
    ".jpg": (get_exif_date, lambda meta, folder: os.path.join(folder, "Images", meta or "NoDate")),
    ".jpeg": (get_exif_date, lambda meta, folder: os.path.join(folder, "Images", meta or "NoDate")),
    ".png": (get_exif_date, lambda meta, folder: os.path.join(folder, "Images", meta or "NoDate")),
    ".pdf": (get_pdf_metadata, lambda meta, folder: os.path.join(folder, "Documents", meta["author"].replace("/", "_").replace(" ", "_") or "Unknown")),
    ".docx": (get_docx_metadata, lambda meta, folder: os.path.join(folder, "Documents", meta["date"] or "NoDate")),
    ".xlsx": (get_excel_metadata, lambda meta, folder: os.path.join(folder, "Documents", meta["title"].replace("/", "_").replace(" ", "_") or "Untitled")),
    ".txt": (get_txt_metadata, lambda meta, folder: os.path.join(folder, "Documents", meta["date"] or "NoDate")),
}

def sort_by_extension(folder, seen_hashes=None):
    """Sort files by type and metadata, skip duplicates."""
    if seen_hashes is None:
        seen_hashes = {}
    folder = os.path.abspath(folder)
    logger.info(f"Processing folder: {folder}")
    try:
        for filename in os.listdir(folder):
            src = os.path.join(folder, filename)
            logger.info(f"Checking file: {filename}")
            if not os.path.isfile(src):
                logger.info(f"Skipping non-file: {filename}")
                continue
            file_hash = get_file_hash(src)
            seen_hashes[file_hash] = src
            ext = os.path.splitext(filename)[1].lower()
            handler = FILE_HANDLERS.get(ext, (None, lambda meta, folder: os.path.join(folder, "Others")))
            metadata_func, folder_func = handler
            try:
                metadata = metadata_func(src) if metadata_func else None
                logger.info(f"Metadata for {filename}: {metadata}")
                dest_folder = folder_func(metadata, folder)
                # Sanitize folder name
                dest_folder = "".join(c for c in dest_folder if c.isalnum() or c in (os.sep, "_", "-"))
                logger.info(f"Destination for {filename}: {dest_folder}")
                os.makedirs(dest_folder, exist_ok=True)
                dest = os.path.join(dest_folder, filename)
                shutil.move(src, dest)
                logger.info(f"Moved {filename} to {dest_folder}")
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
    except Exception as e:
        logger.error(f"Error accessing folder {folder}: {e}")

def main():
    """Run file organizer with CLI arguments."""
    parser = argparse.ArgumentParser(description="Organize files by type and metadata")
    parser.add_argument("--folder", required=True, help="Folder to organize")
    args = parser.parse_args()
    sort_by_extension(args.folder)

if __name__ == "__main__":
    logger = setup_logging()
    main()