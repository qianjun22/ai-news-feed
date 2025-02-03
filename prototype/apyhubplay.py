import http.client
import urllib.parse
import json
import os
import openai
from datetime import datetime
import time

# Load API Keys
def load_api_keys():
    # Load ApyHub API Key
    apyhub_key = os.getenv("APYHUB_API_KEY")
    if not apyhub_key:
        with open("apyhub_credentials.json", "r") as file:
            credentials = json.load(file)
        apyhub_key = credentials.get("token")

    # Load OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OpenAI API key not found in environment variables")

    return apyhub_key, openai_key

# Initialize API clients
APYHUB_API_KEY, OPENAI_API_KEY = load_api_keys()

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def save_api_response(response_data, site_name, api_type):
    """Save individual API response to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"responses/{site_name}_{api_type}_{timestamp}.json"
    
    try:
        with open(filename, "w") as f:
            json.dump(response_data, f, indent=2)
        print(f"💾 Saved {api_type} response to {filename}")
    except Exception as e:
        print(f"❌ Error saving {api_type} response: {str(e)}")

def extract_text(url, max_retries=3, timeout=60):
    """Extracts raw text from a webpage using ApyHub API with retries."""
    site_name = url.split("/")[-1]
    
    for attempt in range(max_retries):
        try:
            print(f"\n📥 Attempt {attempt + 1}/{max_retries} for text extraction: {url}")
            conn = http.client.HTTPSConnection("api.apyhub.com", timeout=timeout)
            encoded_url = urllib.parse.quote(url)
            headers = {'apy-token': APYHUB_API_KEY}

            print("🔑 Using ApyHub token:", APYHUB_API_KEY[:8] + "...")
            print("🔗 Requesting URL:", f"/extract/text/webpage?url={encoded_url}")
            
            conn.request("GET", f"/extract/text/webpage?url={encoded_url}", headers=headers)
            print(f"⏳ Waiting for response... (timeout: {timeout}s)")
            
            res = conn.getresponse()
            print(f"📊 Response status: {res.status} {res.reason}")
            
            data = res.read()
            response_json = json.loads(data.decode("utf-8"))
            
            # Save response immediately
            save_api_response(response_json, site_name, "text")
            
            if res.status != 200:
                print(f"❌ Error response: {response_json}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                return None
                
            print("✅ Text extraction successful")
            return response_json.get("data")

        except Exception as e:
            print(f"❌ Error in text extraction: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
                continue
            return None
        finally:
            conn.close()

def extract_links(url, max_retries=3, timeout=60):
    """Extracts raw links from a webpage using ApyHub API with retries."""
    site_name = url.split("/")[-1]
    
    for attempt in range(max_retries):
        try:
            print(f"\n🔍 Attempt {attempt + 1}/{max_retries} for links extraction: {url}")
            conn = http.client.HTTPSConnection("api.apyhub.com", timeout=timeout)
            headers = {
                'Content-Type': "application/json",
                'apy-token': APYHUB_API_KEY
            }
            payload = json.dumps({"url": url})

            print("🔑 Using ApyHub token:", APYHUB_API_KEY[:8] + "...")
            print("📦 Request payload:", payload)
            
            conn.request("POST", "/extract/links/url", payload, headers)
            print(f"⏳ Waiting for response... (timeout: {timeout}s)")
            
            res = conn.getresponse()
            print(f"📊 Response status: {res.status} {res.reason}")
            
            data = res.read()
            response_json = json.loads(data.decode("utf-8"))
            
            # Save response immediately
            save_api_response(response_json, site_name, "links")
            
            if res.status != 200:
                print(f"❌ Error response: {response_json}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                return None
                
            print("✅ Links extraction successful")
            return response_json.get("data", {}).get("links")

        except Exception as e:
            print(f"❌ Error in links extraction: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
                continue
            return None
        finally:
            conn.close()

def process_with_openai(text_response, links_response):
    """Process raw API responses with OpenAI."""
    prompt = (
        "You are an AI news aggregator. Your task is to provide a concise and fact-based summary of the latest AI-related news.\n\n"
        "### **Instructions:**\n"
        "1. **Gather AI News:** Focus on key developments, breakthroughs, investments, regulations, or controversies related to AI.\n"
        "2. **Include Trusted Sources:** Extract information from the provided content and links.\n"
        "3. **Summarize Each Story Clearly:**\n"
        "   - Title: Concise and engaging.\n"
        "   - Source: Include the publication name.\n"
        "   - Summary: 2-3 sentences summarizing the key points.\n"
        "4. **Ensure Relevance:** Prioritize major AI-related updates, industry announcements, or impactful developments.\n"
        "5. **Format Output as JSON:** Structure the data as follows:\n\n"
        "{\n"
        "    'title': 'Article title',\n"
        "    'excerpt': '2-3 sentence summary',\n"
        "    'source_url': 'URL of the article',\n"
        "    'source_name': 'Name of the publication',\n"
        "    'category': 'One of: research/industry/ethics/funding/policy/general',\n"
        "    'published_at': 'Publication date if available'\n"
        "}\n\n"
        f"Text API Response: {text_response}\n\n"
        f"Links API Response: {links_response}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI news aggregator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"⚠️ Error processing with OpenAI: {str(e)}")
        return None

def save_responses_to_files(text_response, links_response, site_name):
    """Save API responses to files for testing."""
    # Create a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save text response
    with open(f"responses/{site_name}_text_{timestamp}.json", "w") as f:
        json.dump(text_response, f, indent=2)
    
    # Save links response
    with open(f"responses/{site_name}_links_{timestamp}.json", "w") as f:
        json.dump(links_response, f, indent=2)

def process_news_websites(news_sites):
    """Process news websites and save responses."""
    for site in news_sites:
        print(f"\n🔍 Processing: {site}")
        site_name = site.split("/")[-1]
        
        # Get raw API responses
        text_response = extract_text(site)
        links_response = extract_links(site)
        
        if text_response and links_response:
            # Save responses to files
            save_responses_to_files(text_response, links_response, site_name)
            print(f"\n💾 Saved responses to files for {site_name}")

# News websites to process
news_websites = [
    "https://www.theverge.com/ai-artificial-intelligence",
]

# Create responses directory if it doesn't exist
os.makedirs("responses", exist_ok=True)

# Process websites
process_news_websites(news_websites)
