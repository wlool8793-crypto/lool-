# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Docs Clone - a Google Docs clone built with vanilla HTML, CSS, and JavaScript. It's a complete single-page application that provides rich text editing, document management, and export functionality without any external dependencies.

## Development Status

### ✅ Completed Features
- **Rich Text Editor**: Full formatting toolbar with bold, italic, underline, headings, lists, alignment, colors
- **Document Management**: Create, save, load, delete documents with localStorage persistence
- **Auto-save Functionality**: Automatic saving every 5 seconds with visual feedback
- **Export System**: Export to HTML and plain text formats
- **Advanced Features**: Undo/redo, word count, keyboard shortcuts
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, Google Docs-inspired interface

### 🎯 Key Technologies
- **HTML5**: ContentEditable div for rich text editing
- **CSS3**: Modern styling with flexbox, grid, CSS variables, animations
- **ES6+ JavaScript**: Modern JavaScript with classes, modules, async/await
- **Web APIs**: localStorage, File API, Clipboard API, Document.execCommand
- **No Frameworks**: Pure vanilla JavaScript implementation

## File Structure

```
docs-making/
├── index.html          # Main application HTML structure
├── styles.css          # All CSS styling and responsive design
├── script.js           # Main application logic and features
├── README.md           # Comprehensive documentation
└── CLAUDE.md           # This file - development guidance
```

## Architecture

### Core Components
- **Editor Engine**: ContentEditable-based rich text editor
- **Document Manager**: localStorage-based document persistence
- **Toolbar System**: Dynamic formatting controls
- **Export System**: HTML and plain text export functionality
- **State Management**: Undo/redo stack and document state

### Key Design Patterns
- **Single Page Application**: No page reloads, smooth transitions
- **Event-Driven Architecture**: Comprehensive event handling
- **State Management**: Global state with undo/redo capabilities
- **Modular Functions**: Well-organized, reusable functions

## Development Commands

### Running the Application
```bash
# Simply open in browser (no build process required)
open index.html

# Or use a local server (recommended for development)
python -m http.server 8000
# Visit http://localhost:8000
```

### Testing
```bash
# No formal test suite (vanilla JS project)
# Test manually in different browsers:
# - Chrome (recommended)
# - Firefox
# - Safari
# - Edge
```

### Building for Production
```bash
# No build process required
# Files are production-ready:
# - Minimize CSS/JS if desired
# - Add service worker for PWA features
# - Optimize images and assets
```

## Key Implementation Details

### Document Storage
```javascript
// Documents are stored in localStorage as:
{
  id: "unique-id",
  title: "Document Title",
  content: "HTML content",
  createdAt: "ISO timestamp",
  modifiedAt: "ISO timestamp"
}
```

### Editor Features
- **Formatting**: Uses document.execCommand for cross-browser compatibility
- **Auto-save**: Saves every 5 seconds using setInterval
- **Undo/Redo**: Custom stack implementation with 50-state limit
- **Word Count**: Real-time counting using textContent

### Keyboard Shortcuts
- `Ctrl/Cmd + B`: Bold
- `Ctrl/Cmd + I`: Italic
- `Ctrl/Cmd + U`: Underline
- `Ctrl/Cmd + S`: Save
- `Ctrl/Cmd + O`: Open document manager
- `Ctrl/Cmd + N`: New document
- `Ctrl/Cmd + Z`: Undo
- `Ctrl/Cmd + Y`: Redo

## Browser Compatibility

### ✅ Fully Supported
- Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- Mobile browsers with touch optimization
- All modern web standards supported

### ⚠️ Considerations
- No Internet Explorer support (ES6+ required)
- localStorage limits apply (~5-10MB)
- ContentEditable differences across browsers

## Code Conventions

### JavaScript Style
- **ES6+ Features**: Classes, arrow functions, destructuring, template literals
- **Naming**: camelCase for variables/functions, PascalCase for classes
- **Comments**: Comprehensive JSDoc-style comments
- **Error Handling**: Try-catch blocks with user-friendly toast notifications

### CSS Architecture
- **CSS Variables**: Theming with custom properties in :root
- **BEM-like Naming**: Component-based class names
- **Responsive Design**: Mobile-first approach with media queries
- **Animations**: Smooth transitions and keyframe animations

