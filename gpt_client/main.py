import requests
import re
import codecs
import logging
from requests.exceptions import RequestException

API_URL = "http://127.0.0.1:8000/api/ask"
QUESTION = "描述一下图片中的内容?"
COUNT = 5

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def decode_unicode(s):
    """Decode Unicode escape sequences."""
    return re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)

def parse_openai_stream(raw_response):
    """Parse the OpenAI stream response."""
    text_decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    pattern = re.compile(r'"content":\s*"(.*?)"')
    buffer = ''
    
    try:
        for chunk in raw_response.iter_content(chunk_size=1):
            if chunk:
                buffer += text_decoder.decode(chunk)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    for match in pattern.finditer(line):
                        text = match.group(1)
                        text = text.replace('\\n', '\n')
                        text = decode_unicode(text)
                        if text != '\0':
                            print(text, end='', flush=True)
    except Exception as e:
        logging.error(f"Error parsing stream: {str(e)}")
    finally:
        # Process any remaining data in the buffer
        for match in pattern.finditer(buffer):
            text = match.group(1)
            text = text.replace('\\n', '\n')
            text = decode_unicode(text)
            if text != '\0':
                print(text, end='', flush=True)

def main():
    payload = {
        "question": QUESTION,
        "count": COUNT
    }

    try:
        response = requests.post(API_URL, json=payload, stream=True, timeout=30)
        response.raise_for_status()
        parse_openai_stream(response)
    except RequestException as e:
        logging.error(f"HTTP request failed: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {str(e)}")