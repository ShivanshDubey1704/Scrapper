import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import time

# DuckDuckGo Search Function
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
    progress_bar = st.progress(0)

    for i, link in enumerate(links):
        title = link.get_text()
        href = link['href']
        snippet_tag = link.find_parent("div", class_="result")
        snippet = snippet_tag.find("a", class_="result__snippet").get_text() if snippet_tag else ""

        results.append({
            "Title": title,
            "Snippet": snippet,
            "URL": href
        })

        time.sleep(0.5)  # polite scraping delay
        progress_bar.progress((i + 1) / num_results)

    return results

# Bing Search Function
def bing_search(query, num_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.bing.com/search?q={query}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"Bing failed with status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("li", class_="b_algo", limit=num_results)

    results = []
    progress_bar = st.progress(0)

    for i, link in enumerate(links):
        title = link.find("h2").get_text()
        href = link.find("a")['href']
        snippet = link.find("p").get_text() if link.find("p") else "No snippet available"

        results.append({
            "Title": title,
            "Snippet": snippet,
            "URL": href
        })

        time.sleep(0.5)  # polite scraping delay
        progress_bar.progress((i + 1) / num_results)

    return results

# Google Search Function
def google_search(query, num_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"Google search failed with status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    progress_bar = st.progress(0)

    for i, g in enumerate(soup.find_all('div', class_='tF2Cxc')):
        title = g.find('h3').get_text() if g.find('h3') else "No title"
        snippet = g.find('div', class_='VwiC3b').get_text() if g.find('div', class_='VwiC3b') else "No snippet"
        link = g.find('a')['href'] if g.find('a') else None

        results.append({
            "Title": title,
            "Snippet": snippet,
            "URL": link
        })

        time.sleep(1)  # polite scraping delay
        progress_bar.progress((i + 1) / num_results)

    return results

# Streamlit UI
st.set_page_config(page_title="Multi Search Scraper", layout="centered")
st.title("📰 Multi-Search Engine Scraper")

# Input Fields
keyword = st.text_input("Enter Keyword")
date = st.date_input("Select Date")
location = st.text_input("Enter Location")
num_results = st.slider("Number of Articles", min_value=5, max_value=30, value=10)

# Select Search Engine
search_engine = st.radio(
    "Select Search Engine",
    ('Google', 'DuckDuckGo', 'Bing', 'All')
)

if st.button("Search"):
    if keyword and location:
        query = f"{keyword} {location} after:{date.strftime('%Y-%m-%d')}"
        st.write(f"Searching for: **{query}**")

        if search_engine == 'Google':
            results = google_search(query, num_results)
        elif search_engine == 'DuckDuckGo':
            results = duckduckgo_search(query, num_results)
        elif search_engine == 'Bing':
            results = bing_search(query, num_results)
        else:  # 'All'
            all_results = []
            all_results += google_search(query, num_results)
            all_results += duckduckgo_search(query, num_results)
            all_results += bing_search(query, num_results)
            results = all_results

        # Display Results & Download Option
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
