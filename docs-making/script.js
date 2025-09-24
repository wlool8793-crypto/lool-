// Docs Clone - Main Application JavaScript

// Global state
let currentDocument = null;
let documents = [];
let autoSaveTimer = null;
let isAutoSaving = false;
let undoStack = [];
let redoStack = [];
let currentDocumentId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadDocuments();
    setupKeyboardShortcuts();
});

// Initialize application
function initializeApp() {
    // Set up editor placeholder
    const editor = document.getElementById('editor');
    editor.addEventListener('input', handleEditorInput);
    editor.addEventListener('keyup', handleEditorKeyup);
    editor.addEventListener('paste', handlePaste);

    // Initialize with a new document
    createNewDocument();

    // Start auto-save timer
    startAutoSaveTimer();

    // Update word count
    updateWordCount();
}

// Setup event listeners
function setupEventListeners() {
    // Document title input
    const titleInput = document.getElementById('documentTitle');
    titleInput.addEventListener('input', handleTitleChange);

    // Editor events for undo/redo
    const editor = document.getElementById('editor');
    editor.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                undo();
            } else if ((e.key === 'z' && e.shiftKey) || (e.key === 'y')) {
                e.preventDefault();
                redo();
            }
        }
    });

    // Modal close on outside click
    window.addEventListener('click', function(e) {
        const docModal = document.getElementById('documentModal');
        const exportModal = document.getElementById('exportModal');

        if (e.target === docModal) {
            closeDocumentModal();
        }
        if (e.target === exportModal) {
            closeExportModal();
        }
    });
}

// Document Management System
function loadDocuments() {
    try {
        const saved = localStorage.getItem('docsClone_documents');
        documents = saved ? JSON.parse(saved) : [];
        updateDocumentList();
    } catch (error) {
        console.error('Error loading documents:', error);
        showToast('Error loading documents', 'error');
    }
}

function saveDocuments() {
    try {
        localStorage.setItem('docsClone_documents', JSON.stringify(documents));
    } catch (error) {
        console.error('Error saving documents:', error);
        showToast('Error saving documents', 'error');
    }
}

function createNewDocument() {
    // Save current document if it exists and has content
    if (currentDocument && (currentDocument.content.trim() !== '' || currentDocument.title !== 'Untitled Document')) {
        saveCurrentDocument();
    }

    // Create new document
    currentDocument = {
        id: generateId(),
        title: 'Untitled Document',
        content: '',
        createdAt: new Date().toISOString(),
        modifiedAt: new Date().toISOString()
    };

    currentDocumentId = currentDocument.id;

    // Update UI
    document.getElementById('documentTitle').value = currentDocument.title;
    document.getElementById('editor').innerHTML = currentDocument.content;
    updateWordCount();
    updateSaveStatus('saved');

    // Clear undo/redo stacks
    undoStack = [];
    redoStack = [];

    showToast('New document created', 'success');
}

function saveCurrentDocument() {
    if (!currentDocument) return;

    const title = document.getElementById('documentTitle').value || 'Untitled Document';
    const content = document.getElementById('editor').innerHTML;

    currentDocument.title = title;
    currentDocument.content = content;
    currentDocument.modifiedAt = new Date().toISOString();

    // Update or add to documents array
    const existingIndex = documents.findIndex(doc => doc.id === currentDocument.id);
    if (existingIndex >= 0) {
        documents[existingIndex] = currentDocument;
    } else {
        documents.push(currentDocument);
    }

    saveDocuments();
    updateDocumentList();
    updateSaveStatus('saved');
}

function loadDocument(documentId) {
    const document = documents.find(doc => doc.id === documentId);
    if (!document) return;

    // Save current document first
    if (currentDocument && (currentDocument.content.trim() !== '' || currentDocument.title !== 'Untitled Document')) {
        saveCurrentDocument();
    }

    // Load selected document
    currentDocument = { ...document };
    currentDocumentId = document.id;

    // Update UI
    document.getElementById('documentTitle').value = currentDocument.title;
    document.getElementById('editor').innerHTML = currentDocument.content;
    updateWordCount();
    updateSaveStatus('saved');

    // Clear undo/redo stacks
    undoStack = [];
    redoStack = [];

    closeDocumentModal();
    showToast('Document loaded', 'success');
}

