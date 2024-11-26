import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import langdetect
from langdetect import detect, LangDetectException  # For language detection

# Function to clean text (remove emojis and unwanted characters)
def clean_text(text):
    return re.sub(r'[^\w\s.,!?\'-]', '', text)

# Function to detect if the review is in English
def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False  # In case language detection fails

# Function to extract reviews and ratings from a single review page
def extract_reviews(soup):
    reviews = []
    for review_div in soup.find_all('div', {'data-hook': 'review'}):
        # Extract review body
        body = review_div.find('span', {'data-hook': 'review-body'})
        body_text = clean_text(body.text.strip()) if body else "No Review"
        
        # Check if the review is in English
        if not is_english(body_text):
            continue  # Skip non-English reviews
        
        # Extract review rating (individual rating for each review)
        rating_span = review_div.find('i', {'data-hook': 'review-star-rating'})
        rating = rating_span.text.strip().split(" ")[0] if rating_span else "No Rating"
        
        reviews.append({'Review': body_text, 'Rating': rating})
    return reviews

# Function to scrape product details (only product name in this case)
def scrape_product_details(base_url, headers):
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch product page, status code: {response.status_code}")
        return "Unknown Product"
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract product name using id="productTitle"
    product_name = soup.find('span', {'id': 'productTitle'})
    product_name = product_name.text.strip() if product_name else "Unknown Product"
    
    return product_name

# Main function to scrape reviews and product details
def scrape_amazon_reviews(base_url, max_reviews=100):
    all_reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    # Scrape product details
    product_name = scrape_product_details(base_url, headers)
    
    print(f"Scraping reviews for {product_name}...")
    
    page = 1
    while len(all_reviews) < max_reviews:
        print(f"Scraping page {page}...")
        url = f"{base_url}&pageNumber={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {page}, status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_reviews = extract_reviews(soup)
        
        all_reviews.extend(page_reviews)
        if len(all_reviews) >= max_reviews:
            all_reviews = all_reviews[:max_reviews]  # Trim excess reviews
            break
        
        page += 1
        time.sleep(2)  # To avoid overwhelming the server
    
    # Add product name to each review
    for review in all_reviews:
        review['Product Name'] = product_name
    
    # Return DataFrame instead of saving to CSV
    return pd.DataFrame(all_reviews)

# Example usage (optional, remove in production):
if __name__ == "__main__":
    base_url = "https://www.amazon.in/Sony-Bluetooth-Headphones-Multipoint-Connectivity/dp/B0BS1RT9S2"
    reviews_df = scrape_amazon_reviews(base_url, max_reviews=100)
    print(reviews_df)
