from openai import OpenAI
import requests

import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def assess_performance(code_diff):
    # openai.api_key = OPENAI_API_KEY
    prompt = f"Review the following code for potential performance improvements:\n{code_diff}"

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

    # response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=150)
    # return response.choices[0].text.strip()

def post_performance_feedback(pr_url, performance_feedback):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"body": f"Performance Improvement Suggestions:\n{performance_feedback}"}
    requests.post(f"{pr_url}/comments", headers=headers, json=data)

def main(pr_url, pr_diff):
    performance_feedback = assess_performance(pr_diff)
    post_performance_feedback(pr_url, performance_feedback)
    print("Performance feedback posted to PR.")

# Example usage
# main("https://api.github.com/repos/nickchase/agentdemo/pulls/1", "diff content here")

