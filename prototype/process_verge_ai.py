import os
from openai import OpenAI
import json
from datetime import datetime
import tiktoken

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_incremental_results(results, output_file='processed_verge_ai.json'):
    """Save results to JSON file with pretty printing"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} articles to {output_file}")

def process_with_gpt(html_content):
    # Debug information
    print(f"\nInput HTML length: {len(html_content)} characters")
    token_count = count_tokens(html_content)
    print(f"Input token count: {token_count} tokens")
    
    # Split content into chunks of approximately 20K tokens
    chunk_size = 50000  # characters
    chunks = [html_content[i:i + chunk_size] for i in range(0, len(html_content), chunk_size)]
    print(f"Split into {len(chunks)} chunks")
    
    all_results = []
    
    # Try to load existing results
    output_file = 'processed_verge_ai.json'
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
            print(f"Loaded {len(all_results)} existing articles")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Starting fresh with no existing articles")
    
    for i, chunk in enumerate(chunks):
        print(f"\nProcessing chunk {i+1}/{len(chunks)}")
        print(f"Chunk size: {len(chunk)} characters")
        chunk_tokens = count_tokens(chunk)
        print(f"Chunk tokens: {chunk_tokens}")
        
        prompt = f"""You are a data analyst tasked with precisely extracting ALL news articles from The Verge webpage content. 
This is part {i+1} of {len(chunks)} of the webpage content. Extract all complete articles you can find in this section.

### **Data Extraction Requirements:**
1. **Extract ALL Articles:** Identify and extract every news article present in this section
2. **For Each Article Extract:**
   - The exact article headline
   - A comprehensive excerpt (4-6 sentences) including:
     * Main argument or thesis
     * Key developments or announcements
     * Important statistics or data points
     * Significant quotes from key figures
     * Impact or implications discussed
   - The complete article URL with full path
   - The exact publication date
3. **Process Every Article:** Extract all complete articles in this section

Format each article as a JSON object in an array:
   - title: The exact article headline
   - excerpt: Comprehensive summary including main points, key details, and significant quotes
   - source_url: The complete URL with full path (never just 'https://www.theverge.com')
   - source_name: Always 'The Verge'
   - category: Categorize based on content: research/industry/ethics/funding/policy/general
   - published_at: The exact date in YYYY-MM-DD format

CRITICAL REQUIREMENTS:
- Extract EVERY complete article you can find in this section
- Include key quotes, statistics, and specific details in each excerpt
- Extract the COMPLETE article URL including the full path for each article
- Use the EXACT publication date from each article
- Do not infer or generate any information not present in the source
- Ensure all extracted information is directly grounded in the input data

Please analyze the following section of webpage content and extract all articles with their required information:"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise data analyst focused on extracting ALL articles and their details from webpage content."},
                    {"role": "user", "content": f"{prompt}\n\n{chunk}"}
                ],
                temperature=0.3
            )
            
            # Debug information for response
            result = response.choices[0].message.content
            print(f"Response length: {len(result)} characters")
            print(f"Response token count: {count_tokens(result)} tokens")
            
            try:
                # Print the raw response for debugging
                print("Raw chunk response:")
                print(result)
                
                # Try to parse the JSON
                chunk_results = json.loads(result)
                if isinstance(chunk_results, list):
                    print(f"Found {len(chunk_results)} articles in chunk {i+1}")
                    all_results.extend(chunk_results)
                    print(f"Total articles so far: {len(all_results)}")
                    # Save after each successful chunk
                    save_incremental_results(all_results)
            except json.JSONDecodeError as e:
                print(f"Warning: Chunk {i+1} returned invalid JSON: {str(e)}")
                # Try to clean the response and parse again
                cleaned_result = result.strip()
                if cleaned_result.startswith('```json'):
                    cleaned_result = cleaned_result[7:]
                if cleaned_result.endswith('```'):
                    cleaned_result = cleaned_result[:-3]
                try:
                    chunk_results = json.loads(cleaned_result)
                    if isinstance(chunk_results, list):
                        print(f"Successfully parsed cleaned JSON. Found {len(chunk_results)} articles")
                        all_results.extend(chunk_results)
                        print(f"Total articles so far: {len(all_results)}")
                        # Save after each successful chunk
                        save_incremental_results(all_results)
                except json.JSONDecodeError:
                    print("Failed to parse even after cleaning")
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            # Save current progress even if there's an error
            if all_results:
                save_incremental_results(all_results)
    
    print(f"\nTotal articles found: {len(all_results)}")
    return json.dumps(all_results, indent=2)

def main():
    # Read the raw HTML file from the same directory
    html_content = read_html_file('raw_verge_ai.html')
    print(f"Raw HTML length: {len(html_content)} characters")
    
    # Process with GPT
    result = process_with_gpt(html_content)
    
    if result:
        try:
            parsed_result = json.loads(result)
            print("\nFinal Processed Article Information:")
            print(json.dumps(parsed_result, indent=2))
        except json.JSONDecodeError:
            print("\nError: Invalid JSON in final result")
            print(result)

if __name__ == "__main__":
    main() 