from openai import OpenAI
import requests
import sys
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

def get_content(url):
    response = requests.get(url)
    return response.text

def assess_performance(code_diff):
    
    prompt = f"Review the following code for potential performance improvements:\n{get_content(code_diff)}"

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


    response = chat_completion # openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=500)
    print ("Response: ")
    print (response)
    return response.choices[0].message.content.strip() # text.strip()

    # response = openai.Completion.create(model="gpt-4", prompt=prompt, max_tokens=150)
    # return response.choices[0].text.strip()

def post_performance_feedback(pr_url, performance_feedback):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {"body": f"Performance Improvement Suggestions:\n{performance_feedback}"}
    
    print(f"PR URL = {pr_url}")
    print(f"headers = {headers}")
    print(f"data = {data}")

    response = requests.post(f"{pr_url}/comments", headers=headers, json=data)
    print(response.status_code)

def main():
    """
    Main function to handle command-line arguments for `pr_url` and `pr_diff`.
    """
    # Ensure the script receives `pr_url` and `pr_diff` arguments
    if len(sys.argv) < 3:
        print("Usage: python performance_review.py <pr_url> <pr_diff>")
        sys.exit(1)
        
    pr_url = sys.argv[1]
    pr_diff = sys.argv[2]

    # Process the performance feedback and post it to the PR
    performance_feedback = assess_performance(pr_diff)
    post_performance_feedback(pr_url, performance_feedback)
    print("Performance feedback posted to PR.")

if __name__ == "__main__":
    main()
