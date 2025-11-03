#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator - Converts PDF to Traditional Chinese while preserving formatting
"""

import fitz  # PyMuPDF
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import re
import time

# Try to import deep-translator first (preferred, no httpx conflicts)
# Fallback to googletrans if deep-translator is not available
try:
    from deep_translator import GoogleTranslator
    USE_DEEP_TRANSLATOR = True
except ImportError:
    try:
        from googletrans import Translator
        USE_DEEP_TRANSLATOR = False
    except ImportError:
        raise ImportError(
            "No translation library found. Install one of:\n"
            "  pip install deep-translator  (recommended)\n"
            "  pip install googletrans==4.0.0rc1"
        )

# Try to import language detection library
try:
    from langdetect import detect, detect_langs, LangDetectException
    USE_LANGDETECT = True
except ImportError:
    USE_LANGDETECT = False
    print("Warning: langdetect not installed. Install with: pip install langdetect")
    print("Language auto-detection will be disabled. Defaulting to 'auto'.")


class PDFTranslator:
    """Translates PDF documents to Traditional Chinese while preserving formatting."""
    
    def __init__(self, translator_service: str = "google", api_key: Optional[str] = None, 
                 auto_detect_language: bool = True, base_url: Optional[str] = None):
        """
        Initialize PDF translator.
        
        Args:
            translator_service: Service to use ('google', 'openai', 'localai', or 'freegpt')
            api_key: API key for OpenAI/LocalAI/FreeGPT if using OpenAI-compatible service
            auto_detect_language: Whether to automatically detect source language
            base_url: Base URL for LocalAI or custom OpenAI-compatible API endpoint
        """
        self.translator_service = translator_service
        self.auto_detect_language = auto_detect_language and USE_LANGDETECT
        if translator_service == "google":
            if USE_DEEP_TRANSLATOR:
                # Don't set source language here - will be set dynamically
                self.translator_base = GoogleTranslator
            else:
                self.translator = Translator()
        else:
            self.translator = None
        self.api_key = api_key
        # Set default base_url for freegpt service
        if translator_service == "freegpt":
            self.base_url = base_url or "https://free.v36.cm/v1/"
        else:
            self.base_url = base_url
        self.model_name = None  # Will be set via command line if provided
        self.translation_cache = {}  # Cache translations to avoid duplicate API calls
        self.language_cache = {}  # Cache detected languages
        
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code (e.g., 'en', 'ja', 'fr', etc.) or 'zh' if Chinese
        """
        if not USE_LANGDETECT or not text or not text.strip():
            return 'auto'
        
        # Check cache first
        if text in self.language_cache:
            return self.language_cache[text]
        
        try:
            # If already Chinese, no need to detect
            if self._is_chinese(text):
                detected = 'zh'
            else:
                # Detect language
                detected = detect(text)
                # Map some common variations
                if detected == 'zh-cn':
                    detected = 'zh'
                elif detected == 'zh-tw':
                    detected = 'zh'
            
            # Cache the result
            self.language_cache[text] = detected
            return detected
            
        except LangDetectException:
            return 'auto'
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'auto'
    
    def translate_text(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to Traditional Chinese.
        
        Args:
            text: Text to translate
            source_lang: Source language code (if None, will auto-detect)
            
        Returns:
            Translated text in Traditional Chinese
        """
        if not text or not text.strip():
            return text
        
        # Skip if already Chinese
        if self._is_chinese(text):
            return text
            
        # Check cache first
        cache_key = f"{source_lang}:{text}" if source_lang else text
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Detect language if not provided and auto-detection is enabled
        if source_lang is None and self.auto_detect_language:
            source_lang = self.detect_language(text)
            if source_lang == 'zh':
                return text  # Already Chinese, no translation needed
        
        # Use 'auto' if no language detected or detection disabled
        if source_lang is None or source_lang == 'auto':
            source_lang = 'auto'
        
        try:
            if self.translator_service == "google":
                # Use Google Translate
                if USE_DEEP_TRANSLATOR:
                    # Create translator with detected source language
                    # deep-translator doesn't support 'auto', so we omit source if auto
                    if source_lang and source_lang != 'auto' and source_lang != 'zh':
                        translator = self.translator_base(source=source_lang, target='zh-TW')
                    else:
                        # Use 'auto' mode - deep-translator will auto-detect
                        translator = self.translator_base(source='auto', target='zh-TW')
                    translated = translator.translate(text)
                else:
                    # Use googletrans with auto-detection
                    if source_lang and source_lang != 'auto' and source_lang != 'zh':
                        result = self.translator.translate(text, src=source_lang, dest='zh-TW')
                    else:
                        result = self.translator.translate(text, dest='zh-TW')
                    translated = result.text
            elif self.translator_service in ["openai", "localai", "freegpt"]:
                # Use OpenAI API, LocalAI, or Free ChatGPT API (OpenAI-compatible)
                try:
                    from openai import OpenAI
                except ImportError:
                    raise ImportError(
                        "OpenAI package is not installed. Install it with: pip install openai"
                    )
                # For LocalAI, API key might not be required, but we'll use a placeholder if not provided
                if not self.api_key:
                    if self.translator_service == "localai":
                        # LocalAI often doesn't require API key, use placeholder
                        self.api_key = "not-needed"
                    elif self.translator_service == "freegpt":
                        raise ValueError("API key is required when using Free ChatGPT API service. Get your free API key from: https://github.com/popjane/free_chatgpt_api")
                    else:
                        raise ValueError("API key is required when using OpenAI service")
                
                # Configure client - use base_url if provided (for LocalAI, FreeGPT, or custom endpoints)
                if self.base_url:
                    client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                else:
                    client = OpenAI(api_key=self.api_key)
                
                # Use appropriate model name
                # Check if model_name attribute exists (set via command line)
                model_name = getattr(self, 'model_name', None)
                if not model_name:
                    if self.translator_service == "freegpt":
                        # Default model for Free ChatGPT API
                        model_name = "gpt-4o-mini"
                    elif self.translator_service == "openai":
                        model_name = "gpt-3.5-turbo"
                    else:
                        # For LocalAI, try to use a common model name or default
                        model_name = "gpt-3.5-turbo"  # Common default for LocalAI
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate the following text to Traditional Chinese, maintaining technical accuracy and formatting."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                translated = response.choices[0].message.content
            else:
                translated = text
                
            # Cache the translation
            self.translation_cache[cache_key] = translated
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
            return translated
            
        except Exception as e:
            print(f"Translation error for text '{text[:50]}...': {e}")
            return text  # Return original text if translation fails
    
    def extract_text_blocks(self, page) -> List[Dict]:
        """
        Extract text blocks with their positions and formatting information.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of text blocks with position and formatting info
        """
        blocks = []
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            bbox = span["bbox"]
                            blocks.append({
                                "text": text,
                                "bbox": bbox,
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"],
                                "color": span.get("color", 0),
                            })
        
        return blocks
    
    def translate_pdf(self, input_path: str, output_path: str, 
                     translate_images: bool = False) -> None:
        """
        Translate PDF to Traditional Chinese while preserving formatting.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file
            translate_images: Whether to translate text in images (OCR)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        print(f"Opening PDF: {input_path}")
        doc = fitz.open(input_path)
        total_pages = len(doc)
        print(f"Total pages: {total_pages}")
        
        for page_num in range(total_pages):
            print(f"Processing page {page_num + 1}/{total_pages}...")
            page = doc[page_num]
            
            # Extract text blocks
            text_blocks = self.extract_text_blocks(page)
            
            # Translate each text block
            for block in text_blocks:
                original_text = block["text"]
                
                # Skip if text is already in Chinese or contains only numbers/symbols
                if self._is_chinese(original_text) or not self._needs_translation(original_text):
                    continue
                
                # Detect language for this text block (optional, for info)
                detected_lang = None
                if self.auto_detect_language:
                    detected_lang = self.detect_language(original_text)
                    if detected_lang == 'zh':
                        continue  # Already Chinese, skip
                
                # Translate text with detected language
                translated_text = self.translate_text(original_text, source_lang=detected_lang)
                
                if translated_text != original_text:
                    # Replace text in PDF
                    self._replace_text_in_page(page, block, translated_text)
            
            # Optionally translate text in images
            if translate_images:
                self._translate_image_text(page)
        
        # Save translated PDF
        print(f"Saving translated PDF to: {output_path}")
        doc.save(output_path)
        doc.close()
        print("Translation completed!")
    
    def _is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def _needs_translation(self, text: str) -> bool:
        """Check if text needs translation (contains English letters)."""
        return bool(re.search(r'[a-zA-Z]', text))
    
    def _replace_text_in_page(self, page, block: Dict, new_text: str) -> None:
        """
        Replace text in page while preserving formatting.
        
        Args:
            page: PyMuPDF page object
            block: Text block dictionary with position and formatting info
            new_text: New text to insert
        """
        try:
            # Get text insertion point
            bbox = block["bbox"]
            x0, y0, x1, y1 = bbox
            
            # Calculate text width ratio to adjust font size if needed
            original_width = x1 - x0
            fontsize = block["size"]
            
            # Remove original text by redacting it
            rect = fitz.Rect(x0, y0, x1, y1)
            page.add_redact_annot(rect)
            page.apply_redactions()
            
            # Insert translated text at the same position
            # Use baseline position for text insertion
            point = fitz.Point(x0, y0 + block["size"] * 0.85)
            
            # Try to use a Chinese-supporting font
            # PyMuPDF has built-in fonts, try to use one that supports Chinese
            try:
                # Try common Chinese fonts available in PyMuPDF
                chinese_fonts = ["china-s", "china-ss", "china-t", "china-ts"]
                font_name = None
                for font in chinese_fonts:
                    try:
                        # Test if font is available by checking font list
                        available_fonts = page.get_fonts()
                        font_names = [f[3] for f in available_fonts]
                        if font in font_names or font.replace('-', '') in [f.replace('-', '') for f in font_names]:
                            font_name = font
                            break
                    except:
                        continue
                
                if not font_name:
                    # Use first available Chinese font or fallback to original
                    font_name = chinese_fonts[0] if chinese_fonts else block["font"]
            except:
                # Fallback to original font
                font_name = block["font"]
            
            # Determine text color
            color = block["color"]
            if color == 0:  # Default black
                color = (0, 0, 0)
            elif isinstance(color, int):
                # Convert color integer to RGB
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                color = (r/255.0, g/255.0, b/255.0)
            
            # Insert text with preserved formatting
            page.insert_text(
                point,
                new_text,
                fontsize=fontsize,
                fontname=font_name,
                color=color,
                render_mode=0
            )
            
        except Exception as e:
            print(f"Error replacing text '{block['text'][:30]}...': {e}")
            # Fallback: try simple text insertion
            try:
                page.add_redact_annot(fitz.Rect(block["bbox"]))
                page.apply_redactions()
            except:
                pass
    
    def _translate_image_text(self, page) -> None:
        """Translate text in images using OCR (placeholder for future implementation)."""
        # This would require OCR libraries like pytesseract
        # For now, skip image text translation
        pass


def main():
    """Main function to run PDF translation."""
    import argparse
    
    # Try to load configuration from config.py
    config_service = None
    config_api_key = None
    config_base_url = None
    config_model = None
    
    try:
        import config
        config_service = getattr(config, 'TRANSLATION_SERVICE', None)
        config_api_key = getattr(config, 'OPENAI_API_KEY', None)
        config_base_url = getattr(config, 'BASE_URL', None)
        config_model = getattr(config, 'MODEL_NAME', None)
    except ImportError:
        pass  # config.py not found, use defaults
    
    parser = argparse.ArgumentParser(
        description="Translate PDF to Traditional Chinese while preserving formatting"
    )
    parser.add_argument(
        "input_pdf",
        help="Path to input PDF file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output PDF file (default: input_filename_zh-TW.pdf)",
        default=None
    )
    parser.add_argument(
        "--service",
        choices=["google", "openai", "localai", "freegpt"],
        default=config_service or "freegpt",
        help="Translation service to use (default: freegpt - Free ChatGPT API)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for OpenAI/LocalAI/FreeGPT (if using OpenAI-compatible service). For FreeGPT, get free key from: https://github.com/popjane/free_chatgpt_api",
        default=None
    )
    parser.add_argument(
        "--base-url",
        help="Base URL for LocalAI or custom OpenAI-compatible API endpoint (e.g., http://localhost:8080/v1). For FreeGPT, default is https://free.v36.cm/v1/",
        default=None
    )
    parser.add_argument(
        "--model",
        help="Model name to use (for LocalAI/OpenAI/FreeGPT, e.g., 'gpt-4o-mini', 'gpt-3.5-turbo-0125', 'mistral-7b-instruct', 'gpt-3.5-turbo'). Default for FreeGPT: gpt-4o-mini",
        default=None
    )
    parser.add_argument(
        "--translate-images",
        action="store_true",
        help="Translate text in images (requires OCR setup)"
    )
    parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="Disable automatic language detection (will use 'auto' mode)"
    )
    
    args = parser.parse_args()
    
    # Use config.py values if command line arguments are not provided
    # Command line arguments take precedence over config.py
    service = args.service
    api_key = args.api_key or config_api_key
    base_url = args.base_url or config_base_url
    model = args.model or config_model
    
    # Set output path
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input_pdf)
        output_path = str(input_path.parent / f"{input_path.stem}_zh-TW.pdf")
    
    # Initialize translator
    translator = PDFTranslator(
        translator_service=service,
        api_key=api_key,
        auto_detect_language=not args.no_auto_detect,
        base_url=base_url
    )
    
    # Set model name if provided
    if model:
        translator.model_name = model
    
    # Translate PDF
    try:
        translator.translate_pdf(
            input_path=args.input_pdf,
            output_path=output_path,
            translate_images=args.translate_images
        )
        print(f"\n✓ Successfully translated PDF!")
        print(f"  Input:  {args.input_pdf}")
        print(f"  Output: {output_path}")
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

