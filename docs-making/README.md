# Docs Clone - Google Docs Clone

A fully functional web-based collaborative document editor similar to Google Docs, built with vanilla HTML, CSS, and JavaScript. Features rich text editing, document management, auto-save functionality, and export capabilities.

## Features

### 📝 Rich Text Editor
- **Formatting Options**: Bold, italic, underline, strikethrough, subscript, superscript
- **Headings**: Support for H1-H6 heading formats
- **Lists**: Bulleted and numbered lists
- **Text Alignment**: Left, center, right, and justify alignment
- **Colors**: Text color and highlight color selection
- **Font Styles**: Clean, modern typography with Inter font

### 📄 Document Management
- **Create New Documents**: Start with a blank document
- **Save Documents**: Auto-save every 5 seconds + manual save
- **Load Documents**: Open previously saved documents
- **Delete Documents**: Remove unwanted documents
- **Document List**: Organized by modification date
- **Title Editing**: Edit document titles inline

### 💾 Storage & Persistence
- **Local Storage**: All documents saved to browser localStorage
- **Auto-save**: Automatic saving every 5 seconds
- **Save Status**: Real-time save status indicators
- **Data Recovery**: Prevents accidental data loss

### 📤 Export Functionality
- **HTML Export**: Export as formatted HTML file
- **Plain Text Export**: Export as clean text file
- **Preserved Formatting**: Maintains document structure in exports

### ⌨️ Keyboard Shortcuts
- `Ctrl/Cmd + B`: Bold text
- `Ctrl/Cmd + I`: Italic text
- `Ctrl/Cmd + U`: Underline text
- `Ctrl/Cmd + S`: Save document
- `Ctrl/Cmd + O`: Open document manager
- `Ctrl/Cmd + N`: New document
- `Ctrl/Cmd + Z`: Undo
- `Ctrl/Cmd + Y` or `Ctrl/Cmd + Shift + Z`: Redo

### 🎨 User Interface
- **Modern Design**: Clean, Google Docs-inspired interface
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Word Count**: Live word count display
- **Toolbar**: Intuitive formatting toolbar with icons
- **Modal Dialogs**: Clean document management interface
- **Toast Notifications**: User-friendly feedback messages

### 🛠️ Advanced Features
- **Undo/Redo**: Full undo/redo functionality with state management
- **Word Count**: Real-time word count tracking
- **Auto-save**: Configurable auto-save intervals
- **Cross-browser Compatibility**: Works in all modern browsers
- **Performance Optimized**: Efficient for large documents

## Installation & Setup

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- No additional software or dependencies required

### Quick Start
1. **Download the files** or clone this repository
2. **Open `index.html`** in your web browser
3. **Start typing** - that's it!

### File Structure
```
docs-making/
├── index.html          # Main application file
├── styles.css          # All styling and CSS
├── script.js           # Main application logic
└── README.md           # This file
```

## Usage Guide

### Creating Your First Document
1. Open `index.html` in your browser
2. Click in the editor area and start typing
3. Use the toolbar to format your text
4. Your document auto-saves every 5 seconds

### Document Management
1. **Open Document Manager**: Click the folder icon or press `Ctrl+O`
2. **Create New Document**: Click "New Document" or press `Ctrl+N`
3. **Load Document**: Click on any document in the list
4. **Delete Document**: Click the trash icon next to a document

### Formatting Text
1. **Select Text**: Highlight the text you want to format
2. **Use Toolbar**: Click formatting buttons in the toolbar
3. **Keyboard Shortcuts**: Use keyboard shortcuts for faster formatting
4. **Apply Styles**: Choose headings, lists, or alignment options

### Exporting Documents
1. **Open Export Dialog**: Click the download icon in the header
2. **Choose Format**: Select HTML or Plain Text export
3. **Download File**: File downloads automatically to your computer

## Technical Implementation

### Architecture
- **Single Page Application (SPA)**: No page reloads required
- **Vanilla JavaScript**: No frameworks or dependencies
- **Component-based Structure**: Organized, maintainable code
- **Event-driven Design**: Responsive user interactions

### Key Technologies
- **HTML5**: Semantic markup with contenteditable
- **CSS3**: Modern styling with flexbox, grid, and animations
- **ES6+ JavaScript**: Modern JavaScript features
- **Web APIs**: localStorage, File API, Clipboard API
- **CSS Custom Properties**: Theming and consistency

