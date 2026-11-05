(function () {
  try {
    var location = window.location;
    var pathname = location.pathname;
    var stripped = pathname === '/plans' || pathname === '/plans/'
      ? ['stay_in_browser']
      : ['mwbv', 'stay_in_browser'];
    var pairs = location.search.slice(1).split('&').filter(function (pair) {
      return pair !== '';
    });
    var kept = pairs.filter(function (pair) {
      return stripped.indexOf(decodeURIComponent(pair.split('=')[0].replace(/\+/g, ' '))) === -1;
    });
    if (kept.length === pairs.length) return;
    var search = kept.length > 0 ? '?' + kept.join('&') : '';
    window.history.replaceState(window.history.state, '', pathname + search + location.hash);
  } catch (error) {}
})();