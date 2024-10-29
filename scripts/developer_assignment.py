import requests
from openai import OpenAI
import os
import sys

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
    # openai.api_key = OPENAI_API_KEY
    recent_contributors = get_recent_contributors(pr_files)
    prompt = f"Based on contributors {recent_contributors}, suggest a reviewer with relevant experience for files: {pr_files}."
    
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

def assign_reviewer(pr_url, reviewer):
    reviewer = "roadnick"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"reviewers": [reviewer]}
    requests.post(f"{pr_url}/requested_reviewers", headers=headers, json=data)

def main():
    """
    Main function to handle command-line arguments for `pr_url` and `repo_name`.
    """
    # Ensure the script receives `pr_url` and `repo_name` arguments
    if len(sys.argv) < 3:
        print("Usage: python developer_assignment.py <pr_url> <repo_name>")
        sys.exit(1)
    
    pr_url = sys.argv[1]
    repo_name = sys.argv[2]
    
    # Retrieve file paths affected by the PR
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(f"{pr_url}/files", headers=headers)
    
    if response.status_code == 200:
        file_paths = [file['filename'] for file in response.json()]
    else:
        print("Failed to fetch PR files:", response.json())
        sys.exit(1)
    
    # Recommend a reviewer and assign them to the PR
    reviewer = recommend_reviewer(file_paths)
    if reviewer:
        assign_reviewer(pr_url, reviewer)
    else:
        print("No suitable reviewer found.")

if __name__ == "__main__":
    main()