function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document?')) return;

    documents = documents.filter(doc => doc.id !== documentId);
    saveDocuments();
    updateDocumentList();

    // If deleting current document, create new one
    if (currentDocumentId === documentId) {
        createNewDocument();
    }

    showToast('Document deleted', 'success');
}

function updateDocumentList() {
    const listContainer = document.getElementById('documentList');
    listContainer.innerHTML = '';

    if (documents.length === 0) {
        listContainer.innerHTML = '<p style="text-align: center; color: var(--gray-color); padding: 20px;">No documents yet. Create your first document!</p>';
        return;
    }

    // Sort documents by modified date (newest first)
    const sortedDocs = [...documents].sort((a, b) => new Date(b.modifiedAt) - new Date(a.modifiedAt));

    sortedDocs.forEach(doc => {
        const docElement = createDocumentElement(doc);
        listContainer.appendChild(docElement);
    });
}

function createDocumentElement(doc) {
    const div = document.createElement('div');
    div.className = `document-item ${currentDocumentId === doc.id ? 'selected' : ''}`;

    const created = new Date(doc.createdAt).toLocaleDateString();
    const modified = new Date(doc.modifiedAt).toLocaleDateString();

    div.innerHTML = `
        <div class="document-info" onclick="loadDocument('${doc.id}')">
            <div class="document-title">${escapeHtml(doc.title)}</div>
            <div class="document-meta">Created: ${created} • Modified: ${modified}</div>
        </div>
        <div class="document-actions">
            <button class="btn btn-danger btn-sm" onclick="deleteDocument('${doc.id}')" title="Delete">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;

    return div;
}

// Rich Text Editor Functions
function formatText(command, value = null) {
    document.execCommand(command, false, value);
    document.getElementById('editor').focus();
    saveState();
    updateToolbarState();
}

function updateToolbarState() {
    const commands = ['bold', 'italic', 'underline', 'strikeThrough', 'subscript', 'superscript',
                      'justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'];

    commands.forEach(command => {
        const btn = document.querySelector(`[onclick="formatText('${command}')"]`);
        if (btn) {
            if (document.queryCommandState(command)) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    });
}

// Auto-save functionality
function startAutoSaveTimer() {
    if (autoSaveTimer) clearInterval(autoSaveTimer);

    autoSaveTimer = setInterval(() => {
        if (!isAutoSaving) {
            autoSave();
        }
    }, 5000); // Auto-save every 5 seconds
}

function autoSave() {
    if (!currentDocument) return;

    const content = document.getElementById('editor').innerHTML;
    const title = document.getElementById('documentTitle').value;

    if (content.trim() === '' && title === 'Untitled Document') return;

    isAutoSaving = true;
    updateSaveStatus('saving');

    setTimeout(() => {
        saveCurrentDocument();
        isAutoSaving = false;
        updateSaveStatus('saved');
    }, 500);
}

function updateSaveStatus(status) {
    const saveStatus = document.getElementById('saveStatus');

    switch (status) {
        case 'saving':
            saveStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            saveStatus.className = 'save-status saving';
            break;
        case 'saved':
            saveStatus.innerHTML = '<i class="fas fa-check"></i> Saved';
            saveStatus.className = 'save-status';
            break;
    }
}

// Word count functionality
function updateWordCount() {
    const editor = document.getElementById('editor');
    const text = editor.innerText || editor.textContent || '';
    const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;
    document.getElementById('wordCount').textContent = words;
}

// Event Handlers
function handleEditorInput() {
    updateWordCount();
    updateSaveStatus('saving');
    setTimeout(() => {
        updateSaveStatus('saved');
    }, 1000);
    saveState();
    updateToolbarState();
}

function handleEditorKeyup() {
    updateWordCount();
}

function handleTitleChange() {
    updateSaveStatus('saving');
    setTimeout(() => {
        saveCurrentDocument();
    }, 1000);
}

function handlePaste(e) {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
}

// Undo/Redo functionality
function saveState() {
    const editor = document.getElementById('editor');
    const content = editor.innerHTML;

    if (undoStack.length === 0 || undoStack[undoStack.length - 1] !== content) {
        undoStack.push(content);
        redoStack = [];

        // Limit stack size
        if (undoStack.length > 50) {
            undoStack.shift();
        }
    }
}

function undo() {
    if (undoStack.length > 1) {
        redoStack.push(undoStack.pop());
        const content = undoStack[undoStack.length - 1];
        document.getElementById('editor').innerHTML = content;
        updateWordCount();
        updateToolbarState();
    }
}

function redo() {
    if (redoStack.length > 0) {
        const content = redoStack.pop();
        undoStack.push(content);
        document.getElementById('editor').innerHTML = content;
        updateWordCount();
        updateToolbarState();
    }
}

// Export functionality
function exportDocument() {
    document.getElementById('exportModal').classList.add('active');
}

function closeExportModal() {
    document.getElementById('exportModal').classList.remove('active');
}

function exportAsHTML() {
    const title = document.getElementById('documentTitle').value || 'Untitled Document';
    const content = document.getElementById('editor').innerHTML;

    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; }
        p { margin-bottom: 16px; }
        ul, ol { margin-bottom: 16px; }
        blockquote { border-left: 4px solid #ccc; margin: 16px 0; padding-left: 16px; }
        code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
        pre { background-color: #f4f4f4; padding: 16px; border-radius: 4px; overflow-x: auto; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>${escapeHtml(title)}</h1>
    ${content}
</body>
</html>`;

    downloadFile(htmlContent, title + '.html', 'text/html');
    closeExportModal();
    showToast('Document exported as HTML', 'success');
}

