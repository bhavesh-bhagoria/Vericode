import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://ws-03yf1xwqq43yfujk.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
)
MODEL_NAME = os.getenv("QWEN_MODEL")
print("MODEL:", repr(MODEL_NAME))
# import os
# import requests

# api_key = os.getenv("QWEN_API_KEY")

# url = "https://dashscope-intl.aliyuncs.com/api/v1/models"

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# params = {
#     "page_no": 1,
#     "page_size": 100
# }

# response = requests.get(
#     url,
#     headers=headers,
#     params=params
# )

# data = response.json()

# for model in data["output"]["models"]:
#     print(model["model"])


def analyze_code(code):
    """
    Analyze source code for:
    - code quality
    - production readiness
    - security problems
    - suspicious/incorrect code
    - accidentally committed files
    - AI-generated likelihood
    """

    prompt = f"""
You are VeriCode, a code analysis assistant.

Analyze the code for:
- bugs and incorrect logic
- security vulnerabilities
- poor code quality
- unnecessary complexity
- missing error handling
- resource/timeout problems
- production-readiness issues
- files that should not be committed
- possible AI-generated patterns

Only report issues supported by the code. Do not invent problems or line numbers.

For each issue provide:
issue_number, severity, category, location, problem, reason, evidence, suggestion.

Also provide:
- ai_likelihood (0-100)
- summary
- production_status (READY, NEEDS_REVIEW, or NOT_READY)
- production_reason
- suspicious_files
- ai_indicators
- positive_observations

Return ONLY valid JSON in this format:

{{
    "ai_likelihood": 0,
    "summary": "",
    "production_status": "READY",
    "production_reason": "",
    "issues": [],
    "suspicious_files": [],
    "ai_indicators": [],
    "positive_observations": []
}}

SOURCE CODE:
{code}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are VeriCode, a professional code analysis and production-readiness assistant. Return only valid JSON when performing code analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

    )

    result = response.choices[0].message.content.strip()

    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
        "error": "The model returned invalid JSON",
        "raw_response": result
    }


def get_github_file(url):
    """
    Download source code from a GitHub file URL.
    """

    parts = url.rstrip("/").split("/")

    # Example:
    # https://github.com/user/repository/blob/main/app.py

    if "blob" not in parts:
        raise ValueError("Invalid GitHub file URL")

    blob_index = parts.index("blob")

    if len(parts) <= blob_index + 2:
        raise ValueError("Invalid GitHub file URL")

    username = parts[3]
    repository = parts[4]
    branch = parts[blob_index + 1]

    file_path = "/".join(parts[blob_index + 2:])

    raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{username}/{repository}/{branch}/{file_path}"
    )

    response = requests.get(
        raw_url,
        timeout=20
    )

    if response.status_code != 200:
        raise ValueError("Could not download GitHub file")

    return response.text


def analyze_github_file(url):
    """
    Download a GitHub file and analyze it.
    """

    code = get_github_file(url)

    result = analyze_code(code)

    return {
        "type": "file",
        "url": url,
        "result": result
    }


def chat_about_analysis(
    question,
    analysis_result,
    source_code,
    conversation_history=None
):
    if conversation_history is None:
        conversation_history = []

    system_prompt = """
You are the conversational assistant for VeriCode.

The user has already run a code analysis.

Your job is to help the user understand, question, and fix the findings from that analysis.

You have access to the analysis report and original source code.

If the user mentions an issue number, find that issue in the analysis report.

If the user says "why?", "how?", "what should I do?", or similar follow-up questions, use the previous conversation to understand what they are referring to.

Explain things in simple developer-friendly language.

When appropriate:

1. Explain what the issue means.
2. Explain why it was detected.
3. Show the relevant code.
4. Explain the risk.
5. Show how to fix it.
6. Explain what changes after the fix.

Do not invent issues or information that are not present in the provided analysis or source code.

If the analysis says something is only a possible problem, do not present it as a confirmed bug.

Do not use Markdown formatting such as **bold**, *italic*, backticks, headings, bullet points, tables, or code fences. Return simple plain text only.

Return normal conversational text.
Do not return JSON unless the user explicitly asks for JSON.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "system",
            "content": (
                "Here is the actual analysis report:\n\n"
                + json.dumps(analysis_result, indent=2)
            )
        },
        {
            "role": "system",
            "content": (
                "Here is the actual source code:\n\n"
                + source_code
            )
        }
    ]

    for message in conversation_history:
        messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    answer = response.choices[0].message.content

    answer = answer.replace("**", "")
    answer = answer.replace("__", "")
    answer = answer.replace("`", "")
    answer = answer.replace("#", "")

    return answer