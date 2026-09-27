import json
import os
import shutil
import subprocess
import tempfile

from .services import analyze_code


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".html",
    ".css",
    ".sql",
    ".txt",
    ".md",
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}


def clone_repository(github_url):
    temp_directory = tempfile.mkdtemp(prefix="github_repo_")

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                github_url,
                temp_directory
            ],
            check=True
        )

        return temp_directory

    except Exception:
        shutil.rmtree(
            temp_directory,
            ignore_errors=True
        )

        raise ValueError(
            "Could not clone GitHub repository"
        )


def get_source_files(repository_path):

    source_files = []

    for root, directories, files in os.walk(
        repository_path
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in ALLOWED_EXTENSIONS:
                continue

            file_path = os.path.join(
                root,
                filename
            )

            source_files.append(file_path)

    return source_files


def analyze_repository(github_url):

    repository_path = clone_repository(
        github_url
    )

    try:

        source_files = get_source_files(
            repository_path
        )

        results = []

        for file_path in source_files:

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    code = file.read()

                code = code[:15000]

                result = analyze_code(code)

                relative_path = os.path.relpath(
                    file_path,
                    repository_path
                )

                results.append({
                    "file": relative_path,
                    "result": result
                })

            except Exception as error:

                results.append({
                    "file": os.path.relpath(
                        file_path,
                        repository_path
                    ),
                    "result": f"Could not analyze file: {error}"
                })

        return {
            "type": "repository",
            "url": github_url,
            "total_files": len(results),
            "files": results
        }

    finally:

        shutil.rmtree(
            repository_path,
            ignore_errors=True
        )


def analyze_repository_stream(github_url):

    repository_path = clone_repository(
        github_url
    )

    try:

        source_files = get_source_files(
            repository_path
        )

        total_files = len(source_files)

        yield json.dumps({
            "type": "start",
            "total_files": total_files
        }) + "\n"

        results = []

        for index, file_path in enumerate(
            source_files,
            start=1
        ):

            relative_path = os.path.relpath(
                file_path,
                repository_path
            )

            yield json.dumps({
                "type": "file_start",
                "file": relative_path,
                "index": index,
                "total": total_files
            }) + "\n"

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    code = file.read()

                code = code[:15000]

                result = analyze_code(code)

                results.append({
                    "file": relative_path,
                    "result": result
                })

                yield json.dumps({
                    "type": "file_complete",
                    "file": relative_path,
                    "index": index,
                    "total": total_files,
                    "result": result
                }) + "\n"

            except Exception as error:

                error_message = (
                    f"Could not analyze file: {error}"
                )

                results.append({
                    "file": relative_path,
                    "result": error_message
                })

                yield json.dumps({
                    "type": "file_error",
                    "file": relative_path,
                    "index": index,
                    "total": total_files,
                    "error": error_message
                }) + "\n"

        yield json.dumps({
            "type": "complete",
            "repository": {
                "type": "repository",
                "url": github_url,
                "total_files": len(results),
                "files": results
            }
        }) + "\n"

    finally:

        shutil.rmtree(
            repository_path,
            ignore_errors=True
        )