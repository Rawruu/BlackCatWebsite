import streamlit as st
import requests
import random
import time
import json

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

# Sidebar metrics
with st.sidebar:
    st.markdown("### 📊 Metrics")
    st.metric("✅ Accepted Cats", st.session_state.accepted_cats)
    st.metric("❌ Rejected Cats", st.session_state.rejected_cats)
    st.metric("📈 Total Fetched", st.session_state.total_fetched)

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
if 'cat_history' not in st.session_state:
    st.session_state.cat_history = []
if 'history_index' not in st.session_state:
    st.session_state.history_index = -1
if 'accepted_cats' not in st.session_state:
    st.session_state.accepted_cats = 0
if 'rejected_cats' not in st.session_state:
    st.session_state.rejected_cats = 0
if 'total_fetched' not in st.session_state:
    st.session_state.total_fetched = 0

@st.cache_data(ttl=3600)
def fetch_reddit_cats():
    """Fetch from r/blackcats with proper headers - multiple pages for more cats"""
    try:
        all_posts = []
        url = 'https://www.reddit.com/r/blackcats/.json?limit=100'  # Increased from default 25 to 100
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Fetch first page
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()['data']
            posts = data['children']
            
            image_posts = []
            for post in posts:
                post_data = post['data']
                if not post_data.get('stickied') and not post_data.get('is_self'):
                    post_url = post_data.get('url', '')
                    if post_url and ('i.redd.it' in post_url or 'imgur.com' in post_url):
                        image_posts.append({
                            'url': post_url,
                            'title': post_data.get('title', 'Black Cat'),
                            'author': post_data.get('author', 'anonymous'),
                            'source': 'r/blackcats'
                        })
            
            # Try to fetch next page for even more images
            after = data.get('after')
            if after and len(image_posts) < 150:
                url_page2 = f'https://www.reddit.com/r/blackcats/.json?limit=100&after={after}'
                try:
                    response2 = requests.get(url_page2, headers=headers, timeout=15)
                    if response2.status_code == 200:
                        data2 = response2.json()['data']['children']
                        for post in data2:
                            post_data = post['data']
                            if not post_data.get('stickied') and not post_data.get('is_self'):
                                post_url = post_data.get('url', '')
                                if post_url and ('i.redd.it' in post_url or 'imgur.com' in post_url):
                                    image_posts.append({
                                        'url': post_url,
                                        'title': post_data.get('title', 'Black Cat'),
                                        'author': post_data.get('author', 'anonymous'),
                                        'source': 'r/blackcats'
                                    })
                except:
                    pass  # If second page fails, just use first page
            
            return image_posts if image_posts else None
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def fetch_cat_api():
    """Fetch from Cat API with black cat breeds - get from ALL breeds"""
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
        
        all_cats = []
        
        # Fetch from ALL breeds and accumulate (increased from 10 to 50 per breed)
        for breed in black_breeds:
            try:
                url = f'https://api.thecatapi.com/v1/images/search?limit=50&breed_ids={breed}'
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    cats = response.json()
                    for cat in cats:
                        all_cats.append({
                            'url': cat['url'],
                            'title': f'{cat.get("breeds", [{}])[0].get("name", "Black Cat")}' if cat.get('breeds') else 'Black Cat',
                            'author': 'The Cat API',
                            'source': 'Cat API',
                            'breed': cat.get('breeds', [{}])[0].get('name', 'Unknown') if cat.get('breeds') else 'Unknown'
                        })
            except:
                continue  # Continue to next breed if one fails
        
        if all_cats:
            return all_cats
        
        # If specific breeds fail, get any random cats as fallback
        url = 'https://api.thecatapi.com/v1/images/search?limit=50'
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
    """Fallback to CATAAS (Cat As A Service) - no auth required, fetch in bulk"""
    try:
        # CATAAS API returns cat list - fetch larger batch (increased from 20 to 100)
        url = 'https://cataas.com/api/cats?limit=100&skip=0'
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
                
                # Try to fetch another batch as well
                if len(urls) < 100:
                    try:
                        url2 = 'https://cataas.com/api/cats?limit=100&skip=100'
                        response2 = requests.get(url2, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                        if response2.status_code == 200:
                            data2 = response2.json()
                            cats2 = data2 if isinstance(data2, list) else data2.get('data', [])
                            for cat in cats2:
                                cat_id = cat.get('_id') or cat.get('id')
                                if cat_id:
                                    urls.append({
                                        'url': f'https://cataas.com/cat/{cat_id}',
                                        'title': 'Random Cat',
                                        'author': 'CATAAS',
                                        'source': 'CATAAS',
                                        'breed': 'Unknown'
                                    })
                    except:
                        pass
                
                return urls if urls else None
    except Exception as e:
        print(f"CATAAS error: {e}")
    return None

@st.cache_data(ttl=3600)
def fetch_random_cat_batch():
    """Fetch multiple cats from Random.cat API - batch fetch instead of 1 at a time"""
    try:
        # Random.cat doesn't support batch, so we'll fetch multiple times and cache
        batch = []
        for _ in range(50):  # Fetch 50 cats in this batch
            try:
                url = 'https://api.random.cat/meow'
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    cat_url = data.get('file')
                    if cat_url and cat_url not in [c['url'] for c in batch]:  # Avoid duplicates
                        batch.append({
                            'url': cat_url,
                            'title': 'Random Cat',
                            'author': 'Random.cat',
                            'source': 'Random.cat',
                            'breed': 'Unknown'
                        })
                    if len(batch) >= 50:
                        break
            except:
                continue
        
        return batch if batch else None
    except Exception as e:
        print(f"Random.cat batch error: {e}")
    return None

@st.cache_data(ttl=3600)
def is_black_cat_with_huggingface(image_url):
    """Use HuggingFace to verify if the cat image is primarily black"""
    try:
        # Using image-to-text model to describe the cat
        hf_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
        
        headers = {
            "User-Agent": "BlackCatApp/1.0"
        }
        
        payload = {"inputs": image_url}
        response = requests.post(hf_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                caption = result[0].get('generated_text', '').lower()
                
                # Check for black/dark indicators
                black_indicators = ['black', 'dark', 'ebony', 'raven', 'midnight', 'shadow', 'coal']
                non_black_indicators = ['white', 'orange', 'ginger', 'red', 'tabby', 'calico', 'gray', 'grey', 'brown', 'tan', 'cream', 'yellow', 'siamese']
                
                has_black = any(indicator in caption for indicator in black_indicators)
                has_non_black = any(indicator in caption for indicator in non_black_indicators)
                
                # If it explicitly mentions black-related terms and doesn't mention color contradictions, accept it
                if has_black and not has_non_black:
                    return True
                
                # If it mentions non-black colors, reject it
                if has_non_black:
                    return False
                
                # Reject if no color info found (just says "cat" with no details)
                if 'cat' in caption and not has_black and not has_non_black:
                    return False
                
                # Default reject for safety
                return False
        
    except Exception as e:
        print(f"Color verification error: {e}")
    
    # If API fails, reject the cat (safer to filter too much than too little)
    return False

@st.cache_data(ttl=3600)
def identify_breed_with_huggingface(image_url):
    """Use HuggingFace free inference to identify cat breed from image URL"""
    try:
        # Using HuggingFace's free inference API with image-to-text model
        # This model can describe images including identifying cats and their characteristics
        hf_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
        
        headers = {
            "User-Agent": "BlackCatApp/1.0"
        }
        
        payload = {"inputs": image_url}
        
        # Make request with timeout
        response = requests.post(hf_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                caption = result[0].get('generated_text', '')
                
                # Parse caption for breed info
                if 'cat' in caption.lower():
                    # Try to extract breed names from common breeds
                    breeds = [
                        'bombay', 'british', 'cornish', 'devon', 'egyptian', 'korat', 
                        'manx', 'ocicat', 'oriental', 'russian', 'scottish', 'sphynx', 
                        'thai', 'tonkinese', 'turkish', 'siamese', 'bengal', 'maine', 
                        'ragdoll', 'persian', 'poodle', 'calico', 'tabby', 'tuxedo'
                    ]
                    
                    caption_lower = caption.lower()
                    for breed in breeds:
                        if breed in caption_lower:
                            return breed.title()
                    
                    # If no specific breed found but has 'cat', return generic with description
                    if len(caption) > 20:
                        return caption.title()[:50]
                    
                return "Black Cat"
        
        # Fallback: try alternate endpoint if first fails
        alt_url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
        response = requests.post(alt_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            return "Identified Cat"
            
    except Exception as e:
        print(f"Breed identification error: {e}")
        # Silently fail - breed will remain as 'Unknown'
    
    return "Unknown"


def get_random_cat():
    """Get cat from Reddit → Cat API → CATAAS, avoiding repeats and non-black cats"""
    def get_unseen_cat(cats_list):
        """Filter out previously seen cat URLs"""
        if not cats_list:
            return None
        unseen = [cat for cat in cats_list if cat['url'] not in st.session_state.seen_cats]
        return random.choice(unseen) if unseen else None
    
    # Try Reddit first (most reliable for black cats)
    reddit_cats = fetch_reddit_cats()
    if reddit_cats:
        cat = get_unseen_cat(reddit_cats)
        if cat:
            st.session_state.total_fetched += 1
            return cat
    
    # Fallback to Cat API (has guaranteed black breed filtering)
    cat_api_cats = fetch_cat_api()
    if cat_api_cats:
        cat = get_unseen_cat(cat_api_cats)
        if cat:
            st.session_state.total_fetched += 1
            return cat
    
    # Try CATAAS with validation (verify it's a black cat)
    cataas_cats = fetch_cataas()
    if cataas_cats:
        # Keep trying until we find a black cat or run out
        for _ in range(5):
            cat = get_unseen_cat(cataas_cats)
            if cat:
                st.session_state.total_fetched += 1
                if is_black_cat_with_huggingface(cat['url']):
                    return cat
                else:
                    st.session_state.rejected_cats += 1
    
    # Final fallback: try Random.cat batch with validation
    random_cats = fetch_random_cat_batch()
    if random_cats:
        for _ in range(10):
            cat = get_unseen_cat(random_cats)
            if cat:
                st.session_state.total_fetched += 1
                if is_black_cat_with_huggingface(cat['url']):
                    return cat
                else:
                    st.session_state.rejected_cats += 1
    
    return None

def display_cat(cat_data):
    """Display cat information, track it as seen, validate it's black, and identify breed"""
    st.session_state.current_cat = cat_data['url']
    st.session_state.current_title = cat_data.get('title', 'Black Cat')
    st.session_state.current_author = cat_data.get('author', 'anonymous')
    st.session_state.current_source = cat_data.get('source', 'Unknown')
    st.session_state.current_breed = cat_data.get('breed', 'Unknown')
    st.session_state.cat_counter += 1
    st.session_state.accepted_cats += 1  # Track accepted cats
    # Track this cat URL to avoid repeats
    st.session_state.seen_cats.add(cat_data['url'])
    
    # Add to history and update index
    st.session_state.cat_history.append(cat_data)
    st.session_state.history_index = len(st.session_state.cat_history) - 1
    
    # Verify it's actually a black cat and identify breed using HuggingFace
    if st.session_state.current_cat:
        try:
            # First verify it's black
            is_black = is_black_cat_with_huggingface(st.session_state.current_cat)
            
            # Then identify breed
            identified_breed = identify_breed_with_huggingface(st.session_state.current_cat)
            
            if identified_breed and identified_breed != 'Unknown':
                st.session_state.current_breed = identified_breed
            
            # If we detected it's not black, we can mark it for later retry logic
            if not is_black:
                st.session_state.current_breed = f"{st.session_state.current_breed} (❌ Not black)"
                
        except:
            pass  # Continue with breed identification failure

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
    
    # Navigation buttons with image
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀️ Back", use_container_width=True, disabled=(st.session_state.history_index <= 0)):
            if st.session_state.history_index > 0:
                st.session_state.history_index -= 1
                prev_cat = st.session_state.cat_history[st.session_state.history_index]
                st.session_state.current_cat = prev_cat['url']
                st.session_state.current_title = prev_cat.get('title', 'Black Cat')
                st.session_state.current_author = prev_cat.get('author', 'anonymous')
                st.session_state.current_source = prev_cat.get('source', 'Unknown')
                st.session_state.current_breed = prev_cat.get('breed', 'Unknown')
                st.rerun()
    
    with col2:
        try:
            st.image(st.session_state.current_cat, width=760)
        except:
            st.error("Could not load image")
    
    with col3:
        if st.button("Forward ▶️", use_container_width=True):
            if st.session_state.history_index < len(st.session_state.cat_history) - 1:
                st.session_state.history_index += 1
                next_cat = st.session_state.cat_history[st.session_state.history_index]
                st.session_state.current_cat = next_cat['url']
                st.session_state.current_title = next_cat.get('title', 'Black Cat')
                st.session_state.current_author = next_cat.get('author', 'anonymous')
                st.session_state.current_source = next_cat.get('source', 'Unknown')
                st.session_state.current_breed = next_cat.get('breed', 'Unknown')
                st.rerun()
            else:
                # If at end of history, get new cat
                cat_data = get_random_cat()
                if cat_data:
                    display_cat(cat_data)
                    st.rerun()
    
    st.markdown(f"""
    <div class='info-box'>
    <strong>🐱 {st.session_state.current_title}</strong><br>
    {st.session_state.current_source}
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
with col1:
    st.metric("✅ Accepted", st.session_state.accepted_cats)
with col2:
    st.metric("❌ Rejected", st.session_state.rejected_cats)
with col3:
    st.metric("📈 Total Fetched", st.session_state.total_fetched)

# Footer
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
Made with ❤️ for cat lovers
</div>
""", unsafe_allow_html=True)
