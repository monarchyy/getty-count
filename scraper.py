import os
import time
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style

# Settings
settings = {
    "base_url": "https://www.gettyimages",
    # Change the extension if you live in a different locale or use a VPN
    "domain_extension": ".com.au",
    # The current end poinst - end 2023
    "search_endpoint": "/search/2/image?family=editorial&phrase=",
}

# List of terms to scrape -- put your list of terms in here or create functionality to use a CSV.
terms_to_scrape = [
    # ADD search terms in here
]

# Set the output file path -- must be a .txt file
output_path = "output.txt"

# Add --clear flag to remove the output file existing text
def parse_arguments():
    parser = argparse.ArgumentParser(description='Getty Images Scraper')
    parser.add_argument('--clear', action='store_true', help='Clear the output file before running the script')
    return parser.parse_args()

# Function to replace spaces with %20
def format_name_for_url(name):
    return name.replace(" ", "%20")

# Scraper
def scrape_getty_images(name, file):
    # Remove spaces from the name that is passed
    formatted_name = format_name_for_url(name)

    # Joining the URL from the setting options
    url = f"{settings['base_url']}{settings['domain_extension']}{settings['search_endpoint']}{formatted_name}"

    # Set headers because it will Status 403 otherwise
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Request the page with headers being sent
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        button = soup.find('button', class_='mnBhCrcsnz9FtLKcXvlt HnvrM4M2DaqMbkR2Daoo')
        images_count_text = button.get_text(strip=True)
        number_of_images = int(images_count_text.replace(' Images', '').replace(',', ''))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_string = f"{name} (Getty Images) -- {number_of_images} Images -- {timestamp}"

        # Add a new line only if the file already contains data
        if file.tell() > 0:
            file.write('\n')

        file.write(output_string)
        print(f"{Fore.GREEN}Scraping successful for {name} (Getty Images) -- {Style.RESET_ALL} Images: {number_of_images}")
    else:
        print(f"{Fore.RED}Failed to pull data from {name} ({url}). Status code: {response.status_code}.{Style.RESET_ALL}")

############################## Script Runs Below ##############################

# Parse command line argument for clearing text output file
args = parse_arguments()

# Script start message
print(f"{Fore.BLUE}Getty Images Scraper is starting...{Style.RESET_ALL}")

if not output_path:
    print(f"{Fore.RED}Please set the output path...{Style.RESET_ALL}")
    exit()

if not os.path.exists(output_path):
    # Create the file if it does not exist on first run
    with open(output_path, 'w') as file:
        pass
    print(f"{Fore.GREEN}File created successfully.{Style.RESET_ALL}")

# Clear the output file if the --clear flag is provided
if args.clear and os.path.exists(output_path):
    os.remove(output_path)
    print("Output file cleared.")   

# Open the file before looping
with open(output_path, 'a') as output_file:

    if not terms_to_scrape:
        print(f"{Fore.RED}Please enter search terms...{Style.RESET_ALL}")
        exit()

    # Loop through the list of terms with tqdm progress bar
    for term in tqdm(terms_to_scrape, desc="Scraping progress", unit="term"):
        scrape_getty_images(term, output_file)
        # Trying to prevent being throttled by waiting one second between the next iteration
        time.sleep(1) 

    # Script completed
    print(f"{Fore.BLUE}Scraping complete. {output_path} generated{Style.RESET_ALL}")