### Data Storage
```javascript
// Document structure stored in localStorage
{
  id: "unique-id",
  title: "Document Title",
  content: "HTML content",
  createdAt: "2024-01-01T00:00:00.000Z",
  modifiedAt: "2024-01-01T00:00:00.000Z"
}
```

### Editor Implementation
- **ContentEditable**: Using browser's native editing capabilities
- **Document.execCommand**: Cross-browser formatting commands
- **State Management**: Undo/redo stack management
- **Event Handling**: Comprehensive input and keyboard event handling

## Browser Compatibility

### ✅ Supported Browsers
- **Chrome**: 80+ (recommended)
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

### ⚠️ Limited Support
- **Internet Explorer**: Not supported (ES6+ features required)
- **Mobile Browsers**: Full support with touch-optimized interface

## Performance Considerations

### Large Document Support
- **Optimized Rendering**: Efficient DOM manipulation
- **Memory Management**: Proper cleanup of event listeners
- **Stack Limits**: Undo/redo stack limited to 50 states
- **Local Storage**: Browser storage limits apply (~5-10MB)

### Best Practices
- **Auto-save**: Configurable intervals prevent data loss
- **Debouncing**: Optimized input handling
- **Caching**: Efficient DOM updates
- **Minification**: Production-ready code structure

## Security Considerations

### Data Safety
- **Client-side Only**: No server communication required
- **Local Storage**: Data stays in user's browser
- **No Tracking**: No analytics or external requests
- **Sanitization**: Basic HTML escaping for security

### Limitations
- **No Authentication**: All documents accessible on the device
- **No Encryption**: Data stored in plain text in localStorage
- **No Backup**: Users must manually backup important documents

## Troubleshooting

### Common Issues

#### Document Not Saving
- **Check Browser Settings**: Ensure localStorage is enabled
- **Clear Browser Cache**: Try clearing cache and cookies
- **Check Storage Space**: Verify available localStorage space

#### Formatting Not Working
- **Text Selection**: Ensure text is selected before formatting
- **Browser Compatibility**: Try a different browser
- **JavaScript Enabled**: Verify JavaScript is enabled

#### Export Issues
- **Browser Permissions**: Check download permissions
- **Pop-up Blocker**: Disable pop-up blocker for the site
- **File Size**: Large documents may take time to process

### Performance Issues
- **Large Documents**: Consider splitting very large documents
- **Browser Memory**: Close other tabs if experiencing slowdown
- **Device Performance**: Older devices may be slower

## Development

### Code Structure
```javascript
// Global state management
let currentDocument = null;
let documents = [];
let undoStack = [];
let redoStack = [];

// Core functions
function initializeApp()           // Application setup
function createNewDocument()       // Document creation
function saveCurrentDocument()     // Document saving
function loadDocument()            // Document loading
function formatText()              // Text formatting
function exportDocument()          // Export functionality
```

### Customization
- **Colors**: Modify CSS custom properties in `:root`
- **Fonts**: Change font family in CSS variables
- **Auto-save Interval**: Adjust timer in `startAutoSaveTimer()`
- **UI Layout**: Modify CSS grid and flexbox properties

### Extending Features
- **Additional Formats**: Add PDF, Markdown export
- **Collaboration**: Add WebSocket support for real-time editing
- **Cloud Storage**: Add Google Drive, Dropbox integration
- **Advanced Formatting**: Add tables, images, media

## Contributing

### Getting Started
1. **Fork the Repository**: Create your own copy
2. **Make Changes**: Implement your features
3. **Test Thoroughly**: Ensure cross-browser compatibility
4. **Submit Pull Request**: Contribute back to the project

### Development Guidelines
- **Code Style**: Follow existing patterns and conventions
- **Comments**: Document complex logic and functions
- **Testing**: Test in multiple browsers and devices
- **Performance**: Optimize for speed and efficiency

## License

This project is open source and available under the MIT License. You are free to use, modify, and distribute this software for any purpose.

## Support

For support, feature requests, or bug reports:
1. **Check the README**: Review existing documentation
2. **Search Issues**: Check if your issue has been reported
3. **Create New Issue**: Provide detailed information about your problem

## Acknowledgments

- **Google Docs**: Inspiration for the user interface
- **Font Awesome**: Icon library used throughout the application
- **Inter Font**: Beautiful typeface from Google Fonts
- **Modern Web APIs**: Leveraging browser capabilities for rich functionality

---

**Built with ❤️ using vanilla web technologies**

Docs Clone provides a complete document editing experience without any external dependencies. Perfect for quick note-taking, document drafting, or as a foundation for more advanced document management systems.