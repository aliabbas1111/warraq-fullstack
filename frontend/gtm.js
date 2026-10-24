/* Google Tag Manager, set up from a file of the site's own (its pages run no inline script: CSP).
   The container id comes from this tag's data-id; the server writes the tag after /ga.js (pages.analytics_head),
   so the consent defaults set there already apply to every tag the container fires. A local copy loads nothing. */
(() => {
    'use strict';
    const me = document.currentScript;
    const id = me && me.dataset.id;
    if (!id || /^(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])$/.test(location.hostname)) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(id);
    if (me.nonce) s.nonce = me.nonce; // pages that run scripts by nonce let the container's loader run too
    document.head.appendChild(s);
})();
