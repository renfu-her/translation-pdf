# PDF Translation Configuration

# Translation service: 'google' or 'openai'
TRANSLATION_SERVICE = "google"

# OpenAI API key (required if using OpenAI service)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = ""

# Translate text in images (requires OCR setup with pytesseract)
TRANSLATE_IMAGE_TEXT = False

# Output filename suffix
OUTPUT_SUFFIX = "_zh-TW"

# Translation cache (saves translations to avoid duplicate API calls)
USE_CACHE = True
CACHE_FILE = "translation_cache.json"

# Rate limiting (delay between API calls in seconds)
API_DELAY = 0.1

