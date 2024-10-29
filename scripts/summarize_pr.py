from openai import OpenAI
import requests
import os
import sys

# Load API keys from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_content(url):
    response = requests.get(url)
    return response.text

def summarize_changes(pr_diff):
    """
    Use OpenAI to generate a summary of the pull request changes.
    """
    prompt = f"Summarize the following code changes in a few sentences:\n\n{get_content(pr_diff)}"

    client = OpenAI(
        # This is the default and can be omitted
        api_key = OPENAI_API_KEY,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )

    response = chat_completion # openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=100)
    return response.choices[0].message.content.strip() # text.strip()

def post_summary_comment(pr_url, summary_text):
    """
    Post the summary of changes as a top-level comment on the GitHub pull request.
    """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {"body": f"### Pull Request Summary\n\n{summary_text}"}
    
    # Use the `issues` endpoint for PR comments instead of the review comment endpoint
    pr_comments_url = pr_url.replace('/pulls/', '/issues/') + "/comments"
    response = requests.post(pr_comments_url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Summary comment posted successfully.")
    else:
        print("Failed to post summary comment:", response.json())

def main():
    """
    Main function to handle command-line arguments for `pr_url` and `pr_diff`.
    """
    # Ensure the script receives `pr_url` and `pr_diff` arguments
    if len(sys.argv) < 3:
        print("Usage: python summarize_pr.py <pr_url> <pr_diff>")
        sys.exit(1)
    
    pr_url = sys.argv[1]
    pr_diff = sys.argv[2]

    # Generate summary of changes
    summary_text = summarize_changes(pr_diff)
    print("Generated Summary:", summary_text)

    # Post summary as a comment on the pull request
    post_summary_comment(pr_url, summary_text)

if __name__ == "__main__":
    main()
