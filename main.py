import requests
import argparse
import random
import string
from termcolor import colored
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36'

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
    parser.add_argument('-n', '--num-headers', type=int, default=10, help='Number of headers to add per request')
    
    counter = 1
    args = parser.parse_args()

    split = args.num_headers

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
            'User-Agent': user_agent
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

        if split > total_requests:
            split = total_requests

        batches_of_headers = []

        for i in range(0, total_requests, split):
            batches_of_headers.append(headers_list[i:i+split])

        print(colored(f'[+] Headers per request: {split}', 'yellow'))
        
        total_batches = len(batches_of_headers)

        for header_batch in batches_of_headers:
            print(f'Request Batch: {counter}/{total_batches}', end='\r')
            counter += 1

            headers = {
                'User-Agent': user_agent
            }

            for header in header_batch:
                headers[header] = args.canary

            params = {random_string(): args.canary}
            response = requests.get(url, headers=headers, params=params, verify=False, proxies=proxies)
            response_size = len(response.text)
            response_status = response.status_code

            #Did batch trigger
            if args.canary in response.text or response_status != base_response_status or response_size != base_response_size:



                for header in header_batch:
                    headers = {
                        'User-Agent': user_agent
                    }

                    headers[header] = args.canary
                    params = {random_string(): args.canary}
                    response = requests.get(url, headers=headers, params=params, verify=False, proxies=proxies)
                    response_size = len(response.text)
                    response_status = response.status_code

                    

                    if args.canary in response.text:
                        print(colored(f'[+] Canary {args.canary} found in response for header: {header}', 'green'))

                    elif response_status != base_response_status:
                        print(colored(f'[+] Response status changed to {response_status} for header: {header}', 'green'))

                    elif response_size != base_response_size:
                        print(colored(f'[+] Response size changed from {base_response_size} to {response_size} for header: {header}', 'green'))

                    del headers[header]



if __name__ == "__main__":
    main()
