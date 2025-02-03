import os
import re
import tiktoken
from openai import OpenAI
import json
from datetime import datetime
import shutil

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(text, model="gpt-4o-mini"):
    """Returns token count for a given text."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def read_html_file(file_path):
    """Reads the raw HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def save_to_txt(data, output_file="ai_news_articles.txt"):
    """Appends extracted articles to a text file."""
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(data + "\n\n")
    print(f"✅ Saved chunk to {output_file}")

def clean_html(html):
    """Removes unnecessary whitespace, script, and style tags."""
    html = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)  # Remove JavaScript
    html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL)  # Remove CSS
    html = re.sub(r"\s+", " ", html)  # Normalize whitespace
    return html.strip()

def split_into_chunks(text, max_tokens=100000):
    """Splits large text into smaller chunks under the model's limit."""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        chunk_tokens = tokens[start:start + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += max_tokens

    return chunks

def extract_articles(html_content, source_name):
    """Processes cleaned HTML content in chunks to extract structured articles."""
    html_content = clean_html(html_content)  # Clean HTML before sending to GPT
    print(f"\n🔹 Processing HTML ({len(html_content)} characters after cleaning)")

    chunks = split_into_chunks(html_content)
    print(f"🔹 Split into {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        print(f"\n📜 Processing Chunk {i+1}/{len(chunks)} ({len(chunk)} characters, {count_tokens(chunk)} tokens)")

        prompt = f"""Extract ALL news articles from the following raw webpage content from {source_name}.
Format the response in structured text, using this format:

Title: [Exact article headline]
Excerpt: [4-6 sentence summary of key points, quotes, and statistics]
Source URL: [Full article URL]
Category: [research/industry/ethics/funding/policy/general]
Published At: [YYYY-MM-DD]

Ensure all extracted information is accurate and directly from the text.
Do not generate any information that is not present in the source content.
Output should be plain text in the exact format shown above."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract structured news articles from webpages."},
                    {"role": "user", "content": f"{prompt}\n\n{chunk}"}
                ],
                temperature=0.3
            )

            result = response.choices[0].message.content
            print(f"✅ Chunk {i+1} extracted ({len(result)} characters, {count_tokens(result)} tokens)")
            
            if "Title:" in result:
                save_to_txt(result)
            else:
                print(f"⚠️ No articles found in chunk {i+1}. Skipping.")

        except Exception as e:
            print(f"❌ Error processing chunk {i+1}: {e}")

def load_raw_html():
    """Load raw HTML from crawler output file."""
    try:
        with open('../scrapy_crawler/ai_news_output.json', 'r', encoding='utf-8') as f:
            crawl_data = json.load(f)
            
        print(f"📂 Loaded {len(crawl_data)} pages from crawler output")
        
        # Save raw HTML files for debugging
        os.makedirs("raw_html", exist_ok=True)
        for page in crawl_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_html/{page['source']}_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(page['raw_html'])
            print(f"💾 Saved raw HTML to {filename}")
            
        return crawl_data

    except FileNotFoundError:
        print("❌ Error: ai_news_output.json not found in scrapy_crawler directory")
        return None
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in ai_news_output.json")
        return None
    except Exception as e:
        print(f"❌ Error loading crawler output: {str(e)}")
        return None

def clean_output_file(filename="ai_news_articles.txt"):
    """Clean output file and raw_html directory before starting."""
    try:
        # Clean output file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('')  # Empty the file
        print(f"🧹 Cleaned {filename}")
        
        # Clean raw_html directory
        raw_html_dir = "raw_html"
        if os.path.exists(raw_html_dir):
            shutil.rmtree(raw_html_dir)
            print(f"🧹 Removed {raw_html_dir} directory")
        os.makedirs(raw_html_dir)
        print(f"📁 Created fresh {raw_html_dir} directory")
        
    except Exception as e:
        print(f"⚠️ Error during cleanup: {str(e)}")

def main():
    """Main function to process raw HTML from JSON and extract articles."""
    print("🚀 Starting HTML processing...")
    
    # Clean output file first
    clean_output_file()
    
    # Load raw HTML files
    crawl_data = load_raw_html()
    if not crawl_data:
        print("❌ Failed to load HTML")
        return
        
    # Then process each page's HTML with GPT
    for page in crawl_data:
        print(f"\n🔍 Processing: {page['source']} from {page['url']}")
        
        try:
            extract_articles(page['raw_html'], page['source'])
            print(f"✅ Finished processing {page['source']}")
        except Exception as e:
            print(f"❌ Error processing {page['source']}: {str(e)}")
            continue
            
    print("\n✅ Processing complete")

if __name__ == "__main__":
    main()
