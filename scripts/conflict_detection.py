import requests
import openai
import os

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
REPO_NAME = "nickchase/agentdemo"

def detect_conflicts(base_branch, head_branch):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    print(f"https://api.github.com/repos/{REPO_NAME}/compare/{base_branch}...{head_branch}")
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

def main(pr_url, base_branch, head_branch):
    if detect_conflicts(base_branch, head_branch):
        conflict_details = "List of conflict files and areas"
        conflict_suggestions = resolve_conflict_suggestion(conflict_details)
        post_conflict_suggestions(pr_url, conflict_suggestions)
        print("Conflict suggestions posted to PR.")
    else:
        print("No conflicts detected.")

# Example usage
# main("https://api.github.com/repos/nickchase/agentdemo/pulls/1", "main", "feature-branch")

