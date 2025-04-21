import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import time
import random

# List of real user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/124.0"
]

HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Cache-Control": "no-cache"
}

def google_search(query, num_results=10):
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = HEADERS.copy()
    headers['User-Agent'] = random.choice(USER_AGENTS)

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Google search failed with status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3')
        snippet = g.find('div', class_='VwiC3b')
        link = g.find('a')['href'] if g.find('a') else None

        if title and link:
            results.append({
                "Title": title.get_text(),
                "Snippet": snippet.get_text() if snippet else "No snippet available",
                "URL": link
            })

        time.sleep(1)  # polite delay

    return results

# Streamlit UI
st.set_page_config(page_title="Google Scraper", layout="centered")
st.title("🔎 Google Search Scraper (No API)")

keyword = st.text_input("Enter Keyword")
date = st.date_input("Select Date")
location = st.text_input("Enter Location")
num_results = st.slider("Number of Articles", min_value=5, max_value=30, value=10)

if st.button("Search"):
    if keyword and location:
        query = f"{keyword} {location} after:{date.strftime('%Y-%m-%d')}"
        st.write(f"Searching Google for: **{query}**")
        results = google_search(query, num_results)

        if results:
            df = pd.DataFrame(results)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Articles')
                writer.close()

            st.success("✅ Search complete. Download the results below.")
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No articles found. Google may be rate-limiting.")
    else:
        st.warning("Please provide both keyword and location.")
