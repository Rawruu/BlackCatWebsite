import streamlit as st
import requests
import random

st.set_page_config(
    page_title="Black Cat Sanctuary",
    page_icon="🌿",
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
/* ── Background ── */
.stApp {
    background: linear-gradient(160deg, #1a2e1e 0%, #1e2d28 45%, #1c2a22 100%);
    min-height: 100vh;
}

/* ── Typography ── */
h1 {
    font-family: Georgia, 'Times New Roman', serif !important;
    color: #c8ddb8 !important;
    text-align: center;
    font-weight: normal !important;
    letter-spacing: 2px;
    text-shadow: 0 2px 14px rgba(0,0,0,0.45);
}
h2, h3 {
    font-family: Georgia, serif !important;
    color: #b8cca8 !important;
    font-weight: normal !important;
}

/* ── Header decoration ── */
.sanctuary-header {
    text-align: center;
    margin-bottom: 0.25rem;
}
.leaf-divider {
    text-align: center;
    color: #6a8c6a;
    font-size: 1.1rem;
    letter-spacing: 6px;
    margin: 0.1rem 0 0.6rem 0;
}
.subtitle {
    text-align: center;
    color: #8aad82;
    font-style: italic;
    font-family: Georgia, serif;
    font-size: 1rem;
    letter-spacing: 0.4px;
    margin-bottom: 0.25rem;
}

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(168, 197, 160, 0.18) !important;
    margin: 1rem 0 !important;
}

/* ── Image ── */
[data-testid="stImage"] img {
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

/* ── Info card ── */
.info-box {
    background: rgba(168, 197, 160, 0.07);
    border-left: 3px solid #8ab87e;
    padding: 13px 18px;
    border-radius: 0 12px 12px 0;
    margin-top: 14px;
    color: #d0e8c8;
    font-family: Georgia, serif;
}
.info-box small {
    color: #8aad82;
}

/* ── Buttons ── */
.stButton > button {
    background: rgba(168, 197, 160, 0.12) !important;
    border: 1px solid rgba(168, 197, 160, 0.32) !important;
    color: #c4dbb4 !important;
    border-radius: 28px !important;
    font-family: Georgia, serif !important;
    letter-spacing: 0.3px;
    transition: all 0.22s ease !important;
}
.stButton > button:hover {
    background: rgba(168, 197, 160, 0.26) !important;
    border-color: rgba(168, 197, 160, 0.58) !important;
    color: #dff0d0 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.22);
}
.stButton > button:disabled {
    background: rgba(168, 197, 160, 0.04) !important;
    border-color: rgba(168, 197, 160, 0.1) !important;
    color: rgba(168, 197, 160, 0.28) !important;
    transform: none !important;
}

/* ── Download button (dusty rose) ── */
[data-testid="stDownloadButton"] > button {
    background: rgba(196, 168, 168, 0.12) !important;
    border: 1px solid rgba(196, 168, 168, 0.32) !important;
    color: #ddc4c4 !important;
    border-radius: 28px !important;
    font-family: Georgia, serif !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(196, 168, 168, 0.26) !important;
    border-color: rgba(196, 168, 168, 0.58) !important;
    color: #f0d8d8 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.22);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(18, 32, 22, 0.97) !important;
    border-right: 1px solid rgba(168, 197, 160, 0.12) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(168, 197, 160, 0.07) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    border: 1px solid rgba(168, 197, 160, 0.13) !important;
}
[data-testid="stMetricLabel"] p { color: #8aad82 !important; }
[data-testid="stMetricValue"]   { color: #c4dbb4 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    background: rgba(168, 197, 160, 0.07) !important;
    border: 1px solid rgba(168, 197, 160, 0.22) !important;
    color: #c4dbb4 !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid rgba(168, 197, 160, 0.18) !important;
    border-radius: 12px !important;
    background: rgba(168, 197, 160, 0.03) !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #5a7a5a;
    font-size: 0.82rem;
    margin-top: 2rem;
    font-style: italic;
    font-family: Georgia, serif;
    letter-spacing: 0.3px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='sanctuary-header'><h1>🌿 Black Cat Sanctuary 🌿</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='leaf-divider'>· · ·</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A peaceful haven for the most mysterious of creatures</p>", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def log(msg: str):
    st.session_state.fetch_log.append(msg)


def fetch_cataas() -> list:
    """CATAAS — filter by 'black' tag. No auth, cloud-friendly."""
    pool = []
    try:
        r = requests.get(
            'https://cataas.com/api/cats?tags=black&limit=50',
            headers=HEADERS, timeout=12,
        )
        if r.status_code == 200:
            data = r.json()
            cats = data if isinstance(data, list) else data.get('cats', [])
            for c in cats:
                cat_id = c.get('_id') or c.get('id')
                if cat_id:
                    pool.append({
                        'url': f'https://cataas.com/cat/{cat_id}',
                        'title': 'Black Cat',
                        'author': 'CATAAS',
                        'source': 'cataas.com',
                    })
            log(f"  ✓ CATAAS (black tag) → {len(pool)} images")
        else:
            log(f"  ✗ CATAAS → HTTP {r.status_code}")
    except Exception as e:
        log(f"  ✗ CATAAS → {e}")
    return pool


def fetch_wikimedia() -> list:
    """Wikimedia Commons — Category:Black_cats. No auth, cloud-friendly."""
    pool = []
    try:
        r = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params={
                'action': 'query',
                'generator': 'categorymembers',
                'gcmtitle': 'Category:Black_cats',
                'gcmtype': 'file',
                'gcmlimit': '50',
                'prop': 'imageinfo',
                'iiprop': 'url',
                'format': 'json',
                'origin': '*',
            },
            headers=HEADERS, timeout=12,
        )
        if r.status_code == 200:
            pages = r.json().get('query', {}).get('pages', {})
            for page in pages.values():
                imageinfo = page.get('imageinfo') or []
                url = imageinfo[0].get('url', '') if imageinfo else ''
                if url and url.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png')):
                    title = page.get('title', 'Black Cat').replace('File:', '').rsplit('.', 1)[0]
                    pool.append({
                        'url': url,
                        'title': title,
                        'author': 'Wikimedia Commons',
                        'source': 'Wikimedia Commons',
                    })
            log(f"  ✓ Wikimedia Commons → {len(pool)} images")
        else:
            log(f"  ✗ Wikimedia → HTTP {r.status_code}")
    except Exception as e:
        log(f"  ✗ Wikimedia → {e}")
    return pool


def build_pool() -> list:
    st.session_state.fetch_log = []
    pool = []

    log("📡 Fetching from CATAAS (black tag)…")
    pool.extend(fetch_cataas())

    log("\n📡 Fetching from Wikimedia Commons…")
    pool.extend(fetch_wikimedia())

    # Deduplicate by URL
    seen_urls: set = set()
    unique = []
    for cat in pool:
        if cat['url'] not in seen_urls:
            seen_urls.add(cat['url'])
            unique.append(cat)
    pool = unique
    log(f"\n🐱 Total pool (deduped): {len(pool)} images")

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
    with st.spinner("Gathering cats from the garden…"):
        st.session_state.pool = build_pool()

if st.session_state.history_index == -1:
    cat = pick_cat()
    if cat:
        show_cat(cat)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 Your Garden")
    st.metric("🐈‍⬛ Cats visited", st.session_state.cat_counter)
    st.metric("🌱 Available", len(st.session_state.pool))
    st.metric("👁️ Already seen", len(st.session_state.seen_cats))

    st.markdown("")
    if st.button("🔄 Find more cats", use_container_width=True):
        st.session_state.pool = build_pool()
        st.session_state.seen_cats.clear()
        st.rerun()

    if st.session_state.fetch_log:
        st.markdown("---")
        with st.expander("🔍 Fetch log"):
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

    st.markdown(f"""
    <div class='info-box'>
    <strong>🐈‍⬛ {st.session_state.current_title}</strong><br>
    <small>🌿 {st.session_state.current_source}</small>
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
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🌿 Meet a black cat", use_container_width=True):
            cat = pick_cat()
            if cat:
                show_cat(cat)
                st.rerun()
            else:
                st.error("No cats found — try 'Find more cats' in the sidebar.")
    if st.session_state.fetch_log:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Fetch log"):
            st.code("\n".join(st.session_state.fetch_log))

st.markdown("""
<div class='footer'>
🌿 &nbsp; made with love, for cat lovers everywhere &nbsp; 🌿
</div>
""", unsafe_allow_html=True)
