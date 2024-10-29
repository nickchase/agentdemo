import requests
from openai import OpenAI
import os
import sys

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
REPO_NAME = "nickchase/agentdemo"

def detect_conflicts(base_branch, head_branch, repo_name):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(f"https://api.github.com/repos/{REPO_NAME}/compare/{base_branch}...{head_branch}", headers=headers)
    print response.text
    return response.json().get("conflicts", False)

def resolve_conflict_suggestion(conflict_details):
    prompt = f"Provide suggestions to resolve the following conflict:\n{conflict_details}"
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

def post_conflict_suggestions(pr_url, conflict_suggestions):
    """
    Post conflict resolution suggestions as a top-level comment on the GitHub pull request.
    """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {"body": f"Conflict Resolution Suggestion:\n{conflict_suggestions}"}
    
    # Use the `issues` endpoint for PR comments instead of the review comment endpoint
    pr_comments_url = pr_url.replace('/pulls/', '/issues/') + "/comments"
    response = requests.post(pr_comments_url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Conflict resolution suggestion posted successfully.")
    else:
        print("Failed to post conflict resolution suggestion:", response.json())

def main():
    """
    Main function to handle command-line arguments for `pr_url`, `base_branch`, `head_branch`, and `repo_name`.
    """
    # Ensure the script receives `pr_url`, `base_branch`, `head_branch`, and `repo_name`
    if len(sys.argv) < 5:
        print("Usage: python conflict_detection.py <pr_url> <base_branch> <head_branch> <repo_name>")
        sys.exit(1)
        
    pr_url = sys.argv[1]
    base_branch = sys.argv[2]
    head_branch = sys.argv[3]
    repo_name = sys.argv[4]

    # Detect conflicts
    conflicts = detect_conflicts(base_branch, head_branch, repo_name)
    if conflicts:
        # Collect conflict details for OpenAI prompt
        conflict_details = "\n".join([file['filename'] for file in conflicts])
        conflict_suggestions = resolve_conflict_suggestion(conflict_details)
        
        # Post conflict resolution suggestions
        post_conflict_suggestions(pr_url, conflict_suggestions)
    else:
        print("No conflicts detected.")

if __name__ == "__main__":
    main()
