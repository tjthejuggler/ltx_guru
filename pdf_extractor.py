import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        print(f"\nAttempting to read: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {str(e)}"

def main():
    manual_dir = "manual"
    pdf_files = [f for f in os.listdir(manual_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(manual_dir, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        
        # Create output text file
        output_file = f"{pdf_path}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Extracted text saved to: {output_file}")

if __name__ == "__main__":
    main()
