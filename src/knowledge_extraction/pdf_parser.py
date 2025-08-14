import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import io

def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using OCR. This is suitable for scanned PDFs.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        The extracted text from the PDF.
    """
    if not os.path.exists(pdf_path):
        return "Error: PDF file not found."

    doc = fitz.open(pdf_path)
    text = ""

    print(f"Starting OCR on {pdf_path} with {len(doc)} pages...")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Render page to an image (pixmap)
        # The higher the DPI, the better the OCR results, but the slower the process.
        pix = page.get_pixmap(dpi=300)

        # Convert pixmap to a PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        # Use pytesseract to do OCR on the image
        # Specify the language 'chi_sim' for Simplified Chinese
        try:
            page_text = pytesseract.image_to_string(image, lang='chi_sim')
            text += page_text + "\n\n" # Add page breaks for clarity
            print(f"  - Page {page_num + 1}/{len(doc)} processed.")
        except pytesseract.TesseractNotFoundError:
            return "Error: Tesseract is not installed or not in your PATH."
        except Exception as e:
            print(f"An error occurred during OCR on page {page_num + 1}: {e}")

    doc.close()
    return text

def convert_to_markdown(text: str) -> str:
    """
    Converts plain text to a simple Markdown format.
    """
    # Simply wrapping the text in a markdown block
    return f"## Extracted Content (OCR)\n\n```text\n{text}\n```"


if __name__ == '__main__':
    pdf_file_path = 'data/example.pdf'
    if os.path.exists(pdf_file_path):
        print(f"Processing {pdf_file_path} with OCR...")
        extracted_text = extract_text_with_ocr(pdf_file_path)

        if "Error:" in extracted_text:
            print(extracted_text)
        else:
            # Save the extracted text to a file for inspection
            with open('data/extracted_text_ocr.txt', 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print("Text extracted via OCR and saved to data/extracted_text_ocr.txt")

            # Convert to Markdown and save
            markdown_content = convert_to_markdown(extracted_text)
            with open('data/output_ocr.md', 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print("Markdown content saved to data/output_ocr.md")
    else:
        print(f"Error: The file {pdf_file_path} does not exist.")
