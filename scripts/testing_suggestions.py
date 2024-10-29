from openai import OpenAI
import os
import requests
import sys

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def suggest_tests(diff_text):
    # openai.api_key = OPENAI_API_KEY
    prompt = f"Create the code for suggested test cases for the following code changes:\n{diff_text}"
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
    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip() # text.strip()

def post_test_suggestions(pr_url, test_suggestions):
    """
    Post test suggestions as a top-level comment on the GitHub pull request.
    """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {"body": f"Suggested Tests:\n{test_suggestions}"}
    
    # Use the `issues` endpoint for PR comments instead of the review comment endpoint
    pr_comments_url = pr_url.replace('/pulls/', '/issues/') + "/comments"
    response = requests.post(pr_comments_url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Test suggestions posted successfully.")
    else:
        print("Failed to post test suggestions:", response.json())

def main():
    """
    Main function to handle command-line arguments for `pr_url` and `pr_diff`.
    """
    # Ensure the script receives `pr_url` and `pr_diff` arguments
    if len(sys.argv) < 3:
        print("Usage: python testing_suggestions.py <pr_url> <pr_diff>")
        sys.exit(1)
    
    pr_url = sys.argv[1]
    pr_diff = sys.argv[2]

    # Generate test suggestions and post them as a comment on the PR
    test_suggestions = suggest_tests(pr_diff)
    post_test_suggestions(pr_url, test_suggestions)

if __name__ == "__main__":
    main()