function exportAsPlainText() {
    const title = document.getElementById('documentTitle').value || 'Untitled Document';
    const content = document.getElementById('editor').innerText || '';

    const textContent = `${title}\n\n${content}`;
    downloadFile(textContent, title + '.txt', 'text/plain');
    closeExportModal();
    showToast('Document exported as plain text', 'success');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// Modal functions
function openDocumentModal() {
    document.getElementById('documentModal').classList.add('active');
    updateDocumentList();
}

function closeDocumentModal() {
    document.getElementById('documentModal').classList.remove('active');
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only apply shortcuts when not in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'b':
                    e.preventDefault();
                    formatText('bold');
                    break;
                case 'i':
                    e.preventDefault();
                    formatText('italic');
                    break;
                case 'u':
                    e.preventDefault();
                    formatText('underline');
                    break;
                case 's':
                    e.preventDefault();
                    saveCurrentDocument();
                    showToast('Document saved', 'success');
                    break;
                case 'o':
                    e.preventDefault();
                    openDocumentModal();
                    break;
                case 'n':
                    e.preventDefault();
                    createNewDocument();
                    break;
            }
        }
    });
}

// Utility functions
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Initialize toolbar state on selection change
document.addEventListener('selectionchange', function() {
    if (document.activeElement.id === 'editor') {
        updateToolbarState();
    }
});

// Prevent default drag and drop behavior on editor
document.getElementById('editor').addEventListener('dragover', function(e) {
    e.preventDefault();
});

document.getElementById('editor').addEventListener('drop', function(e) {
    e.preventDefault();
});

// Handle window before unload to prevent accidental data loss
window.addEventListener('beforeunload', function(e) {
    const content = document.getElementById('editor').innerHTML;
    if (content.trim() !== '') {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Enhanced Features Implementation

// Table insertion functionality
function insertTable() {
    const rows = prompt('Enter number of rows:', '3');
    const cols = prompt('Enter number of columns:', '3');

    if (rows && cols && !isNaN(rows) && !isNaN(cols)) {
        const table = createTableHTML(parseInt(rows), parseInt(cols));
        document.execCommand('insertHTML', false, table);
        saveState();
        showToast('Table inserted', 'success');
    }
}

function createTableHTML(rows, cols) {
    let table = '<table contenteditable="true"><tbody>';

    for (let i = 0; i < rows; i++) {
        table += '<tr>';
        for (let j = 0; j < cols; j++) {
            table += '<td contenteditable="true">Cell ' + (i + 1) + '-' + (j + 1) + '</td>';
        }
        table += '</tr>';
    }

    table += '</tbody></table>';
    return table;
}

// Image insertion functionality
function insertImage() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const img = '<img src="' + event.target.result + '" alt="Inserted image" contenteditable="false">';
                document.execCommand('insertHTML', false, img);
                saveState();
                showToast('Image inserted', 'success');
            };
            reader.readAsDataURL(file);
        }
    };
    input.click();
}

