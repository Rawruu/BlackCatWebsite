// Curated black-cat subreddits — every post here is a black cat
const SUBREDDITS = ['blackcats', 'SuperBlackCats', 'voidcats'];
const SORTS = ['hot', 'new', 'top'];

// Elements
const catImage      = document.getElementById('catImage');
const newCatBtn     = document.getElementById('newCatBtn');
const downloadBtn   = document.getElementById('downloadBtn');
const catInfo       = document.getElementById('catInfo');
const catCount      = document.getElementById('catCount');
const loadingSpinner = document.getElementById('loadingSpinner');

// State
let catCounter    = parseInt(localStorage.getItem('catCounter') || '0');
let currentCatUrl = '';
let pool          = [];   // all fetched posts
let seenUrls      = new Set();

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    updateCountDisplay();
    await fillPool();
    showNextCat();
});

newCatBtn.addEventListener('click', showNextCat);
downloadBtn.addEventListener('click', downloadCat);

// ── Pool management ───────────────────────────────────────────────────────────

/**
 * Fetch image posts from one Reddit sort endpoint.
 * Returns an array of { url, title, author, source } objects.
 * NOTE: browsers block the User-Agent header — omit it intentionally.
 */
async function fetchSubredditSort(sub, sort) {
    const qs = sort === 'top' ? '?t=month&limit=100' : '?limit=100';
    const url = `https://www.reddit.com/r/${sub}/${sort}.json${qs}`;
    try {
        const res = await fetch(url);
        if (!res.ok) return [];
        const data = await res.json();
        return data.data.children
            .map(c => c.data)
            .filter(d => !d.stickied && !d.is_self && d.url &&
                         d.url.includes('i.redd.it'))
            .map(d => ({
                url:    d.url,
                title:  d.title || 'Black Cat',
                author: d.author || 'anonymous',
                source: `r/${sub}`,
            }));
    } catch {
        return [];
    }
}

/**
 * Fill the pool from all subreddits + sorts in parallel.
 * Falls back to Bombay Cat API if Reddit yields nothing.
 */
async function fillPool() {
    catInfo.textContent = 'Summoning voids from Reddit…';

    const fetches = SUBREDDITS.flatMap(sub =>
        SORTS.map(sort => fetchSubredditSort(sub, sort))
    );
    const results = await Promise.allSettled(fetches);

    const newPosts = [];
    const urlsSeen = new Set();
    for (const r of results) {
        if (r.status !== 'fulfilled') continue;
        for (const post of r.value) {
            if (!urlsSeen.has(post.url)) {
                urlsSeen.add(post.url);
                newPosts.push(post);
            }
        }
    }

    if (newPosts.length > 0) {
        // Shuffle so hot/new/top interleave
        pool = shuffle(newPosts);
        console.log(`Pool filled: ${pool.length} cats`);
    } else {
        // Fallback: Bombay (always black)
        console.warn('Reddit returned 0 images, falling back to Bombay Cat API');
        catInfo.textContent = 'Fetching Bombay cats…';
        try {
            const res = await fetch(
                'https://api.thecatapi.com/v1/images/search?limit=50&breed_ids=bom'
            );
            if (res.ok) {
                const cats = await res.json();
                pool = cats.map(c => ({
                    url:    c.url,
                    title:  'Bombay',
                    author: 'The Cat API',
                    source: 'Cat API — Bombay',
                }));
                console.log(`Bombay fallback: ${pool.length} cats`);
            }
        } catch (e) {
            console.error('Bombay fallback also failed:', e);
        }
    }
}

function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

/** Pick one unseen cat from the pool (refills if exhausted). */
async function pickCat() {
    let unseen = pool.filter(c => !seenUrls.has(c.url));
    if (unseen.length === 0) {
        // Refill
        seenUrls.clear();
        await fillPool();
        unseen = pool;
    }
    if (unseen.length === 0) return null;
    const idx = Math.floor(Math.random() * unseen.length);
    return unseen[idx];
}

// ── Display ───────────────────────────────────────────────────────────────────

async function showNextCat() {
    try {
        newCatBtn.disabled  = true;
        downloadBtn.disabled = true;
        showLoadingSpinner(true);

        const cat = await pickCat();
        if (!cat) {
            catInfo.textContent = '😿 No cats available. Try refreshing the page.';
            return;
        }

        seenUrls.add(cat.url);
        currentCatUrl = cat.url;

        catImage.src = cat.url;
        catImage.alt = cat.title;

        let info = `🐱 ${cat.title}`;
        if (cat.source.startsWith('r/')) info += ` • ${cat.source} • u/${cat.author}`;
        else info += ` • ${cat.source}`;
        catInfo.textContent = info;

        incrementCounter();
    } catch (err) {
        console.error(err);
        catInfo.textContent = '😿 Something went wrong. Please try again.';
    } finally {
        showLoadingSpinner(false);
        newCatBtn.disabled  = false;
        downloadBtn.disabled = false;
    }
}

function showLoadingSpinner(show) {
    loadingSpinner.classList.toggle('hidden', !show);
}

function downloadCat() {
    if (!currentCatUrl) { alert('No cat image to download!'); return; }
    const a = document.createElement('a');
    a.href     = currentCatUrl;
    a.download = `black-cat-${Date.now()}.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function incrementCounter() {
    catCounter++;
    localStorage.setItem('catCounter', catCounter);
    updateCountDisplay();
}

function updateCountDisplay() {
    catCount.textContent = catCounter;
}
