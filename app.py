import streamlit as st
import pandas as pd
import json
import os

# --- Page Config ---
st.set_page_config(
    page_title="YouTube Trending Explorer",
    page_icon="📊",
    layout="wide"
)

# --- Load Data Function ---
@st.cache_data
def load_data(country):
    file_csv = f"data/{country}videos.csv"
    file_json = f"data/{country}_category_id.json"

    if not os.path.exists(file_csv):
        st.error(f"Dataset for {country} not found!")
        return pd.DataFrame()

    df = pd.read_csv(file_csv)

    # Load category mapping if available
    if os.path.exists(file_json):
        with open(file_json) as f:
            cats = json.load(f)
        cat_map = {int(item['id']): item['snippet']['title'] for item in cats['items']}
        df['category_name'] = df['category_id'].map(cat_map)
    else:
        df['category_name'] = df['category_id']

    return df

# --- Title ---
st.title("📊 YouTube Trending Videos Dashboard")

st.markdown("""
Explore **YouTube trending videos across countries** by category, views, likes, and comments.  
Use the filters on the sidebar to interact with the data.
""")

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filters")

# Country selector (US + IN for now, extendable)
country = st.sidebar.selectbox("🌍 Choose Country Dataset", ["US", "IN"])

df = load_data(country)

if df.empty:
    st.stop()

cat = st.sidebar.selectbox("📂 Choose Category", ["All"] + sorted(df['category_name'].dropna().unique()))

if cat != "All":
    df = df[df['category_name'] == cat]

top_n = st.sidebar.slider("📈 Top N videos/channels", min_value=5, max_value=20, value=10)

# --- Display Table ---
st.subheader(f"📺 Top Trending Videos in {country}")
st.dataframe(df[['title','channel_title','category_name','views','likes','comment_count']].head(top_n))

# --- Charts ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top Channels by Views")
    top_channels = df.groupby('channel_title')['views'].sum().sort_values(ascending=False).head(top_n)
    st.bar_chart(top_channels)

with col2:
    st.subheader("🏆 Top Categories by Average Views")
    avg_views = df.groupby('category_name')['views'].mean().sort_values(ascending=False).head(top_n)
    st.bar_chart(avg_views)