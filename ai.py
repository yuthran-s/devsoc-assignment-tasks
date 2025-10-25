import json
import requests
import sys


API_KEY = "API-KEY"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


INPUT_PROMPT_FILE = "ai.txt"
OUTPUT_JSON_FILE = "llm_responses.json"


def read_prompts_from_file(filename):
    print(f"Reading prompts from '{filename}'...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace, and filter out empty lines
            prompts = [line.strip() for line in f if line.strip()]
        
        if not prompts:
            print(f"Warning: No prompts found in '{filename}'.")
            
        return prompts
        
    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")
        # Exit the script if the input file is missing
        sys.exit(1) 
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)


def call_llm_api(prompt, url, api_key):
    headers = {
        'Content-Type': 'application/json',
    }
    
    # The API key is passed as a URL query parameter
    params = {
        'key': api_key,
    }
    
    # This is the specific payload structure required by the Gemini API
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status() 
        data = response.json()
        text = data.get('candidates', [{}])[0] \
                   .get('content', {}) \
                   .get('parts', [{}])[0] \
                   .get('text', '')
                   
        if not text:
            
            print(f"Warning: Received empty or unexpected response for prompt: {prompt}")
            return f"Error: No valid text response from API. Full response: {data}"
            
        return text.strip()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return f"Error: HTTP {response.status_code}"
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request: {req_err}")
        return f"Error: Request Exception"
    except (KeyError, IndexError, TypeError) as json_err:
        print(f"Error parsing JSON response: {json_err} - Response: {data}")
        return f"Error: Could not parse API response."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Error: Unexpected error"


def save_responses_to_json(data, filename):
    print(f"\nSaving responses to '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully saved {len(data)} responses.")
        
    except IOError as io_err:
        print(f"Error: Could not write to file '{filename}': {io_err}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")


def main():
    print("--- Starting LLM Prompt Processing ---")
    
    prompts = read_prompts_from_file(INPUT_PROMPT_FILE)
    
    if not prompts:
        print("No prompts to process. Exiting.")
        return
    all_responses = []
    total_prompts = len(prompts)
    
    print(f"Found {total_prompts} prompts. Calling API for each...")
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{total_prompts}] Processing prompt: '{prompt[:60]}...'")
        response_text = call_llm_api(prompt, API_URL, API_KEY)
        result_entry = {
            "prompt": prompt,
            "response": response_text
        }
        all_responses.append(result_entry)
    save_responses_to_json(all_responses, OUTPUT_JSON_FILE)
    
    print("--- Process Complete ---")
if __name__ == "__main__":
    main()



