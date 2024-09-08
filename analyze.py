import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import time

from amazon import AmazonScraper

# 1. Define Constants and API Headers
USER_AGENT = "Your User-Agent"
CACHED_PRICES = {}  # Dictionary to cache prices to reduce redundant API calls

# 2. Function to Scrape Amazon Prices (Optimized)


def get_amazon_price_and_url(product_name):
    if product_name in CACHED_PRICES:
        return CACHED_PRICES[product_name]
    scrapper = AmazonScraper("")
    details = scrapper.scrape(product_name)
    if not details[0]:
        raise Exception('could not do things')
    product = details[0]
    try:
        price = float(product['price'])
        CACHED_PRICES[product_name] = product['price']  # Cache the price
        print('got price', price)
        return {"price": price, "product": product}
    except AttributeError:
        return None

# 3. Function to Analyze Google Trends (With Throttling to Save API Calls)


def get_google_trends_score(product_name):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([product_name], cat=0,
                           timeframe='now 7-d', geo='', gprop='')
    trends_data = pytrends.interest_over_time()

    if not trends_data.empty:
        return trends_data[product_name].mean()
    return 0

# 4. Function to Adjust Price Based on Condition


def adjust_price_for_condition(base_price, condition):
    condition_multiplier = {
        "New": 1.0,
        "Like New": 0.9,
        "Used - Very Good": 0.8,
        "Used - Good": 0.7,
        "Used - Acceptable": 0.5,
    }
    return base_price * condition_multiplier.get(condition, 0.5)

# 5. Function to Calculate Total Cost and Profit Margin


def calculate_total_cost(base_price, shipping=0, fees=0):
    return base_price + shipping + fees


def calculate_profit_margin(resale_price, total_cost):
    return resale_price - total_cost


def is_good_to_resell(product_name, resale_price, total_cost, trends_score, min_profit=20, min_trends_score=4):
    profit_margin_percentage = ((resale_price - total_cost) / total_cost) * 100
    print("Profit Margin Percentage:", profit_margin_percentage, trends_score)
    if profit_margin_percentage >= min_profit:
        return True
    return False

# 7. Main Workflow


def analyze_product(product_name, base_price, condition, shipping=0, fees=0):
    # Step 1: Adjust price based on condition
    adjusted_price = adjust_price_for_condition(base_price, condition)

    # Step 2: Get the Amazon price (cached to save API calls)
    try:
        am = get_amazon_price_and_url(product_name)
    except:
        return {"ok": False}
    if am is None or "price" not in am:
        print(f"Could not find Amazon price for {product_name}")
        return {"ok": False}
    amazon_price = am["price"]
    # Step 3: Calculate total cost
    total_cost = calculate_total_cost(adjusted_price, shipping, fees)

    # Step 4: Get Google Trends score (throttle API calls)
    # trends_score = get_google_trends_score(product_name)
    # print(total_cost, trends_score)
    # Step 5: Decide if it's good to resell
    profit_margin_percentage = ((amazon_price - total_cost) / total_cost) * 100
    if is_good_to_resell(product_name, amazon_price, total_cost, 0):
        print(
            f"Good to resell: {product_name} with a profit margin of ${amazon_price - total_cost}")
        return {"ok": True, "profitMargin": profit_margin_percentage, "amazonPrice": amazon_price,  "product": am["product"]}
    else:
        print(f"Not worth reselling: {product_name}")
        return {"ok": False}

# 8. Example Execution
# if __name__ == "__main__":
#     product_name = "Echo Dot (3rd Gen)"
#     base_price = 20.0
#     condition = "Used - Good"
#     shipping_cost = 5.0
#     fees = 2.0

#     # Analyze the product
#     analyze_product(product_name, base_price, condition, shipping_cost, fees)

#     # Wait a few seconds to avoid hitting rate limits or excessive charges
#     time.sleep(3)
