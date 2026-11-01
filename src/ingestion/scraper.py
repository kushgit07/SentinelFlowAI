import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def fetch_rbi_press_releases():
    url = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print(f"Checking for new regulations at: {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        releases = []
        links = soup.find_all('a')
        print(f"Found {len(links)} total links. Filtering for press releases...")
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            if "prid=" in href and len(title) > 10:
                full_url = href if href.startswith('http') else f"https://www.rbi.org.in/Scripts/{href}"
                if {"title": title, "link": full_url} not in releases:
                    releases.append({"title": title, "link": full_url})
        return releases
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    latest_news = fetch_rbi_press_releases()
    if not latest_news:
        print("Still nothing. We might need to inspect the page manually.")
    else:
        print(f"\nSuccess! Found {len(latest_news)} releases. Here are the top 5:")
        for i, item in enumerate(latest_news[:5], 1):
            print(f"{i}. {item['title']}\n   Source: {item['link']}\n")
