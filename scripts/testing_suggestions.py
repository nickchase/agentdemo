import openai
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def suggest_tests(diff_text):
    openai.api_key = OPENAI_API_KEY
    prompt = f"Suggest test cases for the following code changes:\n{diff_text}"
    response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

def add_test_suggestions(pr_url, test_suggestions):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"body": f"Suggested Tests:\n{test_suggestions}"}
    requests.post(f"{pr_url}/comments", headers=headers, json=data)

def main(pr_url, pr_diff):
    test_suggestions = suggest_tests(pr_diff)
    add_test_suggestions(pr_url, test_suggestions)
    print("Test suggestions added to PR.")

# Example usage
# main("https://api.github.com/repos/owner/repo/pulls/1", "diff content here")

