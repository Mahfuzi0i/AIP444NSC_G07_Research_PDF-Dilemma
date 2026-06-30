import os
import time
import csv
import difflib
import pdfplumber
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()

PDFS_DIR = "./pdfs"
OUTPUTS_DIR = "./outputs"

# table_preservation rubric (manual, fill in outputs CSV after reviewing extracted text):
#   0 = table not detected / completely garbled
#   1 = partial — some rows/columns captured but structure broken
#   2 = mostly correct — minor misalignments or missing cells
#   3 = perfect — all rows, columns, and values intact

os.makedirs(OUTPUTS_DIR, exist_ok=True)

def calculate_similarity(text1, text2):
    """Calculates string similarity ratio between 0 and 100"""
    if not text1 or not text2:
        return 0
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return round(matcher.ratio() * 100, 2)

def run_pdfplumber_extraction(pdf_path):
    start_time = time.time()
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        success = True
    except Exception as e:
        print(f"[-] pdfplumber error on {pdf_path}: {e}")
        success = False
    duration = time.time() - start_time
    return extracted_text, duration, success

def run_pymupdf_extraction(pdf_path):
    start_time = time.time()
    extracted_text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text()
            if page_text:
                extracted_text += page_text + "\n"
        success = True
    except Exception as e:
        print(f"[-] PyMuPDF error on {pdf_path}: {e}")
        success = False
    duration = time.time() - start_time
    return extracted_text, duration, success

def main():
    if not os.path.exists(PDFS_DIR):
        print(f"[-] Directory '{PDFS_DIR}' not found. Please create it and add PDFs.")
        return

    pdf_files = [f for f in os.listdir(PDFS_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"[-] No PDF files found in '{PDFS_DIR}'.")
        return

    print(f"[*] Found {len(pdf_files)} PDF files to process.")

    results = []

    for filename in pdf_files:
        pdf_path = os.path.join(PDFS_DIR, filename)
        pdf_name = os.path.splitext(filename)[0]

        ground_truth_path = os.path.join(PDFS_DIR, f"{pdf_name}_ground_truth.txt")
        ground_truth_text = ""
        if os.path.exists(ground_truth_path):
            with open(ground_truth_path, 'r', encoding='utf-8') as f:
                ground_truth_text = f.read()
            print(f"[+] Ground truth found for {filename}")

        # Create subdirectories for each library to match the required folder structure
        pdfplumber_dir = os.path.join(OUTPUTS_DIR, "pdfplumber")
        pymupdf_dir = os.path.join(OUTPUTS_DIR, "pymupdf")
        os.makedirs(pdfplumber_dir, exist_ok=True)
        os.makedirs(pymupdf_dir, exist_ok=True)

        # 1. pdfplumber
        print(f"[*] Extracting with pdfplumber: {filename}")
        plumber_text, plumber_time, plumber_ok = run_pdfplumber_extraction(pdf_path)

        out_file = os.path.join(pdfplumber_dir, f"{pdf_name}.txt")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(plumber_text)

        accuracy = calculate_similarity(ground_truth_text, plumber_text) if ground_truth_text else ""
        results.append({
            'pdf_name': pdf_name,
            'tool': 'pdfplumber',
            'time_sec': round(plumber_time, 4),
            'char_count': len(plumber_text),
            'accuracy': accuracy,
            'failed': not plumber_ok,
            'content_completeness': '',  # manual review
            'table_preservation': '',    # manual: 0=fail 1=partial 2=mostly 3=perfect
        })

        # 2. PyMuPDF
        print(f"[*] Extracting with PyMuPDF: {filename}")
        mupdf_text, mupdf_time, mupdf_ok = run_pymupdf_extraction(pdf_path)

        out_file = os.path.join(pymupdf_dir, f"{pdf_name}.txt")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(mupdf_text)

        accuracy = calculate_similarity(ground_truth_text, mupdf_text) if ground_truth_text else ""
        results.append({
            'pdf_name': pdf_name,
            'tool': 'pymupdf',
            'time_sec': round(mupdf_time, 4),
            'char_count': len(mupdf_text),
            'accuracy': accuracy,
            'failed': not mupdf_ok,
            'content_completeness': '',  # manual review
            'table_preservation': '',    # manual: 0=fail 1=partial 2=mostly 3=perfect
        })

    csv_file = os.path.join(OUTPUTS_DIR, "text_results.csv")
    fields = ['pdf_name', 'tool', 'time_sec', 'char_count', 'accuracy',
              'failed', 'content_completeness', 'table_preservation']

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[+] Processing complete! Summary results saved to {csv_file}")

if __name__ == "__main__":
    main()
