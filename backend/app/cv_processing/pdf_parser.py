from typing import Optional

def parse_pdf(file_path: str) -> str:
    """
    Parse text from a PDF file.
    """
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Parse text from PDF bytes.
    """
    try:
        import PyPDF2
        import io
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error parsing PDF bytes: {e}")
        return ""
