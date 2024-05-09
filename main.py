import requests
import argparse
import random
import string
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


#proxies = { 'http': 'http://localhost:8080', 'https': 'http://localhost:8080' }
proxies = { }

def random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def main():
    print(colored('[+] HeaderBonk by moopinger https://github.com/moopinger', 'green'))
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL to send requests to')
    parser.add_argument('-f', '--file', help='File containing URLs to send requests to')
    parser.add_argument('-c', '--canary', required=True, help='Canary value')
    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    elif args.file:
        with open(args.file, 'r') as f:
            urls = f.read().splitlines()
    else:
        print(colored('[-] Please provide a URL with the -u flag or a file with URLs using the -f flag', 'red'))
        return

    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36'
        }

        print(colored(f'[+] Sending requests to {url}', 'green'))

        # Read common headers from file
        with open('common-headers.txt', 'r') as f:
            common_headers = f.read().splitlines()

        try:
            base_response = requests.get(url, headers=headers, verify=False, proxies=proxies)
        except requests.exceptions.RequestException as e:
            print(colored(f'[-] Failed to send request: {e}', 'red'))
            continue
    
    
        base_response_size = len(base_response.text)
        base_response_status = base_response.status_code

        # Add headers from the base response that are not in common_headers to headers_list
        with open('headers.txt', 'r') as f:
            headers_list = f.read().splitlines()
        for header in base_response.headers.keys():
            if header not in common_headers:
                headers_list.append(header)
                print(colored(f'[+] Adding header: {header}', 'yellow'))  # Print the name of the header in yellow

        total_requests = len(headers_list)
        for i, header in enumerate(headers_list, start=1):
            headers[header] = args.canary
            params = {random_string(): args.canary}
            response = requests.get(url, headers=headers, params=params, verify=False, proxies=proxies
                                    )
            response_size = len(response.text)
            response_status = response.status_code

            print(f'Request number: {i}, Remaining requests: {total_requests - i}\r', end='', flush=True)

            if args.canary in response.text:
                print(colored(f'[+] Canary {args.canary} found in response for header: {header}', 'green'))

            elif response_status != base_response_status:
                print(colored(f'[+] Response status changed to {response_status} for header: {header}', 'green'))

            elif response_size != base_response_size:
                print(colored(f'[+] Response size changed from {base_response_size} to {response_size} for header: {header}', 'green'))

            del headers[header]  # Remove the custom header after the request is sent

if __name__ == "__main__":
    main()