#!/usr/bin/env python3
import os
from PyPDF2 import PdfReader
import sys
import re

def clean_text(text):
    """Clean and format extracted text."""
    # Remove extra spaces between characters
    text = re.sub(r'\s*(?=[.,!?])', '', text)  # Remove spaces before punctuation
    text = re.sub(r'(?<=\w)\s+(?=\w)', ' ', text)  # Single space between words
    
    # Fix special characters
    text = text.replace('ö', 'f')  # Fix common OCR error
    text = text.replace('´', "'")  # Fix quotes
    text = text.replace('„', '"')  # Fix quotes
    text = text.replace('"', '"')  # Fix quotes
    text = text.replace('ø', 'f')  # Fix common OCR error
    
    # Fix specific patterns
    text = re.sub(r'(?<=\w)\'s\s+', "'s ", text)  # Fix possessives
    text = re.sub(r'Add\'', 'Add ', text)  # Fix common pattern
    text = re.sub(r'Delete\'', 'Delete ', text)  # Fix common pattern
    text = re.sub(r'Move\'', 'Move ', text)  # Fix common pattern
    text = re.sub(r'Replace\'', 'Replace ', text)  # Fix common pattern
    
    # Clean up lines
    lines = []
    for line in text.split('\n'):
        # Remove excessive spaces
        line = ' '.join(word for word in line.split() if word)
        if line:
            lines.append(line)
    
    return '\n'.join(lines)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        print(f"\nProcessing: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = clean_text(page_text)
                    text.append(f"--- Page {i+1} ---\n{cleaned_text}")
            except Exception as e:
                text.append(f"Error extracting page {i+1}: {str(e)}")
        return "\n\n".join(text)
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def save_text(text, output_path):
    """Save extracted text to a file with UTF-8 encoding."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved text to: {output_path}")
    except Exception as e:
        print(f"Error saving {output_path}: {str(e)}")

def main():
    manual_dir = "manual"
    if not os.path.exists(manual_dir):
        print(f"Error: Directory '{manual_dir}' not found")
        sys.exit(1)

    pdf_files = [f for f in os.listdir(manual_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {manual_dir}")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF files")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(manual_dir, pdf_file)
        output_path = pdf_path + ".txt"
        
        text = extract_text_from_pdf(pdf_path)
        save_text(text, output_path)

if __name__ == "__main__":
    main()
