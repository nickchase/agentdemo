from openai import OpenAI
import os
import requests

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def suggest_tests(diff_text):
    # openai.api_key = OPENAI_API_KEY
    prompt = f"Suggest test cases for the following code changes:\n{diff_text}"
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

def add_test_suggestions(pr_url, test_suggestions):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"body": f"Suggested Tests:\n{test_suggestions}"}
    requests.post(f"{pr_url}/comments", headers=headers, json=data)

def main(pr_url, pr_diff):
    test_suggestions = suggest_tests(pr_diff)
    add_test_suggestions(pr_url, test_suggestions)
    print("Test suggestions added to PR.")

# Example usage
# main("https://api.github.com/repos/nickchase/agentdemo/pulls/1", "diff content here")