### HTML Structure
- **Semantic HTML5**: Proper use of header, main, section elements
- **Accessibility**: ARIA labels and keyboard navigation
- **Clean Structure**: Well-organized, readable markup

## Common Development Tasks

### Adding New Features
1. **Plan the Feature**: Consider UI placement and user experience
2. **Update HTML**: Add necessary elements to index.html
3. **Style the Feature**: Add CSS to styles.css
4. **Implement Logic**: Add JavaScript functions to script.js
5. **Test Thoroughly**: Test in multiple browsers
6. **Update Documentation**: Update README.md if needed

### Debugging Issues
- **Browser DevTools**: Use console.log and debugger statements
- **Check Browser Compatibility**: Test in multiple browsers
- **Verify localStorage**: Check browser storage limits and permissions
- **Test Edge Cases**: Empty documents, large content, special characters

### Performance Optimization
- **DOM Manipulation**: Minimize DOM updates and use efficient selectors
- **Event Handling**: Use event delegation and proper cleanup
- **Memory Management**: Clean up intervals and event listeners
- **localStorage Usage**: Be mindful of storage limits

## Security Considerations

### Data Safety
- **Client-side Only**: No server communication
- **localStorage Security**: Data accessible only on same domain
- **Input Sanitization**: Basic HTML escaping for user input
- **No External Dependencies**: Reduced security attack surface

### Limitations
- **No Authentication**: All documents accessible on device
- **No Encryption**: Data stored in plain text
- **No Backup**: Users must manually backup important documents

## Extension Ideas

### Advanced Features
- **Real-time Collaboration**: WebSocket-based multi-user editing
- **Cloud Storage**: Google Drive, Dropbox integration
- **Advanced Export**: PDF, Markdown, DOCX formats
- **Version History**: Document version tracking and restoration
- **Search & Replace**: Find and replace functionality
- **Table Support**: Insert and edit tables
- **Image Insertion**: Base64 encoded image support
- **Dark Mode**: Theme switching functionality

### Technical Improvements
- **Service Worker**: PWA capabilities for offline use
- **IndexedDB**: Better storage for large documents
- **Web Workers**: Heavy processing in background threads
- **Compression**: Compress documents for storage efficiency
- **Caching**: Better performance for repeated operations

## Troubleshooting

### Common Issues
- **localStorage Full**: Clear browser data or implement storage management
- **Formatting Not Working**: Check text selection and browser compatibility
- **Auto-save Not Working**: Verify localStorage permissions
- **Export Issues**: Check browser download permissions

### Debug Steps
1. **Check Browser Console**: Look for JavaScript errors
2. **Verify localStorage**: Check if data is being stored
3. **Test in Different Browser**: Isolate browser-specific issues
4. **Check File Permissions**: Ensure files have proper access rights

## Testing Checklist

### Manual Testing
- [ ] Create new document
- [ ] Edit document title
- [ ] Apply all formatting options
- [ ] Use keyboard shortcuts
- [ ] Test undo/redo functionality
- [ ] Verify auto-save works
- [ ] Test document management (save/load/delete)
- [ ] Export to HTML and plain text
- [ ] Test on mobile devices
- [ ] Test in different browsers

### Performance Testing
- [ ] Test with large documents (10,000+ words)
- [ ] Verify responsive design on various screen sizes
- [ ] Check memory usage during extended editing sessions
- [ ] Test localStorage limits and behavior

## Deployment

### Static Deployment
The application can be deployed to any static hosting service:
- **GitHub Pages**: Free hosting for public repositories
- **Netlify**: Drag-and-drop deployment
- **Vercel**: Static site hosting
- **Any Web Server**: Simply serve the static files

### Production Considerations
- **Minification**: Minify CSS and JavaScript files
- **Compression**: Enable gzip compression on server
- **Caching**: Set proper cache headers for assets
- **HTTPS**: Serve over HTTPS for security
- **CDN**: Use CDN for fonts and external assets

## Notes

This is a complete, production-ready application that demonstrates modern web development capabilities using only vanilla web technologies. It serves as an excellent foundation for more advanced document editing applications or educational resource for learning web development.