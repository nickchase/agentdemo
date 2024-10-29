import requests
import openai
import os
import sys

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
REPO_NAME = "nickchase/agentdemo"

def detect_conflicts(base_branch, head_branch, repo_name):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    print(f"https://api.github.com/repos/{repo_name}/compare/{base_branch}...{head_branch}")
    response = requests.get(f"https://api.github.com/repos/{REPO_NAME}/compare/{base_branch}...{head_branch}", headers=headers)
    return response.json().get("conflicts", False)

def resolve_conflict_suggestion(conflict_details):
    openai.api_key = OPENAI_API_KEY
    prompt = f"Provide suggestions to resolve the following conflict:\n{conflict_details}"
    response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()

def post_conflict_suggestions(pr_url, conflict_suggestions):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"body": f"Conflict Resolution Suggestion:\n{conflict_suggestions}"}
    requests.post(f"{pr_url}/comments", headers=headers, json=data)

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
