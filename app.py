import streamlit as st
import requests
import random

st.set_page_config(
    page_title="Random Black Cats",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    'cat_counter': 0,
    'current_cat': None,
    'current_title': '',
    'current_author': '',
    'current_source': '',
    'seen_cats': set(),
    'cat_history': [],
    'history_index': -1,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #1a1a1a; color: #f0f0f0; }
.main { background-color: #2d2d2d; }
h1 { color: #ffd700; text-align: center; }
.subtitle { text-align: center; color: #b0b0b0; font-style: italic; }
.info-box {
    background-color: rgba(255,215,0,0.1);
    border-left: 4px solid #ffd700;
    padding: 15px;
    border-radius: 5px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐱 Random Black Cats 🐱")
st.markdown("<p class='subtitle'>Purr-fectly Charming Felines</p>", unsafe_allow_html=True)

# ── Data fetching ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_reddit_cats():
    """
    Fetch image posts from r/blackcats (community-curated — always black cats).
    Pulls two pages (up to 200 posts) for a large pool.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BlackCatApp/2.0)'}
    posts = []

    for url in [
        'https://www.reddit.com/r/blackcats/.json?limit=100',
        'https://www.reddit.com/r/blackcats/top/.json?limit=100&t=month',
    ]:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            for child in r.json()['data']['children']:
                d = child['data']
                if d.get('stickied') or d.get('is_self'):
                    continue
                post_url = d.get('url', '')
                # Only trust Reddit's own image CDN — guarantees it's an actual image
                if 'i.redd.it' in post_url:
                    posts.append({
                        'url': post_url,
                        'title': d.get('title', 'Black Cat'),
                        'author': d.get('author', 'anonymous'),
                        'source': 'r/blackcats',
                    })
        except Exception as e:
            st.warning(f"Reddit fetch error: {e}")

    return posts or None


@st.cache_data(ttl=3600)
def fetch_bombay_cats():
    """
    Fetch Bombay breed images from The Cat API.
    Bombay is a solid-black breed — guaranteed black cats.
    Other breeds (BSH, Devon Rex, etc.) come in many colors and are excluded.
    """
    try:
        r = requests.get(
            'https://api.thecatapi.com/v1/images/search?limit=50&breed_ids=bom',
            timeout=15
        )
        if r.status_code == 200:
            return [
                {
                    'url': cat['url'],
                    'title': 'Bombay',
                    'author': 'The Cat API',
                    'source': 'Cat API — Bombay breed',
                }
                for cat in r.json()
            ] or None
    except Exception as e:
        st.warning(f"Cat API fetch error: {e}")
    return None


def pick_unseen(pool):
    """Return a random cat from pool that hasn't been shown yet."""
    if not pool:
        return None
    unseen = [c for c in pool if c['url'] not in st.session_state.seen_cats]
    # If we've exhausted unseen cats, reset so the app doesn't get stuck
    if not unseen:
        st.session_state.seen_cats.clear()
        unseen = pool
    return random.choice(unseen)


def get_random_cat():
    """
    Return one black cat dict, preferring Reddit (community-curated),
    falling back to Bombay Cat API (breed-guaranteed black).
    No HuggingFace verification — it was unreliable and silently rejecting valid cats.
    """
    reddit = fetch_reddit_cats()
    if reddit:
        cat = pick_unseen(reddit)
        if cat:
            return cat

    bombay = fetch_bombay_cats()
    if bombay:
        cat = pick_unseen(bombay)
        if cat:
            return cat

    return None


def show_cat(cat_data):
    """Record cat as seen, push to history, update session state."""
    url = cat_data['url']
    st.session_state.seen_cats.add(url)
    st.session_state.current_cat = url
    st.session_state.current_title = cat_data.get('title', 'Black Cat')
    st.session_state.current_author = cat_data.get('author', 'anonymous')
    st.session_state.current_source = cat_data.get('source', 'Unknown')
    st.session_state.cat_counter += 1
    st.session_state.cat_history.append(cat_data)
    st.session_state.history_index = len(st.session_state.cat_history) - 1


# ── Load first cat ─────────────────────────────────────────────────────────────
if st.session_state.history_index == -1:
    cat = get_random_cat()
    if cat:
        show_cat(cat)

# ── UI ─────────────────────────────────────────────────────────────────────────
if st.session_state.current_cat:
    st.divider()

    col_back, col_img, col_fwd = st.columns([1, 4, 1])

    with col_back:
        st.write("")  # vertical spacing
        st.write("")
        if st.button("◀️", use_container_width=True,
                     disabled=(st.session_state.history_index <= 0)):
            st.session_state.history_index -= 1
            prev = st.session_state.cat_history[st.session_state.history_index]
            st.session_state.current_cat = prev['url']
            st.session_state.current_title = prev.get('title', 'Black Cat')
            st.session_state.current_author = prev.get('author', 'anonymous')
            st.session_state.current_source = prev.get('source', 'Unknown')
            st.rerun()

    with col_img:
        try:
            st.image(st.session_state.current_cat, use_container_width=True)
        except Exception:
            st.error("Could not load image — try the next one.")

    with col_fwd:
        st.write("")
        st.write("")
        if st.button("▶️", use_container_width=True):
            if st.session_state.history_index < len(st.session_state.cat_history) - 1:
                st.session_state.history_index += 1
                nxt = st.session_state.cat_history[st.session_state.history_index]
                st.session_state.current_cat = nxt['url']
                st.session_state.current_title = nxt.get('title', 'Black Cat')
                st.session_state.current_author = nxt.get('author', 'anonymous')
                st.session_state.current_source = nxt.get('source', 'Unknown')
                st.rerun()
            else:
                cat = get_random_cat()
                if cat:
                    show_cat(cat)
                    st.rerun()
                else:
                    st.warning("No more cats available right now. Try again in a moment.")

    st.markdown(f"""
    <div class='info-box'>
    <strong>🐱 {st.session_state.current_title}</strong><br>
    <small>{st.session_state.current_source}
    {"• u/" + st.session_state.current_author if st.session_state.current_source == "r/blackcats" else ""}
    </small>
    </div>
    """, unsafe_allow_html=True)

    # Download
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            img_bytes = requests.get(st.session_state.current_cat, timeout=10).content
            st.download_button(
                label="⬇️ Download this cat",
                data=img_bytes,
                file_name=f"black-cat-{st.session_state.cat_counter}.jpg",
                mime="image/jpeg",
                use_container_width=True,
            )
        except Exception:
            st.warning("Could not prepare download.")

else:
    st.divider()
    st.info("Click ▶️ to load your first black cat!")

# ── Footer stats ───────────────────────────────────────────────────────────────
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("🐈‍⬛ Cats viewed", st.session_state.cat_counter)
with col2:
    st.metric("📚 In history", len(st.session_state.cat_history))

st.markdown("""
<div style='text-align:center; color:#888; font-size:0.85rem; margin-top:1rem;'>
Made with ❤️ for cat lovers
</div>
""", unsafe_allow_html=True)
