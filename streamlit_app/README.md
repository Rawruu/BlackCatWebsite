# Streamlit Black Cats App

A Streamlit app that displays random black cat pictures from r/blackcats subreddit.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

- 🐱 Fetches random black cat images from r/blackcats
- ⬇️ Download images to your computer
- 📊 Tracks number of cats viewed
- 🎨 Beautiful dark theme UI
- 📱 Works on desktop, tablet, and mobile

## How to Use

1. Click "Get New Black Cat" button to fetch a random cat image
2. View the cat's information (title and original poster)
3. Click "Download Image" to save the picture
4. The counter will track how many cats you've viewed

## Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect your GitHub repository
4. Select the `streamlit_app` folder
5. Point to `app.py` as the main script

### Run Locally

```bash
streamlit run app.py
```

### Run on a Server

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Then access at `http://your-server-address:8501`

## Requirements

- Python 3.8+
- Streamlit
- Requests
- Pillow (PIL)

## Notes

- The app fetches data from Reddit's public API (no authentication required)
- Images are fetched on-demand when you click the button
- The counter is session-based (resets on page refresh)

Enjoy your black cats! 🐱⬛
