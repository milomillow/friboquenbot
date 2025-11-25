# UTM remover bot to Wikipedia
# This bot removes UTM parameters from Wikipedia article
# Created by Friboquen
# Version: 1.0
# License: MIT

import pywikibot
import re
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

# Configure the site
site = pywikibot.Site('en', 'wikipedia')
site.login()  # Ensure the bot is logged in

def remove_utm_parameters(url):
    """Remove UTM parameters from a given URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Remove UTM parameters
    filtered_params = {k: v for k, v in query_params.items() if not k.startswith('utm_')}
    
    # Reconstruct the URL without UTM parameters
    new_query = urlencode(filtered_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    
    return new_url

def clean_text(text):
    """Clean the text by removing UTM parameters from all URLs."""

    # Regex para links externos do tipo [URL texto opcional]
    def replace_square_bracket_links(match):
        url = match.group(1)
        new_url = remove_utm_parameters(url)
        return match.group(0).replace(url, new_url)

    text = re.sub(r'\[([^\s\]]+)([^\]]*)\]', replace_square_bracket_links, text)

    # Regex para URLs em templates ou referências, ex: |url=http://example.com?utm_source=x
    def replace_template_links(match):
        url = match.group(1)
        new_url = remove_utm_parameters(url)
        return match.group(0).replace(url, new_url)

    text = re.sub(r'(\bhttps?://[^\s\|\}<>]+)', replace_template_links, text)

    return text

# Loop for all the pages in the main namespace (0)
for page in site.allpages(namespace=0):
    try:
        text = page.text
        new_text = clean_text(text)
        if new_text != text:
            page.text = new_text
            page.save(summary="Removed UTM parameters from URLs (robust version)", botflag=True)
            print(f"Updated page: {page.title()}")
        else:
            print(f"No UTM parameters found in page: {page.title()}")
    except Exception as e:
        print(f"Error processing page {page.title()}: {e}")
