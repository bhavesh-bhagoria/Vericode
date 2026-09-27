from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from .services import analyze_github_file
from .github_service import (
    analyze_repository,
    analyze_repository_stream
)
from .services import chat_about_analysis

@csrf_exempt
def analyze_github(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405
        )

    try:

        data = json.loads(request.body)

        url = data.get("url")

        if not url:
            return JsonResponse(
                {
                    "error": "GitHub URL is required"
                },
                status=400
            )

        # GitHub file
        if "/blob/" in url:

            result = analyze_github_file(url)

            return JsonResponse(result)

        # GitHub repository
        else:

            response = StreamingHttpResponse(
                analyze_repository_stream(url),
                content_type="application/x-ndjson"
            )

            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"

            return response

    except Exception as error:

        return JsonResponse(
            {
                "error": str(error)
            },
            status=400
        )

@csrf_exempt
def chat_analysis(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        question = data.get("question", "")
        analysis_result = data.get("analysis", {})
        source_code = data.get("source_code", "")
        conversation_history = data.get("conversation_history", [])

        result = chat_about_analysis(
            question,
            analysis_result,
            source_code,
            conversation_history
        )

        return JsonResponse({
            "answer": result
        })

    except Exception as error:
        return JsonResponse(
            {"error": str(error)},
            status=400
        )