// Link insertion functionality
function insertLink() {
    const url = prompt('Enter URL:', 'https://');
    const text = prompt('Enter link text:', 'Click here');

    if (url && text) {
        const link = '<a href="' + escapeHtml(url) + '" target="_blank">' + escapeHtml(text) + '</a>';
        document.execCommand('insertHTML', false, link);
        saveState();
        showToast('Link inserted', 'success');
    }
}

// Dark mode functionality
function toggleDarkMode() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');

    body.classList.toggle('dark-mode');

    if (body.classList.contains('dark-mode')) {
        themeIcon.className = 'fas fa-sun';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        themeIcon.className = 'fas fa-moon';
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Load dark mode preference
function loadDarkModePreference() {
    const darkMode = localStorage.getItem('darkMode');
    const themeIcon = document.getElementById('themeIcon');

    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
        themeIcon.className = 'fas fa-sun';
    }
}

// Find and Replace functionality
let findCurrentIndex = -1;
let findMatches = [];

function openFindReplaceModal() {
    document.getElementById('findReplaceModal').classList.add('active');
    document.getElementById('findInput').focus();
}

function closeFindReplaceModal() {
    document.getElementById('findReplaceModal').classList.remove('active');
    findCurrentIndex = -1;
    findMatches = [];
    clearHighlights();
}

function findNext() {
    const findText = document.getElementById('findInput').value;
    const matchCase = document.getElementById('matchCase').checked;
    const matchWholeWord = document.getElementById('matchWholeWord').checked;

    if (!findText) {
        showToast('Please enter text to find', 'warning');
        return;
    }

    const editor = document.getElementById('editor');
    const content = editor.textContent || editor.innerText || '';
    let searchContent = matchCase ? content : content.toLowerCase();
    let searchText = matchCase ? findText : findText.toLowerCase();

    // Clear previous highlights
    clearHighlights();

    // Find all matches
    findMatches = [];
    let regex;

    if (matchWholeWord) {
        regex = new RegExp('\\b' + escapeRegExp(searchText) + '\\b', matchCase ? 'g' : 'gi');
    } else {
        regex = new RegExp(escapeRegExp(searchText), matchCase ? 'g' : 'gi');
    }

    let match;
    while ((match = regex.exec(searchContent)) !== null) {
        findMatches.push({
            start: match.index,
            end: match.index + match[0].length,
            text: match[0]
        });
    }

    if (findMatches.length === 0) {
        document.getElementById('findResults').textContent = 'No matches found';
        return;
    }

    // Move to next match
    findCurrentIndex = (findCurrentIndex + 1) % findMatches.length;
    highlightMatch(findCurrentIndex);

    const resultText = `Match ${findCurrentIndex + 1} of ${findMatches.length} found`;
    document.getElementById('findResults').textContent = resultText;
}

function replaceAll() {
    const findText = document.getElementById('findInput').value;
    const replaceText = document.getElementById('replaceInput').value;
    const matchCase = document.getElementById('matchCase').checked;
    const matchWholeWord = document.getElementById('matchWholeWord').checked;

    if (!findText) {
        showToast('Please enter text to find', 'warning');
        return;
    }

    const editor = document.getElementById('editor');
    const content = editor.innerHTML;

    let regex;
    if (matchWholeWord) {
        regex = new RegExp('\\b' + escapeRegExp(findText) + '\\b', matchCase ? 'g' : 'gi');
    } else {
        regex = new RegExp(escapeRegExp(findText), matchCase ? 'g' : 'gi');
    }

    const newContent = content.replace(regex, escapeHtml(replaceText));
    editor.innerHTML = newContent;

    clearHighlights();
    saveState();

    const matches = (newContent.match(regex) || []).length;
    showToast(`Replaced ${matches} occurrences`, 'success');

    document.getElementById('findResults').textContent = `Replaced ${matches} occurrences`;
}

function highlightMatch(index) {
    const match = findMatches[index];
    if (!match) return;

    const editor = document.getElementById('editor');
    const text = editor.textContent || editor.innerText || '';

    // Create a temporary span to highlight the match
    const beforeText = text.substring(0, match.start);
    const matchText = text.substring(match.start, match.end);
    const afterText = text.substring(match.end);

    // For simplicity, we'll just scroll to the approximate position
    // In a more complex implementation, you'd use ranges and selections
    editor.focus();

    // Show match information
    showToast(`Found: "${match.text}"`, 'info');
}

