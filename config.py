# PDF Translation Configuration

# Translation service: 'google', 'freegpt', 'openai', or 'localai'
# freegpt: Free ChatGPT API (recommended, free) - https://github.com/popjane/free_chatgpt_api
# google: Google Translate (free, may have rate limits)
# openai: OpenAI API (paid, requires API key)
# localai: LocalAI (self-hosted)
TRANSLATION_SERVICE = "freegpt"

# API key (required for freegpt/openai/localai services)
# For FreeGPT: Get free API key from: https://github.com/popjane/free_chatgpt_api
# For OpenAI: Get API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-QoXRGFKPtYlcZ5sD440fC2B6A06d4dD4AfD9E6A5E378DdD1"

# Base URL (for freegpt/localai services)
# For FreeGPT: https://free.v36.cm/v1/
# For LocalAI: http://localhost:8080/v1
BASE_URL = "https://free.v36.cm/v1/"

# Model name (for freegpt/openai/localai services)
# For FreeGPT: gpt-4o-mini (recommended), gpt-3.5-turbo-0125, gpt-3.5-turbo, etc.
# For OpenAI: gpt-3.5-turbo, gpt-4, gpt-4o-mini, etc.
# For LocalAI: depends on your local models
MODEL_NAME = "gpt-4o-mini"

# Translate text in images (requires OCR setup with pytesseract)
TRANSLATE_IMAGE_TEXT = False

# Output filename suffix
OUTPUT_SUFFIX = "_zh-TW"

# Translation cache (saves translations to avoid duplicate API calls)
USE_CACHE = True
CACHE_FILE = "translation_cache.json"

# Rate limiting (delay between API calls in seconds)
API_DELAY = 0.1

