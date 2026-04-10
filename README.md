# Random Black Cats Website 🐱

A charming website that displays random pictures of black cats! Perfect for cat lovers who can't get enough feline cuteness.

## Features

- **Random Cat Images** - Click the button to see a new adorable black cat
- **Beautiful Dark Theme** - Sleek, modern design with a dark background
- **Responsive Design** - Works great on desktop, tablet, and mobile
- **Download Images** - Save your favorite cat photos
- **Counter** - Tracks how many cats you've viewed (saved in browser storage)
- **Cat Information** - Display breed name and temperament when available

## How to Use

1. Open `index.html` in your web browser
2. Click "Get New Cat" to load a random black cat image
3. Click "Download" to save the image to your computer
4. Repeat as many times as you like!

## Technologies Used

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with animations and gradients
- **JavaScript** - Fetch API for cat image retrieval
- **The Cat API** - Source of beautiful cat images

## Files

- `index.html` - Main HTML structure
- `styles.css` - All styling and animations
- `script.js` - JavaScript logic for fetching and managing cats
- `README.md` - This file

## API Information

This website uses [The Cat API](https://thecatapi.com/) to fetch random cat images. The API provides extensive cat image data including breed information, characteristics, and more.

## Customization

### Change the color scheme
Edit `styles.css` and modify the color variables:
- `#ffd700` - Gold accent color
- `#1a1a1a` - Dark background
- `#f0f0f0` - Light text

### Adjust image size
In `styles.css`, modify `.image-container img`:
```css
max-height: 500px;  /* Change this value */
```

### Add more features
Some ideas:
- Filter by breed
- Share to social media
- Create a favorites collection
- Add keyboard shortcuts (spacebar for new cat)

## Troubleshooting

**"Unable to Load Cat" error:**
- Check your internet connection
- The API might be temporarily down
- Try refreshing the page

**Images not loading:**
- Make sure JavaScript is enabled
- Clear your browser cache
- Check the browser console for errors

## License

Feel free to modify and use this for your own purposes!

## Enjoy! 🐾

Made with ❤️ for cat lovers everywhere.
