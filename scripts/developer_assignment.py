import requests
import openai
import os

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_NAME = "nickchase/agentdemo"  # Format: "owner/repo"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def get_potential_reviewers(pr_url):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(f"https://api.github.com/repos/{REPO_NAME}/collaborators", headers=headers)
    return [collaborator['login'] for collaborator in response.json()]

def get_recent_contributors(file_paths):
    contributors = {}
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    for file in file_paths:
        response = requests.get(f"https://api.github.com/repos/{REPO_NAME}/commits?path={file}", headers=headers)
        if response.status_code == 200:
            commits = response.json()
            for commit in commits:
                author = commit['commit']['author']['name']
                if author in contributors:
                    contributors[author] += 1
                else:
                    contributors[author] = 1
    return sorted(contributors, key=contributors.get, reverse=True)

def recommend_reviewer(pr_files):
    openai.api_key = OPENAI_API_KEY
    recent_contributors = get_recent_contributors(pr_files)
    prompt = f"Based on contributors {recent_contributors}, suggest a reviewer with relevant experience for files: {pr_files}."
    response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()

def assign_reviewer(pr_url, reviewer):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"reviewers": [reviewer]}
    requests.post(f"{pr_url}/requested_reviewers", headers=headers, json=data)

def main(pr_url, pr_files):
    reviewer = recommend_reviewer(pr_files)
    if reviewer:
        assign_reviewer(pr_url, reviewer)
        print(f"Reviewer {reviewer} assigned to PR.")
    else:
        print("No suitable reviewer found.")

# Example usage
# main("https://api.github.com/repos/owner/repo/pulls/1", ["src/file1.py", "src/file2.py"])

