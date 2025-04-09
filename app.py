import streamlit as st
import nltk
from nltk.corpus import wordnet
import requests
import time
from datetime import datetime

# Configure the app
st.set_page_config(page_title="SEO Keyword Research Tool", layout="wide")
nltk.download('wordnet')  # Download WordNet data (only needed once)

# Constants
MAX_KEYWORDS_TO_ANALYZE = 10  # Limit API calls for demo purposes
SERPAPI_URL = "https://serpapi.com/search.json"

# --- Cached Functions ---
@st.cache_data(show_spinner="Generating keyword variations...")
def generate_keywords(seed_keyword):
    """Generate keyword variations with caching"""
    synonyms = []
    for syn in wordnet.synsets(seed_keyword):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name().replace('_', ' '))  # Fix WordNet formatting
    return list(set(synonyms))  # Remove duplicates

@st.cache_data(ttl=3600)  # Cache results for 1 hour
def get_seo_metrics(keyword, api_key):
    """Get SEO metrics with error handling and caching"""
    try:
        params = {
            'q': keyword,
            'api_key': api_key,
            'num': 5  # Get top 5 results for analysis
        }
        response = requests.get(SERPAPI_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        
        data = response.json()
        
        # Extract metrics (adapt based on actual API response)
        search_volume = data.get("search_metadata", {}).get("total_results", "N/A")
        keyword_difficulty = data.get("keyword_difficulty", "N/A")
        
        return {
            "keyword": keyword,
            "search_volume": search_volume,
            "keyword_difficulty": keyword_difficulty,
            "success": True
        }
    except Exception as e:
        return {
            "keyword": keyword,
            "error": str(e),
            "success": False
        }

# --- UI Components ---
def display_metrics(metrics):
    """Display SEO metrics in a formatted way"""
    with st.expander(f"🔍 {metrics['keyword']}"):
        if metrics['success']:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estimated Search Volume", metrics['search_volume'])
            with col2:
                st.metric("Keyword Difficulty", metrics['keyword_difficulty'])
            
            # Add more metrics here as needed
            st.progress(min(int(metrics.get('keyword_difficulty', 0)), 100)
        else:
            st.error(f"❌ Failed to analyze: {metrics['error']}")

# --- Main App ---
st.title("🔎 SEO Keyword Research Automation Tool")
st.markdown("Generate keyword ideas and analyze their SEO potential")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("SERPAPI Key", type="password", help="Get your key from serpapi.com")
    analysis_limit = st.slider("Keywords to analyze", 1, 20, 5, help="Limit API calls")

# User input
seed_keyword = st.text_input("Enter a seed keyword:", placeholder="e.g. 'digital marketing'")

if seed_keyword:
    # Generate keywords
    with st.spinner("Generating keyword variations..."):
        keywords = generate_keywords(seed_keyword)
    
    if not keywords:
        st.warning("No keyword variations found. Try a different seed keyword.")
    else:
        # Display generated keywords
        st.subheader(f"Generated Keywords ({len(keywords)} found)")
        st.caption("Top suggestions:")
        st.write(', '.join(keywords[:15]))  # Show first 15 without analysis
        
        # Analysis section
        if api_key:
            st.subheader("SEO Analysis")
            st.caption(f"Analyzing top {analysis_limit} keywords...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for i, keyword in enumerate(keywords[:analysis_limit]):
                status_text.text(f"Analyzing: {keyword} ({i+1}/{analysis_limit})")
                
                # Get metrics with error handling
                metrics = get_seo_metrics(keyword, api_key)
                results.append(metrics)
                
                # Update progress
                progress_bar.progress((i + 1) / analysis_limit)
                time.sleep(0.2)  # Avoid rate limiting
            
            # Hide progress elements when done
            progress_bar.empty()
            status_text.empty()
            
            # Display all results
            for metrics in results:
                display_metrics(metrics)
            
            # Add export option
            if st.button("📥 Export Results as CSV"):
                # Implement CSV export here
                st.success("Export feature coming soon!")
        else:
            st.warning("Please enter your SERPAPI key to enable SEO analysis")
