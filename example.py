# PDF Translation Example Script

from pdf_translator import PDFTranslator

def translate_pdf_file(input_file: str, output_file: str = None):
    """
    Simple function to translate a PDF file.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file (optional)
    """
    if output_file is None:
        from pathlib import Path
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_zh-TW.pdf")
    
    # Create translator (using Google Translate by default)
    translator = PDFTranslator(translator_service="google")
    
    # Translate PDF
    translator.translate_pdf(
        input_path=input_file,
        output_path=output_file
    )
    
    print(f"Translation complete! Output saved to: {output_file}")

if __name__ == "__main__":
    # Example usage
    translate_pdf_file("activa_220_230_240_EN.pdf")

