import json

def load_test_responses():
    """Load saved API responses for testing."""
    with open("responses/ai-artificial-intelligence_text_latest.json", "r") as f:
        text_response = json.load(f)
    
    with open("responses/ai-artificial-intelligence_links_latest.json", "r") as f:
        links_response = json.load(f)
    
    return text_response, links_response

def test_openai_processing():
    """Test OpenAI processing with saved responses."""
    text_response, links_response = load_test_responses()
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI news aggregator."},
            {"role": "user", "content": f"Text: {text_response}\n\nLinks: {links_response}"}
        ]
    )
    
    print(response.choices[0].message.content)

# Run test
test_openai_processing() 