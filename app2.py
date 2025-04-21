import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import time

def duckduckgo_search(query, num_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://html.duckduckgo.com/html/?q={query}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"DuckDuckGo failed with status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", class_="result__a", limit=num_results)

    results = []
    for link in links:
        title = link.get_text()
        href = link['href']
        snippet_tag = link.find_parent("div", class_="result")
        snippet = snippet_tag.find("a", class_="result__snippet").get_text() if snippet_tag else ""
        results.append({
            "Title": title,
            "Snippet": snippet,
            "URL": href
        })
        time.sleep(0.5)  # gentle crawl

    return results

# Streamlit UI
st.set_page_config(page_title="News Scraper", layout="centered")
st.title("📰 Web Search Scraper (DuckDuckGo)")

keyword = st.text_input("Enter Keyword")
date = st.date_input("Select Date")
location = st.text_input("Enter Location")
num_results = st.slider("Number of Articles", min_value=5, max_value=30, value=10)

if st.button("Search"):
    if keyword and location:
        query = f"{keyword} {location} after:{date.strftime('%Y-%m-%d')}"
        st.write(f"Searching DuckDuckGo for: **{query}**")
        results = duckduckgo_search(query, num_results)

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
            st.warning("⚠️ No articles found.")
    else:
        st.warning("Please provide both keyword and location.")
