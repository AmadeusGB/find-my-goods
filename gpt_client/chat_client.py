import requests
import re
import codecs

API_URL = "http://127.0.0.1:8000/api/ask"
QUESTION = "红色的袋子在哪里?"
COUNT = 5

# Function to decode Unicode escape sequences
def decode_unicode(s):
    return re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)

def parse_openai_stream(raw_response):
    text_decoder = codecs.getdecoder('utf-8')

    for chunk in raw_response.iter_content(chunk_size=512):
        if chunk:
            decoded_chunk = text_decoder(chunk)[0]
            matches = re.finditer(r'"content":\s*"(.*?)"', decoded_chunk)
            for match in matches:
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

    response = requests.post(API_URL, json=payload, stream=True)
    response.raise_for_status()

    parse_openai_stream(response)

if __name__ == "__main__":
    main()
