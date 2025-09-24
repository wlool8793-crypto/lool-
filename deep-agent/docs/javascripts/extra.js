// Custom JavaScript for Deep Agent documentation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme toggle
    initializeThemeToggle();

    // Initialize mobile navigation
    initializeMobileNav();

    // Initialize search functionality
    initializeSearch();

    // Initialize smooth scrolling
    initializeSmoothScrolling();

    // Initialize code highlighting
    initializeCodeHighlighting();

    // Initialize table of contents
    initializeTableOfContents();

    // Initialize analytics
    initializeAnalytics();

    // Initialize dark mode detection
    initializeDarkMode();
});

// Theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.querySelector('[data-md-toggle="search"]');
    const body = document.body;

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.setAttribute('data-md-color-scheme', savedTheme);
    }

    // Listen for theme changes
    themeToggle.addEventListener('change', function() {
        const newTheme = body.getAttribute('data-md-color-scheme') === 'slate' ? 'default' : 'slate';
        body.setAttribute('data-md-color-scheme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// Mobile navigation functionality
function initializeMobileNav() {
    const navToggle = document.querySelector('.md-nav__toggle');
    const navList = document.querySelector('.md-nav__list');

    if (navToggle && navList) {
        navToggle.addEventListener('click', function() {
            navList.classList.toggle('md-nav__list--hidden');
        });
    }
}

// Search functionality enhancements
function initializeSearch() {
    const searchInput = document.querySelector('.md-search__input');
    const searchResults = document.querySelector('.md-search__results');

    if (searchInput) {
        // Add debounced search
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Search functionality will be handled by MkDocs
                console.log('Searching for:', searchInput.value);
            }, 300);
        });

        // Add keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchInput.blur();
            }
        });
    }
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = link.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update URL without reload
                history.pushState(null, null, targetId);
            }
        });
    });
}

// Enhanced code highlighting
function initializeCodeHighlighting() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach(block => {
        // Add line numbers
        const lines = block.textContent.split('\n');
        const numberedLines = lines.map((line, index) => {
            return `<span class="code-line" data-line="${index + 1}">${line}</span>`;
        }).join('\n');

        block.innerHTML = numberedLines;

        // Add copy button
        const pre = block.parentElement;
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '📋 Copy';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '10px';
        copyButton.style.right = '10px';
        copyButton.style.padding = '5px 10px';
        copyButton.style.backgroundColor = '#007acc';
        copyButton.style.color = 'white';
        copyButton.style.border = 'none';
        copyButton.style.borderRadius = '4px';
        copyButton.style.cursor = 'pointer';
        copyButton.style.fontSize = '12px';

        pre.style.position = 'relative';
        pre.appendChild(copyButton);

        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(block.textContent).then(() => {
                copyButton.innerHTML = '✅ Copied!';
                setTimeout(() => {
                    copyButton.innerHTML = '📋 Copy';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text:', err);
            });
        });
    });
}

// Table of contents functionality
function initializeTableOfContents() {
    const toc = document.querySelector('.md-toc');
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');

    if (toc && headings.length > 0) {
        // Create a simple TOC if none exists
        if (toc.children.length === 0) {
            const tocList = document.createElement('ul');
            tocList.className = 'md-toc__list';

            headings.forEach(heading => {
                if (heading.id) {
                    const tocItem = document.createElement('li');
                    tocItem.className = 'md-toc__item';

                    const tocLink = document.createElement('a');
                    tocLink.className = 'md-toc__link';
                    tocLink.href = `#${heading.id}`;
                    tocLink.textContent = heading.textContent;

                    tocItem.appendChild(tocLink);
                    tocList.appendChild(tocItem);
                }
            });

            toc.appendChild(tocList);
        }

        // Highlight current section
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    const tocLink = toc.querySelector(`a[href="#${id}"]`);
                    if (tocLink) {
                        // Remove active class from all links
                        toc.querySelectorAll('.md-toc__link').forEach(link => {
                            link.classList.remove('md-toc__link--active');
                        });
                        // Add active class to current link
                        tocLink.classList.add('md-toc__link--active');
                    }
                }
            });
        }, { threshold: 0.1 });

        headings.forEach(heading => {
            observer.observe(heading);
        });
    }
}

// Analytics tracking
function initializeAnalytics() {
    // Track page views
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_MEASUREMENT_ID', {
            'page_path': window.location.pathname
        });
    }

    // Track outbound links
    const outboundLinks = document.querySelectorAll('a[href^="http"]');
    outboundLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'click', {
                    'event_category': 'outbound',
                    'event_label': link.href
                });
            }
        });
    });

    // Track search queries
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'search', {
                        'event_category': 'search',
                        'event_label': searchInput.value
                    });
                }
            }
        });
    }
}

// Dark mode detection
function initializeDarkMode() {
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const body = document.body;

    // Set initial theme based on system preference
    if (!localStorage.getItem('theme')) {
        if (prefersDarkScheme.matches) {
            body.setAttribute('data-md-color-scheme', 'slate');
        }
    }

    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'slate' : 'default';
            body.setAttribute('data-md-color-scheme', newTheme);
        }
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Print functionality
function initializePrintFunctionality() {
    const printButton = document.createElement('button');
    printButton.textContent = '🖨️ Print';
    printButton.className = 'print-button';
    printButton.style.position = 'fixed';
    printButton.style.bottom = '20px';
    printButton.style.right = '20px';
    printButton.style.padding = '10px 15px';
    printButton.style.backgroundColor = '#007acc';
    printButton.style.color = 'white';
    printButton.style.border = 'none';
    printButton.style.borderRadius = '4px';
    printButton.style.cursor = 'pointer';
    printButton.style.zIndex = '1000';

    document.body.appendChild(printButton);

    printButton.addEventListener('click', function() {
        window.print();
    });
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Ctrl/Cmd + / for TOC toggle
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const tocToggle = document.querySelector('.md-nav__toggle');
            if (tocToggle) {
                tocToggle.click();
            }
        }

        // Escape to close search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput === document.activeElement) {
                searchInput.blur();
            }
        }
    });
}

// Initialize additional features when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePrintFunctionality();
    initializeKeyboardShortcuts();

    // Add loading animation
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });

    // Add smooth reveal animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.feature-card, .hero-section, .md-content h1, .md-content h2');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
});

// Export functions for external use
window.DeepAgentDocs = {
    initializeThemeToggle,
    initializeSearch,
    initializeSmoothScrolling,
    debounce,
    throttle
};