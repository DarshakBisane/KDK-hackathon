import io
from pypdf import PdfReader
from fastapi import HTTPException, status


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF byte stream.
    Validates that text content is present.
    If the PDF is scanned or empty, raises a friendly HTTP 400 error.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded resume file is empty. Please upload a valid PDF."
        )

    try:
        pdf_stream = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
        
        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF contains no pages."
            )

        extracted_text = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_text.append(page_text.strip())

        full_text = "\n\n".join(extracted_text).strip()

        # Check if text is completely empty or trivial (e.g. scanned image PDF)
        if not full_text or len(full_text) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="We couldn't read text from this PDF. Please upload a text-based resume PDF."
            )

        return full_text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to parse the PDF file. Please ensure it is a valid, uncorrupted PDF."
        )
