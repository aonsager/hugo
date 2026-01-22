(function() {
  let searchIndex = null;
  let fuse = null;
  let selectedIndex = -1;

  const fuseOptions = {
    keys: [
      { name: 'title', weight: 0.6 },
      { name: 'content', weight: 0.4 }
    ],
    includeMatches: true,
    threshold: 0.3,
    ignoreLocation: true,
    minMatchCharLength: 3
  };

  // Debounce helper
  function debounce(fn, delay) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // Load search index lazily
  async function loadSearchIndex() {
    if (searchIndex) return searchIndex;

    const response = await fetch('/search-index.json');
    searchIndex = await response.json();
    fuse = new Fuse(searchIndex, fuseOptions);
    return searchIndex;
  }

  // Get modal elements
  function getElements() {
    return {
      modal: document.getElementById('search-modal'),
      backdrop: document.getElementById('search-backdrop'),
      input: document.getElementById('search-input'),
      results: document.getElementById('search-results')
    };
  }

  // Open modal
  async function openSearch() {
    const { modal, input } = getElements();
    modal.classList.add('open');
    // document.body.style.overflow = 'hidden';
    input.focus();
    await loadSearchIndex();
  }

  // Close modal
  function closeSearch() {
    const { modal, input, results } = getElements();
    modal.classList.remove('open');
    // document.body.style.overflow = '';
    input.value = '';
    results.innerHTML = '';
    selectedIndex = -1;
    document.activeElement.blur();
  }

  // Highlight matches in text
  function highlightMatches(text, indices) {
    if (!indices || indices.length === 0) return escapeHtml(text);

    let result = '';
    let lastIndex = 0;

    // Sort and merge overlapping indices
    const sorted = [...indices].sort((a, b) => a[0] - b[0]);

    for (const [start, end] of sorted) {
      if (start > lastIndex) {
        result += escapeHtml(text.slice(lastIndex, start));
      }
      result += '<mark>' + escapeHtml(text.slice(start, end + 1)) + '</mark>';
      lastIndex = Math.max(lastIndex, end + 1);
    }

    if (lastIndex < text.length) {
      result += escapeHtml(text.slice(lastIndex));
    }

    return result;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Get snippet around match
  function getSnippet(text, indices, maxLength = 150) {
    if (!indices || indices.length === 0) {
      return text.slice(0, maxLength) + (text.length > maxLength ? '...' : '');
    }

    const firstMatch = indices[0][0];
    const start = Math.max(0, firstMatch - 50);
    const end = Math.min(text.length, start + maxLength);

    let snippet = text.slice(start, end);
    if (start > 0) snippet = '...' + snippet;
    if (end < text.length) snippet += '...';

    // Adjust indices for snippet
    const adjustedIndices = indices
      .filter(([s, e]) => s >= start && e < end)
      .map(([s, e]) => [s - start + (start > 0 ? 3 : 0), e - start + (start > 0 ? 3 : 0)]);

    return highlightMatches(snippet, adjustedIndices);
  }

  // Render search results
  function renderResults(results) {
    const { results: container } = getElements();

    if (results.length === 0) {
      container.innerHTML = '<div class="search-empty">No results found</div>';
      return;
    }

    container.innerHTML = results.slice(0, 10).map((result, index) => {
      const titleMatch = result.matches?.find(m => m.key === 'title');
      const contentMatch = result.matches?.find(m => m.key === 'content');

      const title = titleMatch
        ? highlightMatches(result.item.title, titleMatch.indices)
        : escapeHtml(result.item.title);

      const snippet = contentMatch
        ? getSnippet(result.item.content, contentMatch.indices)
        : escapeHtml(result.item.content.slice(0, 150)) + '...';

      return `
        <a href="${result.item.url}" class="search-result" data-index="${index}">
          <div class="search-result-title">${title}</div>
          <div class="search-result-snippet">${snippet}</div>
        </a>
      `;
    }).join('');

    selectedIndex = -1;
  }

  // Perform search
  const performSearch = debounce(function(query) {
    const { results } = getElements();

    if (!query.trim()) {
      results.innerHTML = '';
      return;
    }

    if (!fuse) {
      results.innerHTML = '<div class="search-empty">Loading...</div>';
      return;
    }

    const searchResults = fuse.search(query);
    renderResults(searchResults);
  }, 150);

  // Keyboard navigation
  function updateSelection(newIndex) {
    const { results } = getElements();
    const items = results.querySelectorAll('.search-result');

    if (items.length === 0) return;

    // Remove current selection
    items.forEach(item => item.classList.remove('selected'));

    // Clamp index
    if (newIndex < 0) newIndex = items.length - 1;
    if (newIndex >= items.length) newIndex = 0;

    selectedIndex = newIndex;
    items[selectedIndex].classList.add('selected');
    items[selectedIndex].scrollIntoView({ block: 'nearest' });
  }

  function handleKeydown(e) {
    const { modal, results } = getElements();

    if (!modal.classList.contains('open')) return;

    switch (e.key) {
      case 'Escape':
        closeSearch();
        e.preventDefault();
        break;
      case 'ArrowDown':
        updateSelection(selectedIndex + 1);
        e.preventDefault();
        break;
      case 'ArrowUp':
        updateSelection(selectedIndex - 1);
        e.preventDefault();
        break;
      case 'Enter':
        const items = results.querySelectorAll('.search-result');
        if (selectedIndex >= 0 && items[selectedIndex]) {
          window.location.href = items[selectedIndex].href;
        }
        e.preventDefault();
        break;
    }
  }

  // Global shortcut ( / )
  function handleGlobalKeydown(e) {
      if (e.key === '/') {
        const activeElement = document.activeElement;
        const isInput = activeElement.tagName === 'INPUT';
        const isTextarea = activeElement.tagName === 'TEXTAREA';
        const isContentEditable = activeElement.isContentEditable; // For rich text editors
        if (isInput || isTextarea || isContentEditable) { return; }
          
        e.preventDefault();
        const { modal } = getElements();
        if (modal.classList.contains('open')) {
            closeSearch();
        } else {
            openSearch();
        }
    }
  }

  // Initialize
  function init() {
    const { modal, backdrop, input } = getElements();

    if (!modal) return;

    // Search toggle button
    const toggleBtnFull = document.getElementById('search-toggle-full');
    if (toggleBtnFull) {
      toggleBtnFull.addEventListener('click', openSearch);
    }
      
    const toggleBtnMobile = document.getElementById('search-toggle-mobile');
    if (toggleBtnMobile) {
      toggleBtnMobile.addEventListener('click', openSearch);
    }

      // Close on backdrop click
    backdrop.addEventListener('click', closeSearch);

    // Input handler
    input.addEventListener('input', (e) => performSearch(e.target.value));

    // Keyboard navigation within modal
    modal.addEventListener('keydown', handleKeydown);

    // Global shortcut
    document.addEventListener('keydown', handleGlobalKeydown);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
