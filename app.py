import streamlit as st
import requests
import random

st.set_page_config(
    page_title="Random Black Cats",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed",
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
    'pool': [],
    'fetch_log': [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
h1 { color: #ffd700; text-align: center; }
.subtitle { text-align: center; color: #b0b0b0; font-style: italic; }
.info-box {
    background: rgba(255,215,0,0.08);
    border-left: 4px solid #ffd700;
    padding: 12px 16px;
    border-radius: 5px;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐱 Random Black Cats 🐱")
st.markdown("<p class='subtitle'>Purr-fectly Charming Felines</p>", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# Subreddits that are 100% curated black cats
SUBREDDITS = ['blackcats', 'SuperBlackCats', 'voidcats']
SORTS = {
    'hot':  '?limit=100',
    'new':  '?limit=100',
    'top':  '?t=month&limit=100',
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def log(msg: str):
    st.session_state.fetch_log.append(msg)


def reddit_image_posts(sub: str, sort: str, qs: str) -> list:
    url = f"https://www.reddit.com/r/{sub}/{sort}.json{qs}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            log(f"  ✗ r/{sub}/{sort} → HTTP {r.status_code}")
            return []
        posts = []
        for child in r.json()['data']['children']:
            d = child['data']
            if d.get('stickied') or d.get('is_self'):
                continue
            post_url = d.get('url', '')
            if 'i.redd.it' in post_url:
                posts.append({
                    'url': post_url,
                    'title': d.get('title', 'Black Cat'),
                    'author': d.get('author', 'anonymous'),
                    'source': f"r/{sub}",
                })
        log(f"  ✓ r/{sub}/{sort} → {len(posts)} images")
        return posts
    except Exception as e:
        log(f"  ✗ r/{sub}/{sort} → {e}")
        return []


def build_pool() -> list:
    st.session_state.fetch_log = []
    pool = []

    log("📡 Fetching from Reddit…")
    for sub in SUBREDDITS:
        for sort, qs in SORTS.items():
            pool.extend(reddit_image_posts(sub, sort, qs))

    # Deduplicate by URL
    seen_urls: set = set()
    unique = []
    for cat in pool:
        if cat['url'] not in seen_urls:
            seen_urls.add(cat['url'])
            unique.append(cat)
    pool = unique
    log(f"\n🐱 Reddit pool (deduped): {len(pool)} images")

    # Bombay fallback only when Reddit yields nothing
    if not pool:
        log("\n⚠️  Reddit returned 0 images — trying Bombay Cat API…")
        try:
            r = requests.get(
                'https://api.thecatapi.com/v1/images/search?limit=50&breed_ids=bom',
                timeout=12,
            )
            if r.status_code == 200:
                bombay = [
                    {'url': c['url'], 'title': 'Bombay',
                     'author': 'The Cat API', 'source': 'Cat API — Bombay'}
                    for c in r.json()
                ]
                pool.extend(bombay)
                log(f"  ✓ Bombay Cat API → {len(bombay)} images")
            else:
                log(f"  ✗ Bombay Cat API → HTTP {r.status_code}")
        except Exception as e:
            log(f"  ✗ Bombay Cat API → {e}")

    random.shuffle(pool)
    return pool


def pick_cat():
    unseen = [c for c in st.session_state.pool
              if c['url'] not in st.session_state.seen_cats]
    if not unseen:
        # Pool exhausted — rebuild silently
        st.session_state.pool = build_pool()
        st.session_state.seen_cats.clear()
        unseen = st.session_state.pool[:]
    return random.choice(unseen) if unseen else None


def show_cat(cat: dict):
    st.session_state.seen_cats.add(cat['url'])
    st.session_state.current_cat    = cat['url']
    st.session_state.current_title  = cat.get('title', 'Black Cat')
    st.session_state.current_author = cat.get('author', '')
    st.session_state.current_source = cat.get('source', '')
    st.session_state.cat_counter   += 1
    st.session_state.cat_history.append(cat)
    st.session_state.history_index = len(st.session_state.cat_history) - 1


# ── Bootstrap ──────────────────────────────────────────────────────────────────
if not st.session_state.pool:
    with st.spinner("Fetching black cats from Reddit…"):
        st.session_state.pool = build_pool()

if st.session_state.history_index == -1:
    cat = pick_cat()
    if cat:
        show_cat(cat)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Stats")
    st.metric("🐈‍⬛ Cats viewed", st.session_state.cat_counter)
    st.metric("📚 Pool size", len(st.session_state.pool))
    st.metric("👁️ Already seen", len(st.session_state.seen_cats))

    if st.button("🔄 Refresh pool"):
        st.session_state.pool = build_pool()
        st.session_state.seen_cats.clear()
        st.rerun()

    if st.session_state.fetch_log:
        st.markdown("### 🔍 Fetch log")
        st.code("\n".join(st.session_state.fetch_log), language=None)

# ── Main UI ────────────────────────────────────────────────────────────────────
if st.session_state.current_cat:
    st.divider()

    col_back, col_img, col_fwd = st.columns([1, 6, 1])

    with col_back:
        st.write("")
        st.write("")
        if st.button("◀️", use_container_width=True,
                     disabled=(st.session_state.history_index <= 0)):
            st.session_state.history_index -= 1
            prev = st.session_state.cat_history[st.session_state.history_index]
            st.session_state.current_cat    = prev['url']
            st.session_state.current_title  = prev.get('title', 'Black Cat')
            st.session_state.current_author = prev.get('author', '')
            st.session_state.current_source = prev.get('source', '')
            st.rerun()

    with col_img:
        try:
            st.image(st.session_state.current_cat, use_container_width=True)
        except Exception:
            st.error("Could not render image — click ▶️ for the next one.")

    with col_fwd:
        st.write("")
        st.write("")
        if st.button("▶️", use_container_width=True):
            if st.session_state.history_index < len(st.session_state.cat_history) - 1:
                st.session_state.history_index += 1
                nxt = st.session_state.cat_history[st.session_state.history_index]
                st.session_state.current_cat    = nxt['url']
                st.session_state.current_title  = nxt.get('title', 'Black Cat')
                st.session_state.current_author = nxt.get('author', '')
                st.session_state.current_source = nxt.get('source', '')
                st.rerun()
            else:
                cat = pick_cat()
                if cat:
                    show_cat(cat)
                    st.rerun()
                else:
                    st.warning("No cats available — click 'Refresh pool' in the sidebar.")

    author_suffix = (
        f"&nbsp;• u/{st.session_state.current_author}"
        if st.session_state.current_source.startswith("r/") and st.session_state.current_author
        else ""
    )
    st.markdown(f"""
    <div class='info-box'>
    <strong>🐱 {st.session_state.current_title}</strong><br>
    <small>Source: {st.session_state.current_source}{author_suffix}</small>
    </div>
    """, unsafe_allow_html=True)

    _, col_dl, _ = st.columns([1, 2, 1])
    with col_dl:
        try:
            img_bytes = requests.get(
                st.session_state.current_cat, headers=HEADERS, timeout=10
            ).content
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
    if st.session_state.fetch_log:
        with st.expander("Fetch log (debug)"):
            st.code("\n".join(st.session_state.fetch_log))

st.markdown("""
<div style='text-align:center;color:#888;font-size:0.85rem;margin-top:1rem;'>
Made with ❤️ for cat lovers
</div>
""", unsafe_allow_html=True)
