import streamlit as st
import requests
import random
import time

st.set_page_config(
    page_title="Random Black Cats",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    body {
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    .main {
        background-color: #2d2d2d;
    }
    h1 {
        color: #ffd700;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        color: #b0b0b0;
        font-style: italic;
    }
    .info-box {
        background-color: rgba(255, 215, 0, 0.1);
        border-left: 4px solid #ffd700;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐱 Random Black Cats 🐱")
st.markdown("<p class='subtitle'>Purr-fectly Charming Felines</p>", unsafe_allow_html=True)

# Initialize session state
if 'cat_counter' not in st.session_state:
    st.session_state.cat_counter = 0
if 'current_cat' not in st.session_state:
    st.session_state.current_cat = None
if 'current_title' not in st.session_state:
    st.session_state.current_title = ''
if 'current_author' not in st.session_state:
    st.session_state.current_author = ''
if 'current_source' not in st.session_state:
    st.session_state.current_source = ''

@st.cache_data(ttl=3600)
def fetch_reddit_cats():
    """Fetch from r/blackcats with proper headers"""
    try:
        url = 'https://www.reddit.com/r/blackcats/.json'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            posts = response.json()['data']['children']
            image_posts = []
            
            for post in posts:
                data = post['data']
                if not data.get('stickied') and not data.get('is_self'):
                    post_url = data.get('url', '')
                    if post_url and ('i.redd.it' in post_url or 'imgur.com' in post_url):
                        image_posts.append({
                            'url': post_url,
                            'title': data.get('title', 'Black Cat'),
                            'author': data.get('author', 'anonymous'),
                            'source': 'r/blackcats'
                        })
            
            return image_posts if image_posts else None
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def fetch_cat_api():
    """Fallback to Cat API"""
    try:
        url = 'https://api.thecatapi.com/v1/images/search?limit=20'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            cats = response.json()
            return [
                {
                    'url': cat['url'],
                    'title': 'Random Cat',
                    'author': 'The Cat API',
                    'source': 'The Cat API'
                }
                for cat in cats
            ]
    except:
        pass
    return None

def get_random_cat():
    """Get cat from Reddit, fallback to Cat API"""
    # Try Reddit first
    reddit_cats = fetch_reddit_cats()
    if reddit_cats:
        return random.choice(reddit_cats)
    
    # Fallback to Cat API
    cat_api_cats = fetch_cat_api()
    if cat_api_cats:
        return random.choice(cat_api_cats)
    
    return None

def display_cat(cat_data):
    """Display cat information"""
    st.session_state.current_cat = cat_data['url']
    st.session_state.current_title = cat_data.get('title', 'Black Cat')
    st.session_state.current_author = cat_data.get('author', 'anonymous')
    st.session_state.current_source = cat_data.get('source', 'Unknown')
    st.session_state.cat_counter += 1

# Main button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🐱 Get New Cat", use_container_width=True):
        with st.spinner('Loading...'):
            cat_data = get_random_cat()
            if cat_data:
                display_cat(cat_data)
                st.success("✅ Got a cat!")
            else:
                st.error("😿 Could not load any cats. Please try again.")

# Display cat
if st.session_state.current_cat:
    st.divider()
    
    try:
        st.image(st.session_state.current_cat, use_column_width=True)
    except:
        st.error("Could not load image")
    
    st.markdown(f"""
    <div class='info-box'>
    <strong>🐱 {st.session_state.current_title}</strong><br>
    Posted by {st.session_state.current_author} • {st.session_state.current_source}
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            img_data = requests.get(st.session_state.current_cat).content
            st.download_button(
                label="⬇️ Download",
                data=img_data,
                file_name=f"cat-{st.session_state.cat_counter}.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
        except:
            st.warning("Could not download image")
else:
    st.info("👋 Click the button above to see a cat!")

# Stats
st.divider()
col1, col2, col3 = st.columns(3)
with col2:
    st.metric("Cats Viewed", st.session_state.cat_counter)

# Footer
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
Made with ❤️ for cat lovers
</div>
""", unsafe_allow_html=True)
