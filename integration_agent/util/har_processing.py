import json


def format_curl(request):
    method = request.get('method', 'GET')
    url = request.get('url', '')
    headers = request.get('headers', [])
    post_data = request.get('postData', {})

    curl_parts = [f"curl -X {method}"]

    for header in headers:
        curl_parts.append(f"-H '{header['name']}: {header['value']}'")

    if post_data:
        mime_type = post_data.get('mimeType', '')
        text = post_data.get('text', '')
        if mime_type and text:
            curl_parts.append(f"-H 'Content-Type: {mime_type}'")
            curl_parts.append(f"--data '{text}'")

    curl_parts.append(f"'{url}'")

    return ' '.join(curl_parts)

def format_response(response):
    status = response.get('status', '')
    status_text = response.get('statusText', '')
    headers = response.get('headers', [])
    content = response.get('content', {})

    response_parts = [f"HTTP/1.1 {status} {status_text}"]

    for header in headers:
        response_parts.append(f"{header['name']}: {header['value']}")

    response_parts.append('')  # Empty line between headers and body

    if content:
        response_parts.append(content.get('text', ''))

    return '\n'.join(response_parts)

# converts the har file to a dictionary of {{url: {request: "request", response: "response"}}}  
def parse_har_file_to_dict(har_file_path):
    parsed_data = {}

    with open(har_file_path, 'r') as file:
        har_data = json.load(file)

    entries = har_data.get('log', {}).get('entries', [])

    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url')

        if url:
            # Format request as cURL command
            curl_command = format_curl(request)

            # Format response as string
            response_string = format_response(response)

            parsed_data[url] = {
                'request': curl_command,
                'response': response_string
            }

    return parsed_data


def get_har_urls(har_file_path):
    # List to store URLs
    urls = []

    # Read the HAR file
    with open(har_file_path, 'r') as file:
        har_data = json.load(file)

    # Extract entries from the HAR data
    entries = har_data.get('log', {}).get('entries', [])

    # Process each entry
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url')

        if url:
            urls.append(url)
    # print(urls)
    return urls