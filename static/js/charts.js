/* Small helpers for loading Plotly figures from the JSON API with
   loading, empty and error states. */
(function () {
  const PLOT_CONFIG = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };

  function setState(el, kind, message) {
    let state = el.querySelector('.chart-state');
    if (!state) {
      state = document.createElement('div');
      state.className = 'chart-state';
      el.appendChild(state);
    }
    const icons = {
      loading: '<div class="spinner-border spinner-border-sm text-primary" role="status"></div>',
      empty: '<i class="bi bi-bar-chart fs-3" aria-hidden="true"></i>',
      error: '<i class="bi bi-exclamation-triangle fs-3 text-danger" aria-hidden="true"></i>',
    };
    state.innerHTML = icons[kind] + '<span></span>';
    state.querySelector('span').textContent = message;
    state.hidden = false;
  }

  function hasData(figure) {
    return (figure.data || []).some(t => (t.x && t.x.length) || (t.values && t.values.length) || (t.z && t.z.length));
  }

  async function loadFigure(el, url, pick) {
    setState(el, 'loading', 'Loading chart…');
    try {
      const response = await fetch(url, { headers: { Accept: 'application/json' }, credentials: 'same-origin' });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
      const figure = pick ? body[pick] : body;
      if (!figure || !hasData(figure)) {
        Plotly.purge(el);
        setState(el, 'empty', 'No data for the current filters.');
        return;
      }
      el.querySelector('.chart-state').hidden = true;
      await Plotly.react(el, figure.data, figure.layout, PLOT_CONFIG);
    } catch (err) {
      Plotly.purge(el);
      setState(el, 'error', 'Could not load chart: ' + err.message);
    }
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  window.TourismCharts = { loadFigure, csrfToken };
})();
