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
if 'current_breed' not in st.session_state:
    st.session_state.current_breed = ''
if 'seen_cats' not in st.session_state:
    st.session_state.seen_cats = set()

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
    """Fallback to Cat API with black cat breeds"""
    try:
        # Black cat breeds from The Cat API
        black_breeds = [
            'bom',   # Bombay - solid black
            'bsh',   # British Shorthair - can be black
            'crx',   # Cornish Rex - can be black
            'drx',   # Devon Rex - can be black
            'egy',   # Egyptian Mau - spotted, can be black
            'kor',   # Korat - blue/gray, sometimes black
            'man',   # Manx - can be black
            'oak',   # Ocicat - can be black
            'ori',   # Oriental - can be black
            'rux',   # Russian Blue - some are very dark
            'sfx',   # Scottish Fold - can be black
            'sph',   # Sphynx - can be black
            'tha',   # Thai - can be black
            'ton',   # Tonkinese - can be black
            'van',   # Turkish Van - can be black
        ]
        
        # Try to get images with breed filtering
        for breed in black_breeds:
            try:
                url = f'https://api.thecatapi.com/v1/images/search?limit=10&breed_ids={breed}'
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    cats = response.json()
                    if cats:
                        return [
                            {
                                'url': cat['url'],
                                'title': f'{cat.get("breeds", [{}])[0].get("name", "Black Cat")}' if cat.get('breeds') else 'Black Cat',
                                'author': 'The Cat API',
                                'source': 'Cat API',
                                'breed': cat.get('breeds', [{}])[0].get('name', 'Unknown')
                            }
                            for cat in cats
                        ]
            except:
                continue
        
        # If specific breeds fail, get any random cats
        url = 'https://api.thecatapi.com/v1/images/search?limit=20'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            cats = response.json()
            return [
                {
                    'url': cat['url'],
                    'title': 'Random Cat',
                    'author': 'The Cat API',
                    'source': 'Cat API',
                    'breed': cat.get('breeds', [{}])[0].get('name', 'Unknown') if cat.get('breeds') else 'Unknown'
                }
                for cat in cats
            ]
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def fetch_cataas():
    """Fallback to CATAAS (Cat As A Service) - no auth required"""
    try:
        # CATAAS API returns cat list
        url = 'https://cataas.com/api/cats?limit=20'
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            # Handle both direct list and wrapped response
            cats = data if isinstance(data, list) else data.get('data', [])
            
            if cats:
                urls = []
                for cat in cats:
                    cat_id = cat.get('_id') or cat.get('id')
                    if cat_id:
                        urls.append({
                            'url': f'https://cataas.com/cat/{cat_id}',
                            'title': 'Random Cat',
                            'author': 'CATAAS',
                            'source': 'CATAAS',
                            'breed': 'Unknown'
                        })
                return urls if urls else None
    except Exception as e:
        print(f"CATAAS error: {e}")
    return None

def get_random_cat():
    """Get cat from Reddit → CATAAS → Cat API, avoiding repeats"""
    def get_unseen_cat(cats_list):
        """Filter out previously seen cat URLs"""
        if not cats_list:
            return None
        unseen = [cat for cat in cats_list if cat['url'] not in st.session_state.seen_cats]
        return random.choice(unseen) if unseen else None
    
    # Try Reddit first
    reddit_cats = fetch_reddit_cats()
    if reddit_cats:
        cat = get_unseen_cat(reddit_cats)
        if cat:
            return cat
    
    # Fallback to CATAAS (second choice)
    cataas_cats = fetch_cataas()
    if cataas_cats:
        cat = get_unseen_cat(cataas_cats)
        if cat:
            return cat
    
    # Final fallback to Cat API
    cat_api_cats = fetch_cat_api()
    if cat_api_cats:
        cat = get_unseen_cat(cat_api_cats)
        if cat:
            return cat
    
    return None

def display_cat(cat_data):
    """Display cat information and track it as seen"""
    st.session_state.current_cat = cat_data['url']
    st.session_state.current_title = cat_data.get('title', 'Black Cat')
    st.session_state.current_author = cat_data.get('author', 'anonymous')
    st.session_state.current_source = cat_data.get('source', 'Unknown')
    st.session_state.current_breed = cat_data.get('breed', 'Unknown')
    st.session_state.cat_counter += 1
    # Track this cat URL to avoid repeats
    st.session_state.seen_cats.add(cat_data['url'])

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
    Breed: {st.session_state.current_breed} • {st.session_state.current_source}
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
