(function () {
  if (typeof window === 'undefined') return;

  var reloadKey = 'doisense_chunk_recovery_once';
  var recoveredKey = 'doisense_chunk_recovery_ok';

  function toLanguage(pathname) {
    var match = String(pathname || '').match(/^\/doisense\/(ro|en|de|fr|it|es|pl)(\/|$)/i);
    return match ? match[1].toLowerCase() : 'en';
  }

  function trackRecoveryEvent(eventName, properties) {
    try {
      var payload = JSON.stringify({
        event_name: eventName,
        source: 'frontend',
        properties: properties || {},
      });
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon('/doisense/api/analytics/track', blob);
        return;
      }
      fetch('/doisense/api/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
      });
    } catch (_) {
      // best effort telemetry
    }
  }

  function shouldRecover(message, target) {
    var msg = String(message || '');
    var scriptError = target && target.tagName === 'SCRIPT' && /\/_nuxt\//.test(target.src || '');

    return scriptError
      || /Failed to fetch dynamically imported module/i.test(msg)
      || /Importing a module script failed/i.test(msg)
      || /Loading chunk [^ ]+ failed/i.test(msg);
  }

  function hardRedirect() {
    var lang = toLanguage(window.location.pathname);
    var next = encodeURIComponent(window.location.pathname + window.location.search + window.location.hash);
    window.location.assign('/doisense/' + lang + '/auth/login?reason=client_recovery&next=' + next);
  }

  function recoverOnce(reason) {
    if (sessionStorage.getItem(reloadKey)) {
      trackRecoveryEvent('frontend_chunk_recovery_failed', {
        reason: reason || 'unknown',
        path: window.location.pathname,
      });
      hardRedirect();
      return;
    }

    sessionStorage.setItem(reloadKey, '1');

    trackRecoveryEvent('frontend_chunk_recovery_triggered', {
      reason: reason || 'unknown',
      path: window.location.pathname,
    });

    try {
      if ('caches' in window) {
        caches.keys()
          .then(function (keys) {
            return Promise.all(keys.map(function (name) {
              return caches.delete(name);
            }));
          })
          .finally(function () {
            window.location.reload();
          });
        return;
      }
    } catch (_) {
      // fallback below
    }

    window.location.reload();
  }

  window.addEventListener('error', function (event) {
    if (shouldRecover(event && event.message, event && event.target)) {
      recoverOnce((event && event.message) || 'window_error');
    }
  }, true);

  window.addEventListener('unhandledrejection', function (event) {
    var reason = event && event.reason;
    var msg = (reason && (reason.message || (reason.toString && reason.toString()))) || '';
    if (shouldRecover(msg, null)) {
      recoverOnce(msg || 'unhandled_rejection');
    }
  });

  if (!sessionStorage.getItem(recoveredKey)) {
    sessionStorage.setItem(recoveredKey, '1');
    sessionStorage.removeItem(reloadKey);
  }
})();
