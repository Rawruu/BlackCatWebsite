import streamlit as st
import requests
import random
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

def fetch_black_cats():
    """Fetch posts from r/blackcats subreddit"""
    try:
        url = 'https://www.reddit.com/r/blackcats/.json'
        response = requests.get(url, headers={'User-Agent': 'BlackCatStreamlitApp/1.0'}, timeout=10)
        
        if response.status_code != 200:
            st.error(f"Reddit API Error: {response.status_code}")
            return None
        
        data = response.json()
        posts = data['data']['children']
        
        # Filter for image posts
        image_posts = []
        for post in posts:
            post_data = post['data']
            url = post_data.get('url', '')
            
            if url and (
                'i.redd.it' in url or 
                'imgur.com' in url or
                url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
            ):
                image_posts.append(post_data)
        
        if not image_posts:
            st.error("No image posts found in r/blackcats")
            return None
        
        return image_posts
    
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error fetching cats: {str(e)}")
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