function clearHighlights() {
    // This would normally remove highlight spans
    // For simplicity, we're just tracking matches
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Templates functionality
function openTemplatesModal() {
    document.getElementById('templatesModal').classList.add('active');
}

function closeTemplatesModal() {
    document.getElementById('templatesModal').classList.remove('active');
}

function loadTemplate(templateType) {
    let content = '';

    switch (templateType) {
        case 'blank':
            content = '';
            break;
        case 'letter':
            content = `
                <h1>Business Letter</h1>
                <p><strong>Your Name</strong><br>
                Your Address<br>
                Your City, State, ZIP Code<br>
                Your Email<br>
                Your Phone Number<br>
                Date</p>

                <p><strong>Recipient Name</strong><br>
                Recipient Title<br>
                Recipient Company<br>
                Recipient Address<br>
                Recipient City, State, ZIP Code</p>

                <p>Dear [Recipient Name],</p>

                <p>I am writing to [state the purpose of your letter]. [Provide relevant details and background information].</p>

                <p>[Include additional paragraphs as needed to explain your situation, provide evidence, or make your case].</p>

                <p>[Conclude with a call to action or next steps]. Thank you for your time and consideration.</p>

                <p>Sincerely,<br>
                [Your Name]<br>
                [Your Title, if applicable]</p>
            `;
            break;
        case 'memo':
            content = `
                <h1>MEMORANDUM</h1>
                <p><strong>TO:</strong> [Recipient Names]</p>
                <p><strong>FROM:</strong> [Your Name]</p>
                <p><strong>DATE:</strong> ${new Date().toLocaleDateString()}</p>
                <p><strong>SUBJECT:</strong> [Memo Subject]</p>

                <h2>Purpose</h2>
                <p>[State the purpose of the memo in one or two sentences]</p>

                <h2>Background</h2>
                <p>[Provide necessary context and background information]</p>

                <h2>Key Points</h2>
                <ul>
                    <li>[Main point 1]</li>
                    <li>[Main point 2]</li>
                    <li>[Main point 3]</li>
                </ul>

                <h2>Action Required</h2>
                <p>[Specify what actions need to be taken and by whom]</p>

                <h2>Timeline</h2>
                <p>[Include relevant deadlines and milestones]</p>
            `;
            break;
        case 'report':
            content = `
                <h1>Business Report</h1>
                <p><strong>Report Title:</strong> [Report Title]<br>
                <strong>Date:</strong> ${new Date().toLocaleDateString()}<br>
                <strong>Author:</strong> [Your Name]<br>
                <strong>Department:</strong> [Your Department]</p>

                <h2>Executive Summary</h2>
                <p>[Provide a brief overview of the report's key findings and recommendations]</p>

                <h2>Introduction</h2>
                <p>[Describe the purpose and scope of the report]</p>

                <h2>Methodology</h2>
                <p>[Explain how the information was gathered and analyzed]</p>

                <h2>Findings</h2>
                <h3>Key Finding 1</h3>
                <p>[Describe the first major finding]</p>

                <h3>Key Finding 2</h3>
                <p>[Describe the second major finding]</p>

                <h2>Analysis</h2>
                <p>[Analyze the findings and their implications]</p>

                <h2>Recommendations</h2>
                <ol>
                    <li>[Recommendation 1]</li>
                    <li>[Recommendation 2]</li>
                    <li>[Recommendation 3]</li>
                </ol>

                <h2>Conclusion</h2>
                <p>[Summarize the key points and next steps]</p>
            `;
            break;
        case 'essay':
            content = `
                <h1>Essay Title</h1>
                <p><strong>Student Name:</strong> [Your Name]<br>
                <strong>Course:</strong> [Course Name]<br>
                <strong>Instructor:</strong> [Instructor Name]<br>
                <strong>Date:</strong> ${new Date().toLocaleDateString()}</p>

                <h2>Introduction</h2>
                <p>[Start with a hook to grab the reader's attention. Provide background information on your topic and end with a clear thesis statement that outlines the main points of your essay.]</p>

                <h2>Body Paragraph 1</h2>
                <p>[Begin with a topic sentence that supports your thesis. Provide evidence, examples, and analysis to support your point. Use transitions to connect ideas.]</p>

                <h2>Body Paragraph 2</h2>
                <p>[Continue with your second main point. Include specific examples and detailed explanations. Make sure to connect back to your thesis statement.]</p>

                <h2>Body Paragraph 3</h2>
                <p>[Present your third main point with supporting evidence. Address potential counterarguments if relevant.]</p>

                <h2>Counterargument and Rebuttal (Optional)</h2>
                <p>[Acknowledge opposing viewpoints and explain why your position is stronger.]</p>

                <h2>Conclusion</h2>
                <p>[Restate your thesis in different words. Summarize your main points. End with a final thought that leaves a lasting impression on the reader.]</p>

                <h2>Works Cited</h2>
                <p>[List your sources in the appropriate citation format]</p>
            `;
            break;
        case 'meeting':
            content = `
                <h1>Meeting Minutes</h1>
                <p><strong>Meeting Title:</strong> [Meeting Title]<br>
                <strong>Date:</strong> ${new Date().toLocaleDateString()}<br>
                <strong>Time:</strong> [Start Time] - [End Time]<br>
                <strong>Location:</strong> [Meeting Location]<br>
                <strong>Called by:</strong> [Meeting Organizer]</p>

                <h2>Attendees</h2>
                <p><strong>Present:</strong> [List of attendees]<br>
                <strong>Absent:</strong> [List of absent members]</p>

                <h2>Agenda</h2>
                <ol>
                    <li>[Agenda Item 1]</li>
                    <li>[Agenda Item 2]</li>
                    <li>[Agenda Item 3]</li>
                </ol>

                <h2>Discussion Summary</h2>
                <h3>Agenda Item 1: [Topic]</h3>
                <p><strong>Key Points:</strong></p>
                <ul>
                    <li>[Discussion point 1]</li>
                    <li>[Discussion point 2]</li>
                </ul>
                <p><strong>Decisions:</strong> [Any decisions made]</p>

                <h3>Agenda Item 2: [Topic]</h3>
                <p><strong>Key Points:</strong></p>
                <ul>
                    <li>[Discussion point 1]</li>
                    <li>[Discussion point 2]</li>
                </ul>
                <p><strong>Decisions:</strong> [Any decisions made]</p>

                <h2>Action Items</h2>
                <table>
                    <tr>
                        <th>Action Item</th>
                        <th>Assigned To</th>
                        <th>Deadline</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>[Action item 1]</td>
                        <td>[Person responsible]</td>
                        <td>[Due date]</td>
                        <td>Pending</td>
                    </tr>
                    <tr>
                        <td>[Action item 2]</td>
                        <td>[Person responsible]</td>
                        <td>[Due date]</td>
                        <td>Pending</td>
                    </tr>
                </table>

                <h2>Next Meeting</h2>
                <p><strong>Date:</strong> [Next meeting date]<br>
                <strong>Time:</strong> [Next meeting time]<br>
                <strong>Location:</strong> [Next meeting location]</p>

                <p><strong>Minutes submitted by:</strong> [Your Name]</p>
            `;
            break;
    }

    document.getElementById('editor').innerHTML = content;
    document.getElementById('documentTitle').value = templateType.charAt(0).toUpperCase() + templateType.slice(1) + ' Document';

    closeTemplatesModal();
    saveState();
    updateWordCount();
    showToast('Template loaded', 'success');
}

// Help modal functionality
function showHelp() {
    document.getElementById('helpModal').classList.add('active');
}

function closeHelpModal() {
    document.getElementById('helpModal').classList.remove('active');
}

// Enhanced export functionality
function exportAsMarkdown() {
    const title = document.getElementById('documentTitle').value || 'Untitled Document';
    const content = document.getElementById('editor').innerHTML;

    const markdown = convertHTMLToMarkdown(content, title);
    downloadFile(markdown, title + '.md', 'text/markdown');
    closeExportModal();
    showToast('Document exported as Markdown', 'success');
}

function convertHTMLToMarkdown(html, title) {
    let markdown = '# ' + title + '\n\n';

    // Convert HTML to markdown (simplified version)
    const temp = document.createElement('div');
    temp.innerHTML = html;

    function processNode(node) {
        let result = '';

        switch (node.nodeType) {
            case Node.TEXT_NODE:
                result = node.textContent;
                break;
            case Node.ELEMENT_NODE:
                switch (node.tagName.toLowerCase()) {
                    case 'h1':
                        result = '# ' + node.textContent + '\n\n';
                        break;
                    case 'h2':
                        result = '## ' + node.textContent + '\n\n';
                        break;
                    case 'h3':
                        result = '### ' + node.textContent + '\n\n';
                        break;
                    case 'h4':
                        result = '#### ' + node.textContent + '\n\n';
                        break;
                    case 'h5':
                        result = '##### ' + node.textContent + '\n\n';
                        break;
                    case 'h6':
                        result = '###### ' + node.textContent + '\n\n';
                        break;
                    case 'p':
                        result = node.textContent + '\n\n';
                        break;
                    case 'strong':
                    case 'b':
                        result = '**' + node.textContent + '**';
                        break;
                    case 'em':
                    case 'i':
                        result = '*' + node.textContent + '*';
                        break;
                    case 'u':
                        result = '__' + node.textContent + '__';
                        break;
                    case 'code':
                        result = '`' + node.textContent + '`';
                        break;
                    case 'pre':
                        result = '```\n' + node.textContent + '\n```\n\n';
                        break;
                    case 'blockquote':
                        result = '> ' + node.textContent + '\n\n';
                        break;
                    case 'ul':
                        result = '\n';
                        for (let li of node.children) {
                            result += '- ' + li.textContent + '\n';
                        }
                        result += '\n';
                        break;
                    case 'ol':
                        result = '\n';
                        for (let i = 0; i < node.children.length; i++) {
                            result += (i + 1) + '. ' + node.children[i].textContent + '\n';
                        }
                        result += '\n';
                        break;
                    case 'a':
                        result = '[' + node.textContent + '](' + node.href + ')';
                        break;
                    case 'img':
                        result = '![' + (node.alt || '') + '](' + node.src + ')';
                        break;
                    case 'br':
                        result = '\n';
                        break;
                    default:
                        for (let child of node.childNodes) {
                            result += processNode(child);
                        }
                }
                break;
        }

        return result;
    }

    markdown += processNode(temp);
    return markdown;
}

function exportAsPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const title = document.getElementById('documentTitle').value || 'Untitled Document';
    const content = document.getElementById('editor').innerText || '';

    // Add title
    doc.setFontSize(20);
    doc.text(title, 20, 30);

    // Add content
    doc.setFontSize(12);
    const splitContent = doc.splitTextToSize(content, 170);
    doc.text(splitContent, 20, 50);

    // Save the PDF
    doc.save(title + '.pdf');
    closeExportModal();
    showToast('Document exported as PDF', 'success');
}

