from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    # Пример перенаправления на порт 49152
    flow.request.port = 49152