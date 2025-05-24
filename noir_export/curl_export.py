from mitmproxy import http
from mitmproxy import ctx

def request(flow: http.HTTPFlow) -> None:
    # Формируем cURL-команду для текущего запроса
    curl_command = f'curl -X {flow.request.method} "{flow.request.url}"'
    
    # Добавляем заголовки
    for key, value in flow.request.headers.items():
        curl_command += f' -H "{key}: {value}"'
    
    # Добавляем тело запроса, если есть
    if flow.request.content:
        curl_command += f' --data-binary @-'
        # mitmdump перенаправит тело в stdin при выполнении curl
    
    # Выводим команду в stdout
    print(curl_command)