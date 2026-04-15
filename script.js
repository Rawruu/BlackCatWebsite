// Configuration
// r/blackcats is community-curated — every post is a black cat
const REDDIT_API = 'https://www.reddit.com/r/blackcats/.json?limit=100';
// Bombay is the ONLY Cat API breed that is always solid black — used as fallback
const CAT_API_BOMBAY = 'https://api.thecatapi.com/v1/images/search?limit=10&breed_ids=bom';

// Elements
const catImage = document.getElementById('catImage');
const newCatBtn = document.getElementById('newCatBtn');
const downloadBtn = document.getElementById('downloadBtn');
const catInfo = document.getElementById('catInfo');
const catCount = document.getElementById('catCount');
const loadingSpinner = document.getElementById('loadingSpinner');

// State
let catCounter = parseInt(localStorage.getItem('catCounter') || '0');
let currentCatUrl = '';
let currentCatTitle = '';
let cachedPosts = []; // pool of Reddit posts — refilled as needed

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCountDisplay();
    fetchRandomCat();
});

// Event Listeners
newCatBtn.addEventListener('click', fetchRandomCat);
downloadBtn.addEventListener('click', downloadCat);

/**
 * Fetch a random black cat.
 * Strategy: Reddit r/blackcats (curated) → Bombay Cat API (always black).
 * NOTE: browsers block the User-Agent header, so we omit it intentionally.
 */
async function fetchRandomCat() {
    try {
        newCatBtn.disabled = true;
        downloadBtn.disabled = true;
        showLoadingSpinner(true);
        catInfo.textContent = 'Summoning a void from r/blackcats...';

        // Serve from cached pool first for instant loads
        if (cachedPosts.length > 0) {
            const idx = Math.floor(Math.random() * cachedPosts.length);
            const post = cachedPosts.splice(idx, 1)[0];
            displayCat(post);
            incrementCounter();
            return;
        }

        // Try Reddit — no custom headers (User-Agent is a forbidden browser header)
        try {
            const response = await fetch(REDDIT_API);
            if (response.ok) {
                const data = await response.json();
                const imagePosts = data.data.children
                    .map(p => p.data)
                    .filter(p =>
                        !p.stickied &&
                        !p.is_self &&
                        p.url &&
                        // Only trust direct Reddit image hosting; imgur links are less reliable
                        p.url.includes('i.redd.it')
                    )
                    .map(p => ({ url: p.url, title: p.title, author: p.author }));

                if (imagePosts.length > 0) {
                    cachedPosts = imagePosts; // cache for future clicks
                    const idx = Math.floor(Math.random() * cachedPosts.length);
                    const post = cachedPosts.splice(idx, 1)[0];
                    displayCat(post);
                    incrementCounter();
                    return;
                }
            }
        } catch (redditErr) {
            console.warn('Reddit unavailable, falling back to Cat API:', redditErr);
        }

        // Fallback: Bombay breed only — always black
        catInfo.textContent = 'Fetching a Bombay...';
        const catRes = await fetch(CAT_API_BOMBAY);
        if (!catRes.ok) throw new Error('Cat API request failed');
        const cats = await catRes.json();
        if (!cats.length) throw new Error('No cats returned from Cat API');
        const cat = cats[Math.floor(Math.random() * cats.length)];
        displayCat({ url: cat.url, title: 'Bombay', author: 'The Cat API' });
        incrementCounter();

    } catch (error) {
        console.error('Error fetching cat:', error);
        catInfo.textContent = '😿 Could not load a black cat. Check your connection and try again.';
        catImage.src = 'https://via.placeholder.com/600x400?text=Unable+to+Load+Cat';
    } finally {
        showLoadingSpinner(false);
        newCatBtn.disabled = false;
        downloadBtn.disabled = false;
    }
}

/**
 * Display cat image and info
 */
function displayCat({ url, title, author }) {
    currentCatUrl = url;
    currentCatTitle = title || 'Black Cat';

    catImage.src = currentCatUrl;
    catImage.alt = currentCatTitle;

    let infoText = `🐱 ${currentCatTitle}`;
    if (author && author !== 'The Cat API') {
        infoText += ` • Posted by u/${author}`;
    } else if (author) {
        infoText += ` • Source: ${author}`;
    }
    catInfo.textContent = infoText;
}

/**
 * Toggle loading spinner visibility
 */
function showLoadingSpinner(show) {
    loadingSpinner.classList.toggle('hidden', !show);
}

/**
 * Download the current cat image
 */
function downloadCat() {
    if (!currentCatUrl) {
        alert('No cat image to download!');
        return;
    }
    const link = document.createElement('a');
    link.href = currentCatUrl;
    link.download = `black-cat-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Increment and persist cat counter
 */
function incrementCounter() {
    catCounter++;
    localStorage.setItem('catCounter', catCounter);
    updateCountDisplay();
}

/**
 * Update the counter display
 */
function updateCountDisplay() {
    catCount.textContent = catCounter;
}
