from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from .services import analyze_github_file
from .github_service import (
    analyze_repository,
    analyze_repository_stream
)
from .services import chat_about_analysis
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Analysis


def get_authenticated_user(request):
    authentication = JWTAuthentication()
    result = authentication.authenticate(request)

    if result is None:
        return None

    user, token = result
    return user


@csrf_exempt
def analyze_github(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only POST requests are allowed"
            },
            status=405
        )

    user = get_authenticated_user(request)

    if user is None:
        return JsonResponse(
            {
                "error": "Authentication required"
            },
            status=401
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

            analysis = Analysis.objects.create(
                user=user,
                github_url=url,
                analysis_result=result,
                source_code=""
            )

            return JsonResponse({
                "analysis_id": analysis.id,
                "result": result
            })

        # GitHub repository
        else:

            def stream_with_save():

                for line in analyze_repository_stream(url):

                    # Send the original stream to frontend
                    yield line

                    try:

                        event = json.loads(line)

                        if event.get("type") == "complete":

                            repository = event.get(
                                "repository",
                                {}
                            )

                            Analysis.objects.create(
                                user=user,
                                github_url=url,
                                analysis_result=repository,
                                source_code=""
                            )

                    except Exception:
                        pass

            response = StreamingHttpResponse(
                stream_with_save(),
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
def list_analyses(request):

    if request.method != "GET":
        return JsonResponse(
            {
                "error": "Only GET requests are allowed"
            },
            status=405
        )

    user = get_authenticated_user(request)

    if user is None:
        return JsonResponse(
            {
                "error": "Authentication required"
            },
            status=401
        )

    analyses = Analysis.objects.filter(
        user=user
    ).order_by("-created_at")

    result = []

    for analysis in analyses:

        result.append({
            "id": analysis.id,
            "github_url": analysis.github_url,
            "analysis_result": analysis.analysis_result,
            "source_code": analysis.source_code,
            "created_at": analysis.created_at
        })

    return JsonResponse({
        "analyses": result
    })

    
@csrf_exempt
def chat_analysis(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    user = get_authenticated_user(request)

    if user is None:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    try:
        data = json.loads(request.body)

        analysis_id = data.get("analysis_id")
        question = data.get("question", "")
        conversation_history = data.get(
            "conversation_history",
            []
        )

        if not analysis_id:
            return JsonResponse(
                {"error": "analysis_id is required"},
                status=400
            )

        if not question:
            return JsonResponse(
                {"error": "Question is required"},
                status=400
            )

        try:
            analysis = Analysis.objects.get(
                id=analysis_id
            )
        except Analysis.DoesNotExist:
            return JsonResponse(
                {"error": "Analysis not found"},
                status=404
            )

        # Check ownership
        if analysis.user != user:
            return JsonResponse(
                {"error": "You do not have access to this analysis"},
                status=403
            )

        result = chat_about_analysis(
            question,
            analysis.analysis_result,
            analysis.source_code,
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
