(function() {
    const siteUrl = 'https://docker-app-9a76b3f1350c.herokuapp.com/';
    const src = `${siteUrl}static/js/bookmarklet.js?r=${Math.random() * 999999999}`;
    
    // Set the site URL for the bookmarklet script to use
    window.bookmarkletSiteUrl = siteUrl;

    function loadScriptAndLaunch() {
        const s = document.createElement('script');
        s.src = src;
        s.async = true;
        s.onload = function() {
            if (typeof bookmarkletLaunch === 'function') {
                bookmarkletLaunch();
                window.bookmarkletLoaded = true;
            } else {
                console.error('bookmarklet script loaded but bookmarkletLaunch is undefined');
            }
        };
        s.onerror = function() {
            console.error('Failed to load bookmarklet script:', src);
            // Reset flag so user can try again
            window.bookmarkletLoaded = false;
        };
        document.body.appendChild(s);
    }

    if (!window.bookmarkletLoaded) {
        // Not yet loaded — load script and call launch when it's ready
        loadScriptAndLaunch();
    } else if (typeof bookmarkletLaunch === 'function') {
        // Already loaded and available — call directly
        bookmarkletLaunch();
    } else {
        // Flag indicates script was attempted before, but function not available.
        // Try loading it again (covers script load failure / stale state).
        loadScriptAndLaunch();
    }
})();