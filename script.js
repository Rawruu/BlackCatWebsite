// Configuration
const REDDIT_API = 'https://www.reddit.com/r/blackcats/.json';

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
let redditPosts = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCountDisplay();
    fetchRandomCat();
});

// Event Listeners
newCatBtn.addEventListener('click', fetchRandomCat);
downloadBtn.addEventListener('click', downloadCat);

/**
 * Fetch a random black cat image from r/blackcats subreddit
 */
async function fetchRandomCat() {
    try {
        newCatBtn.disabled = true;
        downloadBtn.disabled = true;
        showLoadingSpinner(true);
        catInfo.textContent = 'Loading a precious void from r/blackcats...';

        const response = await fetch(REDDIT_API, {
            headers: {
                'User-Agent': 'BlackCatWebsite/1.0'
            }
        });

        if (!response.ok) {
            throw new Error(`Reddit API Error: ${response.statusText}`);
        }

        const data = await response.json();
        const posts = data.data.children;

        if (!posts || posts.length === 0) {
            throw new Error('No posts found');
        }

        // Filter for image posts
        const imagePosts = posts.filter(post => {
            const url = post.data.url;
            return url && (
                url.includes('i.redd.it') || 
                url.includes('imgur.com') ||
                url.match(/\.(jpg|jpeg|png|gif)$/i)
            );
        });

        if (imagePosts.length === 0) {
            throw new Error('No image posts found');
        }

        // Get random post
        const randomPost = imagePosts[Math.floor(Math.random() * imagePosts.length)];
        displayCat(randomPost.data);
        incrementCounter();
    } catch (error) {
        console.error('Error fetching cat:', error);
        catInfo.textContent = '😿 Oops! Could not load a black cat. Please try again.';
        catImage.src = 'https://via.placeholder.com/600x400?text=Unable+to+Load+Black+Cat&bgColor=%23333&textColor=%23ffd700';
    } finally {
        showLoadingSpinner(false);
        newCatBtn.disabled = false;
        downloadBtn.disabled = false;
    }
}

/**
 * Display cat image and info from Reddit post
 */
function displayCat(postData) {
    currentCatUrl = postData.url;
    currentCatTitle = postData.title || 'Black Cat';
    
    catImage.src = currentCatUrl;
    catImage.alt = currentCatTitle;
    
    // Display title and subreddit info
    const author = postData.author || 'unknown';
    const subreddit = postData.subreddit || 'blackcats';
    let infoText = `🐱 ${currentCatTitle}`;
    infoText += ` • Posted by u/${author}`;
    
    catInfo.textContent = infoText;
}

/**
 * Toggle loading spinner
 */
function showLoadingSpinner(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
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
 * Increment and display cat counter
 */
function incrementCounter() {
    catCounter++;
    localStorage.setItem('catCounter', catCounter);
    updateCountDisplay();
}

/**
 * Update counter display
 */
function updateCountDisplay() {
    catCount.textContent = catCounter;
}
