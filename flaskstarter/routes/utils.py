from flask import Response

def response_with_headers(body, status=200, **headers)->Response:
    response = Response(body, status=status)
    for k, val in headers.items():
        response.headers[k] = val
    return response