// Enhanced document statistics
function updateWordCount() {
    const editor = document.getElementById('editor');
    const text = editor.innerText || editor.textContent || '';

    // Word count
    const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;

    // Character count
    const characters = text.length;
    const charactersNoSpaces = text.replace(/\s/g, '').length;

    // Paragraph count
    const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;

    // Reading time (average 200 words per minute)
    const readingTime = Math.ceil(words / 200);

    // Update UI
    document.getElementById('wordCount').textContent = words;
    document.getElementById('charCount').textContent = charactersNoSpaces;
    document.getElementById('readingTime').textContent = readingTime;
}

// Enhanced keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only apply shortcuts when not in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'b':
                    e.preventDefault();
                    formatText('bold');
                    break;
                case 'i':
                    e.preventDefault();
                    formatText('italic');
                    break;
                case 'u':
                    e.preventDefault();
                    formatText('underline');
                    break;
                case 's':
                    e.preventDefault();
                    saveCurrentDocument();
                    showToast('Document saved', 'success');
                    break;
                case 'o':
                    e.preventDefault();
                    openDocumentModal();
                    break;
                case 'n':
                    e.preventDefault();
                    createNewDocument();
                    break;
                case 'f':
                    e.preventDefault();
                    openFindReplaceModal();
                    break;
                case 'h':
                    e.preventDefault();
                    showHelp();
                    break;
                case 'p':
                    e.preventDefault();
                    window.print();
                    break;
            }
        }
    });
}

// Initialize dark mode preference
document.addEventListener('DOMContentLoaded', function() {
    loadDarkModePreference();
});