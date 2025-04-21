# streamlit_app.py
import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import io
import time

def get_articles(query, num_results=10):
    results = []
    urls = []
    
    try:
        urls = list(search(query, num_results=num_results, lang='en'))
    except Exception as e:
        st.error(f"❌ Error during Google Search: {e}")
        return results

    if not urls:
        st.warning("No URLs found. Try changing the keyword or reducing filters.")
        return results

    progress = st.progress(0)

    for i, url in enumerate(urls):
        try:
            r = requests.get(url, timeout=5, verify=False)
            soup = BeautifulSoup(r.content, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title"
            snippet_tag = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            snippet = snippet_tag['content'].strip() if snippet_tag and 'content' in snippet_tag.attrs else "No description"
            results.append({
                'Title': title,
                'Snippet': snippet,
                'URL': url
            })
        except Exception as e:
            results.append({
                'Title': 'Error fetching',
                'Snippet': str(e),
                'URL': url
            })

        progress.progress((i + 1) / len(urls))
        time.sleep(0.1)

    return results

# Streamlit UI
st.set_page_config(page_title="Web News Scraper", layout="centered")
st.title("📰 Web News Scraper")

keyword = st.text_input("Enter Keyword")
date = st.date_input("Select Date")
location = st.text_input("Enter Location")
num_results = st.slider("Number of Articles", min_value=5, max_value=50, value=10)

if st.button("🔍 Search and Save"):
    if keyword and location:
        search_query = f"{keyword} {location} after:{date.strftime('%Y-%m-%d')}"
        st.write(f"Searching for: **{search_query}**")
        data = get_articles(search_query, num_results)

        if data:
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Articles')
                writer.close()

            st.success("✅ Search complete. Download your file below:")
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No data found. Try a different keyword or fewer results.")
    else:
        st.warning("⚠️ Please provide both keyword and location.")
