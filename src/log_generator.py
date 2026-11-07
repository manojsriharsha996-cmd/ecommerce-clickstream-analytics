"""
Module: log_generator.py
Description: Generates high-volume, realistic, anonymized e-commerce clickstream
logs reflecting real-world customer journeys, drop-offs, and conversions.
"""

import os
import random
import uuid
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

PRODUCTS = [
    {"product_id": "PROD_101", "name": "Wireless Noise Cancelling Headphones", "category": "Electronics", "price": 149.99},
    {"product_id": "PROD_102", "name": "Ultra-Wide Gaming Monitor 27-inch", "category": "Electronics", "price": 289.50},
    {"product_id": "PROD_103", "name": "Smart Fitness Watch Series 5", "category": "Electronics", "price": 99.00},
    {"product_id": "PROD_104", "name": "Ergonomic Mechanical Keyboard", "category": "Electronics", "price": 75.20},
    {"product_id": "PROD_201", "name": "Premium Cotton Crewneck T-Shirt", "category": "Apparel", "price": 24.99},
    {"product_id": "PROD_202", "name": "Slim Fit Denim Jeans", "category": "Apparel", "price": 54.00},
    {"product_id": "PROD_203", "name": "Breathable Athletic Running Shoes", "category": "Apparel", "price": 89.95},
    {"product_id": "PROD_204", "name": "Waterproof Outdoor Windbreaker", "category": "Apparel", "price": 68.50},
    {"product_id": "PROD_301", "name": "Cast Iron Non-Stick Skillet", "category": "Home & Kitchen", "price": 42.00},
    {"product_id": "PROD_302", "name": "Programmable Espresso Coffee Machine", "category": "Home & Kitchen", "price": 199.99},
    {"product_id": "PROD_303", "name": "HEPA Air Purifier for Large Rooms", "category": "Home & Kitchen", "price": 129.00},
    {"product_id": "PROD_401", "name": "Hydrating Facial Moisturizer Cream", "category": "Beauty & Health", "price": 28.00},
    {"product_id": "PROD_402", "name": "Sonic Electric Toothbrush Rechargeable", "category": "Beauty & Health", "price": 49.50},
    {"product_id": "PROD_501", "name": "Adjustable Dumbbell Pair 20kg", "category": "Sports & Fitness", "price": 119.00},
    {"product_id": "PROD_502", "name": "Anti-Slip Pro Yoga Mat with Strap", "category": "Sports & Fitness", "price": 32.50},
]

CHANNELS = ["Organic Search", "Google Ads", "Meta Ads", "Email Newsletter", "Direct", "Affiliate"]
CHANNEL_WEIGHTS = [0.30, 0.25, 0.20, 0.12, 0.08, 0.05]

DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_WEIGHTS = [0.62, 0.32, 0.06]

LOCATIONS = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi NCR", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
LOCATION_WEIGHTS = [0.22, 0.20, 0.18, 0.15, 0.10, 0.07, 0.05, 0.03]

