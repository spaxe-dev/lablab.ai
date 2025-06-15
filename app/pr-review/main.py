from fastapi import FastAPI, Request
from github import Github
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize GitHub client with access token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

# Webhook endpoint to receive GitHub events
@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    # Check if the event is a pull request opening
    if payload.get("action") == "opened":
        pr_number = payload["pull_request"]["number"]
        repo_name = payload["repository"]["full_name"]
        # Process the pull request
        process_pr(repo_name, pr_number)
    return {"status": "received"}

def process_pr(repo_name: str, pr_number: int):
    # Get the repository and pull request
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Get the files changed in the PR
    files = pr.get_files()
    comments = []
    
    # Analyze Python files
    for file in files:
        if file.filename.endswith(".py"):
            # Get the file content
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
            issues = analyze_code(content, file.filename)
            if issues:
                comments.append(f"Issues in {file.filename}:\n{issues}")
    
    # Post comments to the PR
    if comments:
        pr.create_issue_comment("\n".join(comments))
    else:
        pr.create_issue_comment("No issues found in Python files.")

def analyze_code(code: str, filename: str) -> str:
    # Save code to a temporary file for pylint
    with open(f"temp_{filename}", "w") as f:
        f.write(code)
    
    # Run pylint and capture output
    from pylint.lint import Run
    from io import StringIO
    from contextlib import redirect_stdout
    
    output = StringIO()
    with redirect_stdout(output):
        Run([f"temp_{filename}", "--from-stdin"], do_exit=False)
    
    # Clean up temporary file
    os.remove(f"temp_{filename}")
    
    return output.getvalue()[:500]  # Limit output length for simplicity

# Run the app (for testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
