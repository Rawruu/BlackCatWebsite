import streamlit as st
import requests
import random
import time
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

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
st.markdown("<p class='subtitle'>Purr-fectly Charming Felines from r/blackcats</p>", unsafe_allow_html=True)

# Initialize session state
if 'cat_counter' not in st.session_state:
    st.session_state.cat_counter = 0
if 'current_cat' not in st.session_state:
    st.session_state.current_cat = None
if 'current_title' not in st.session_state:
    st.session_state.current_title = ''
if 'current_author' not in st.session_state:
    st.session_state.current_author = ''

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_black_cats():
    """Fetch posts from r/blackcats subreddit with caching"""
    """Fetch posts from r/blackcats subreddit with caching"""
    try:
        url = 'https://www.reddit.com/r/blackcats/.json'
        
        # Use a realistic browser User-Agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache'
        }
        
        # Add small delay to be respectful
        time.sleep(1)
        
        # Try with retries in case of temporary failures
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data['data']['children']
                    
                    # Filter for image posts
                    image_posts = []
                    for post in posts:
                        post_data = post['data']
                        post_url = post_data.get('url', '')
                        
                        # Skip stickied posts and ads
                        if post_data.get('stickied') or post_data.get('is_self'):
                            continue
                        
                        if post_url and not post_url.startswith('https://www.reddit.com') and (
                            'i.redd.it' in post_url or 
                            'imgur.com' in post_url or
                            'gfycat' in post_url or
                            'redgifs' in post_url or
                            post_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                        ):
                            image_posts.append(post_data)
                    
                    if not image_posts:
                        return None
                    
                    return image_posts
                
                elif response.status_code == 429:
                    # Rate limited
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return None
                
                elif response.status_code == 403:
                    return None
                
                else:
                    return None
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return None
        
        return None
        
    except Exception:
        return None

def display_cat(post_data):
    """Display a cat image and information"""
    st.session_state.current_cat = post_data['url']
    st.session_state.current_title = post_data.get('title', 'Black Cat')
    st.session_state.current_author = post_data.get('author', 'anonymous')
    st.session_state.cat_counter += 1

# Button to fetch new cat
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🐱 Get New Black Cat", use_container_width=True, key="get_cat_btn"):
        with st.spinner('Loading a precious void from r/blackcats...'):
            image_posts = fetch_black_cats()
            if image_posts:
                random_post = random.choice(image_posts)
                display_cat(random_post)
                st.success("✅ Got your black cat!")
            else:
                st.error("😿 I'm having trouble connecting to r/blackcats. Reddit might be temporarily unavailable or blocking us. Please try again in a moment!")

# Display current cat
if st.session_state.current_cat:
    st.divider()
    
    try:
        # Try to display the image
        st.image(st.session_state.current_cat, use_column_width=True, caption="Black Cat from r/blackcats")
    except Exception as e:
        st.warning(f"Could not load image: {str(e)}")
        st.info(f"Image URL: {st.session_state.current_cat}")
    
    # Display info
    st.markdown(f"""
    <div class='info-box'>
    <strong>🐱 {st.session_state.current_title}</strong><br>
    Posted by u/{st.session_state.current_author}
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="⬇️ Download Image",
            data=requests.get(st.session_state.current_cat).content,
            file_name=f"black-cat-{st.session_state.cat_counter}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
else:
    st.info("👋 Click the button above to see a random black cat!")

# Display stats
st.divider()
col1, col2, col3 = st.columns(3)
with col2:
    st.metric("Cats Viewed", st.session_state.cat_counter, delta=None)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
Made with ❤️ for cat lovers | Images from r/blackcats
</div>
""", unsafe_allow_html=True)
