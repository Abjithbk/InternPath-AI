import pdfminer.high_level
import io

def extract_text(file_bytes: bytes) -> str:
    try:
        with io.BytesIO(file_bytes) as pdf:
            return pdfminer.high_level.extract_text(pdf)
    except Exception:
        return ""