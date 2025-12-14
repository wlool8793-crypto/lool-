# Icon Generation Guide

## Quick Setup
The PWA requires icons in multiple sizes. Use one of these methods:

### Method 1: Online Tool (Easiest)
1. Visit https://www.pwabuilder.com/imageGenerator
2. Upload the `icon.svg` file
3. Download the generated icon pack
4. Extract all PNG files to this directory

### Method 2: Using ImageMagick (Command Line)
If you have ImageMagick installed, run these commands from this directory:

```bash
# Convert SVG to various PNG sizes
convert icon.svg -resize 72x72 icon-72x72.png
convert icon.svg -resize 96x96 icon-96x96.png
convert icon.svg -resize 128x128 icon-128x128.png
convert icon.svg -resize 144x144 icon-144x144.png
convert icon.svg -resize 152x152 icon-152x152.png
convert icon.svg -resize 192x192 icon-192x192.png
convert icon.svg -resize 384x384 icon-384x384.png
convert icon.svg -resize 512x512 icon-512x512.png
```

### Method 3: Using Node.js Script
Install sharp: `npm install -D sharp`

Then create and run this script:

```javascript
// generate-icons.js
const sharp = require('sharp');
const fs = require('fs');

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];

async function generateIcons() {
  const svgBuffer = fs.readFileSync('./icon.svg');

  for (const size of sizes) {
    await sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(`./icon-${size}x${size}.png`);
    console.log(`Generated icon-${size}x${size}.png`);
  }
}

generateIcons();
```

### Method 4: Use Figma/Sketch/Photoshop
1. Import `icon.svg`
2. Export at each required size:
   - 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512
3. Save as PNG files with correct names

## Required Icon Sizes
- icon-72x72.png (iOS)
- icon-96x96.png (Android)
- icon-128x128.png (Chrome Web Store)
- icon-144x144.png (Windows)
- icon-152x152.png (iOS)
- icon-192x192.png (Android, Manifest)
- icon-384x384.png (Android)
- icon-512x512.png (Splash screens, Android)

## Apple Touch Icon
Also create:
- apple-touch-icon.png (180x180) for iOS devices

## Maskable Icons
For best Android support, consider creating maskable icons with safe zone padding.
The current icons are marked as "any maskable" which works for both purposes.
