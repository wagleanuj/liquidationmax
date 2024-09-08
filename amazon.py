import requests
from bs4 import BeautifulSoup


class AmazonScraper:
    def __init__(self, user_agent):
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        }

    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to retrieve the page: {response.status_code}")
            return None

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def search_product(self, product_name):
        search_url = f"https://www.amazon.ca/s?k={product_name.replace(' ', '+')}"
        html = self.get_html(search_url)
        if html:
            return self.parse_html(html)
        return None

    def extract_product_info(self, soup):
        products = []
        for item in soup.select(".s-main-slot .s-result-item"):
            title = item.select_one("h2 .a-text-normal")
            price = item.select_one(".a-price-whole")
            price_fraction = item.select_one(".a-price-fraction")
            rating = item.select_one(".a-icon-alt")
            product_url = item.select_one("h2 a.a-link-normal")
            brand_name = item.select_one("#bylineInfo_feature_div")

            if title and price and rating and product_url:
                products.append({
                    "title": title.get_text(strip=True),
                    "price": price.get_text(strip=True)+price_fraction.get_text(strip=True),
                    "rating": rating.get_text(strip=True),
                    "product_url": f"https://www.amazon.ca{product_url['href']}",
                    "brand_name": brand_name.get_text(strip=True) if brand_name else "N/A"
                })

        return products

    def scrape(self, product_name):
        soup = self.search_product(product_name)
        if soup:
            products = self.extract_product_info(soup)
            return products
        return []


# if __name__ == "__main__":
#     # Replace 'Your User-Agent' with your actual User-Agent string
#     scraper = AmazonScraper(user_agent="")

#     product_name = "Echo Dot (3rd Gen)"
#     products = scraper.scrape(product_name)

#     for product in products:
#         print(f"Title: {product['title']}")
#         print(f"Price: {product['price']}")
#         print(f"Rating: {product['rating']}")
#         print("---------------")
#         print(product)
5
