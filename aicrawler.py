import os
import openai
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client, Client
from crawler.config.settings import SUPABASE_CONFIG
import hashlib
import re

# Load OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Error: OPENAI_API_KEY is not set in the environment.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_CONFIG['url'], SUPABASE_CONFIG['key'])

# Path to your service account key file
SERVICE_ACCOUNT_FILE = './ai-news-feed-449705-afd28f77d175.json'

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def fetch_ai_news():
    prompt = (
        "You are an AI news aggregator. Your task is to provide a concise and fact-based summary of the latest AI-related news from the past 24 hours.\n\n"
        "### **Instructions:**\n"
        "1. **Gather AI News:** Focus on key developments, breakthroughs, investments, regulations, or controversies related to AI.\n"
        "2. **Include Trusted Sources:** Extract information from reputable news websites like VentureBeat, MIT Technology Review, Wired, The Verge, IEEE Spectrum, and other major tech publications.\n"
        "3. **Summarize Each Story Clearly:**\n"
        "   - Title: Concise and engaging.\n"
        "   - Source: Include the publication name (e.g., VentureBeat, Wired).\n"
        "   - Summary: 2-3 sentences summarizing the key points.\n"
        "4. **Ensure Relevance:** Prioritize major AI-related updates, industry announcements, or impactful developments.\n"
        "5. **Exclude Older News:** Only include news from the last 24 hours.\n\n"
        "### **Output Format Example:**\n"
        "1. **Title:** OpenAI Launches GPT-5 Early Beta Testing  \n"
        "   **Source:** VentureBeat  \n"
        "   **Summary:** OpenAI has begun early beta testing of GPT-5, featuring significant improvements in contextual memory and reasoning capabilities. The model is expected to be released in Q3 2025.\n\n"
        "2. **Title:** Google DeepMind Releases AlphaCode 2 for AI-Powered Coding  \n"
        "   **Source:** Wired  \n"
        "   **Summary:** Google DeepMind has unveiled AlphaCode 2, an upgraded AI model for software development, improving coding efficiency by 40%. This move intensifies competition with OpenAI's Codex.\n\n"
        "Please generate **at least 5 AI news summaries** following this format."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI news aggregator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        # Extract response
        news_summary = response.choices[0].message.content.strip()

        print(f"📢 AI News Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n{news_summary}")

    except Exception as e:
        print(f"⚠️ Error fetching AI news: {str(e)}")

def load_data_from_gsheet(sheet_url):
    # Authenticate and create a client
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Open the Google Sheet by URL
    spreadsheet = client.open_by_url(sheet_url)

    # Select the first sheet
    sheet = spreadsheet.sheet1

    # Get all values
    data = sheet.get_all_records()

    return data

def generate_hash(text):
    """Generate a normalized hash for text"""
    if not text:
        return None
    # Normalize: lowercase, remove punctuation, extra spaces
    normalized = re.sub(r'[^\w\s]', '', text.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return hashlib.md5(normalized.encode()).hexdigest()

def insert_data_to_supabase(data):
    for row in data:
        # Check if required fields are present
        if not row.get('title') or not row.get('source_url'):
            print("Skipping row due to missing required fields:", row)
            continue

        # Generate hashes for title and URL
        title_hash = generate_hash(row.get('title'))
        url_hash = generate_hash(row.get('source_url'))

        # Check for duplicates using hashes
        existing_article = supabase.table('articles').select('id').or_(
            f'title_hash.eq.{title_hash},url_hash.eq.{url_hash}'
        ).execute()

        if existing_article.data:
            print(f"Duplicate article found, skipping: {row.get('title')}")
            continue

        # Prepare the data for insertion
        article_data = {
            'title': row.get('title'),
            'excerpt': row.get('excerpt', ''),
            'content': row.get('content', ''),
            'source_url': row.get('source_url'),
            'source_name': row.get('source_name', ''),
            'category': row.get('category', 'General'),
            'published_at': row.get('published_at'),
            'status': 'active',
            'title_hash': title_hash,
            'url_hash': url_hash
        }

        # Insert into Supabase
        response = supabase.table('articles').insert(article_data).execute()
        if response.data:
            print(f"Inserted article: {article_data['title']}")
        else:
            print(f"Error inserting article: {response.error}")

if __name__ == "__main__":
    sheet_url = 'https://docs.google.com/spreadsheets/d/1EQFA1TIhwMNXKn6p1b1QkP0EKtg_AHWiev6jCkpLi5o/edit?usp=sharing'
    data = load_data_from_gsheet(sheet_url)
    
    # Insert data into Supabase
    insert_data_to_supabase(data)