def generate_clickstream_dataset(num_sessions=10000, start_date=None, output_csv="data/raw/clickstream_logs.csv"):
    """
    Simulates high-volume enterprise clickstream logs over a 30-day temporal window.
    """
    if start_date is None:
        start_date = datetime(2026, 9, 1, 0, 0, 0)
        
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # 3,500 unique users generating 10,000 sessions (shows repeat behavior and RFM traits)
    num_users = int(num_sessions * 0.38)
    user_pool = [f"USR_{10000 + i}" for i in range(num_users)]
    
    events = []
    
    print(f"[LogGenerator] Simulating {num_sessions} sessions across {num_users} users...")
    
    for sess_idx in range(num_sessions):
        session_id = f"SESS_{100000 + sess_idx}"
        user_id = random.choice(user_pool)
        channel = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0]
        device = random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0]
        location = random.choices(LOCATIONS, weights=LOCATION_WEIGHTS)[0]
        
        # Stagger session start across 30 days with diurnal peaks (higher traffic 10am-2pm, 7pm-10pm)
        day_offset = random.uniform(0, 30)
        raw_hour_p = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.06, 0.07,
                               0.08, 0.08, 0.07, 0.06, 0.05, 0.05, 0.06, 0.07, 0.08, 0.08,
                               0.06, 0.04, 0.03, 0.02], dtype=np.float64)
        hour_p = raw_hour_p / raw_hour_p.sum()
        hour = np.random.choice(range(24), p=hour_p)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        curr_time = start_date + timedelta(days=day_offset, hours=int(hour), minutes=minute, seconds=second)
        
        # Decide journey archetype:
        # 1: Bounce (30%) - 1 event and leave
        # 2: Casual Browse (35%) - 2-5 views, no cart
        # 3: Abandoned Cart (22%) - Views -> Add to cart -> maybe checkout -> drop
        # 4: Converted Purchase (13%) - Full funnel completion
        journey_type = random.choices(["bounce", "browse", "cart_abandon", "convert"], weights=[0.30, 0.35, 0.22, 0.13])[0]
        
        # Base event 1: landing
        landing_page = random.choice(["home", "category_page", "search_landing"])
        events.append({
            "event_id": str(uuid.uuid4())[:12],
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session_id,
            "user_id": user_id,
            "event_type": "page_view",
            "page_url": f"/{landing_page}",
            "product_id": None,
            "product_category": None,
            "price": 0.0,
            "dwell_time_seconds": random.randint(5, 35) if journey_type != "bounce" else random.randint(2, 10),
            "traffic_channel": channel,
            "device": device,
            "location": location
        })
        
        if journey_type == "bounce":
            continue
            
        # Continue journey
        num_product_views = random.randint(1, 9)
        viewed_products = random.choices(PRODUCTS, k=num_product_views)
        
        cart_items = []
        
        for prod in viewed_products:
            curr_time += timedelta(seconds=random.randint(10, 90))
            events.append({
                "event_id": str(uuid.uuid4())[:12],
                "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "user_id": user_id,
                "event_type": "product_view",
                "page_url": f"/product/{prod['product_id']}",
                "product_id": prod["product_id"],
                "product_category": prod["category"],
                "price": prod["price"],
                "dwell_time_seconds": random.randint(15, 180),
                "traffic_channel": channel,
                "device": device,
                "location": location
            })
            
            # Chance of adding to cart (both for abandons and converts, plus small chance for casual browsers)
            add_cart_chance = 0.70 if journey_type in ["cart_abandon", "convert"] else 0.15
            if random.random() < add_cart_chance:
                curr_time += timedelta(seconds=random.randint(5, 45))
                cart_items.append(prod)
                events.append({
                    "event_id": str(uuid.uuid4())[:12],
                    "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": session_id,
                    "user_id": user_id,
                    "event_type": "add_to_cart",
                    "page_url": f"/cart/add/{prod['product_id']}",
                    "product_id": prod["product_id"],
                    "product_category": prod["category"],
                    "price": prod["price"],
                    "dwell_time_seconds": random.randint(10, 50),
                    "traffic_channel": channel,
                    "device": device,
                    "location": location
                })
        
        # If cart_items were generated for abandon or convert
        if len(cart_items) > 0:
            if journey_type in ["cart_abandon", "convert"]:
                # Proceed to checkout
                curr_time += timedelta(seconds=random.randint(15, 60))
                events.append({
                    "event_id": str(uuid.uuid4())[:12],
                    "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": session_id,
                    "user_id": user_id,
                    "event_type": "checkout_start",
                    "page_url": "/checkout/step1",
                    "product_id": None,
                    "product_category": None,
                    "price": sum(p["price"] for p in cart_items),
                    "dwell_time_seconds": random.randint(25, 90),
                    "traffic_channel": channel,
                    "device": device,
                    "location": location
                })
                
                if journey_type == "convert":
                    curr_time += timedelta(seconds=random.randint(20, 80))
                    events.append({
                        "event_id": str(uuid.uuid4())[:12],
                        "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "session_id": session_id,
                        "user_id": user_id,
                        "event_type": "payment_info",
                        "page_url": "/checkout/payment",
                        "product_id": None,
                        "product_category": None,
                        "price": sum(p["price"] for p in cart_items),
                        "dwell_time_seconds": random.randint(30, 100),
                        "traffic_channel": channel,
                        "device": device,
                        "location": location
                    })
                    
                    curr_time += timedelta(seconds=random.randint(10, 45))
                    total_amount = round(sum(p["price"] for p in cart_items) * 1.05, 2)
                    events.append({
                        "event_id": str(uuid.uuid4())[:12],
                        "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "session_id": session_id,
                        "user_id": user_id,
                        "event_type": "purchase_completed",
                        "page_url": "/checkout/confirmation",
                        "product_id": None,
                        "product_category": None,
                        "price": total_amount,
                        "dwell_time_seconds": random.randint(15, 60),
                        "traffic_channel": channel,
                        "device": device,
                        "location": location
                    })

    df = pd.DataFrame(events)
    # Sort chronologically
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    df.to_csv(output_csv, index=False)
    print(f"[LogGenerator] Successfully generated {len(df):,} clickstream log rows across {num_sessions:,} sessions.")
    print(f"[LogGenerator] Saved to: {output_csv}")
    return df

if __name__ == "__main__":
    generate_clickstream_dataset(num_sessions=12000)
