import asyncio
import httpx
from datetime import date, datetime
from email.utils import parsedate_to_datetime

from app.collectors.bmkg import fetch_bmkg_weather

async def test_parse():
    print("Fetching from BMKG...")
    raw_data = await fetch_bmkg_weather()
    print("Got response. Parsing...")
    
    # Logic extracted from parse_and_store_weather to debug directly
    nowcast_list = raw_data.get("nowcast", [])
    if not isinstance(nowcast_list, list):
        print(f"Error: nowcast is not a list, it is {type(nowcast_list)}")
        return

    print(f"Nowcast items: {len(nowcast_list)}")
    daily_data = {}

    for i, item in enumerate(nowcast_list[:3]):
        print(f"\nItem {i+1}:")
        if not isinstance(item, dict):
            print("  Item is not dict")
            continue

        rss = item.get("rss", {})
        if not isinstance(rss, dict):
            print(f"  rss is not dict, it is {type(rss)}")
            continue

        title = rss.get("title", "")
        description = rss.get("description", "")
        pub_date_str = rss.get("pubDate", "")
        print(f"  title: {title}")
        print(f"  date str: {pub_date_str}")

        if not title and not description:
            print("  Missing title and description")
            continue

        fc_date = date.today()
        if pub_date_str:
            try:
                dt = parsedate_to_datetime(pub_date_str)
                fc_date = dt.date()
                print(f"  Parsed date: {fc_date}")
            except Exception as e:
                print(f"  Date parse error: {e}")

if __name__ == "__main__":
    asyncio.run(test_parse())
