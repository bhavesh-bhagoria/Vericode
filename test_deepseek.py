from detector.services import analyze_code


code = """
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b
"""


result = analyze_code(code)

print(result)
