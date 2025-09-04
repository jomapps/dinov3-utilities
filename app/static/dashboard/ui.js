(() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  const state = {
    schema: null,
    endpoints: [],
    selected: null,
    baseUrl: ''
  };

  function computeBaseUrl() {
    const input = $('#baseUrl');
    if (input && input.value.trim()) return input.value.trim();

    // Auto-detect based on current location
    const { protocol, host } = window.location;
    const currentUrl = `${protocol}//${host}`;

    // If we're on the production domain, use it
    if (host.includes('dino.ft.tc')) {
      return 'https://dino.ft.tc';
    }

    // Otherwise use current location
    return currentUrl;
  }

  function setHealth(status) {
    const el = $('#healthStatus');
    el.classList.remove('ok', 'bad', 'unknown');
    if (status === 'ok') el.classList.add('ok');
    else if (status === 'bad') el.classList.add('bad');
    else el.classList.add('unknown');
    el.textContent = status === 'ok' ? 'Healthy' : status === 'bad' ? 'Unhealthy' : 'Unknown';
  }

  async function checkHealth() {
    setHealth('unknown');
    try {
      const res = await fetch(`${state.baseUrl}/api/v1/health`);
      setHealth(res.ok ? 'ok' : 'bad');
    } catch (_e) {
      setHealth('bad');
    }
  }

  async function loadSchema() {
    try {
      const url = `${state.baseUrl}/openapi.json`;
      console.log('Loading schema from:', url);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Failed to load OpenAPI schema: ${res.status}`);
      const json = await res.json();
      console.log('Schema loaded successfully:', json);
      state.schema = json;
      state.endpoints = extractEndpoints(json);
      console.log('Extracted endpoints:', state.endpoints.length);
      renderSidebar();
    } catch (error) {
      console.error('Error loading schema:', error);
      // Show error in the sidebar
      const nav = $('#nav');
      nav.innerHTML = `<div class="group"><div class="group-title">Error</div><div style="color: var(--bad); padding: 8px;">Failed to load API schema: ${error.message}</div></div>`;
    }
  }

  function extractEndpoints(schema) {
    const paths = schema.paths || {};
    const result = [];
    for (const [path, methods] of Object.entries(paths)) {
      for (const [method, spec] of Object.entries(methods)) {
        const tags = spec.tags || ['General'];
        result.push({
          id: `${method.toUpperCase()} ${path}`,
          method: method.toUpperCase(),
          path,
          tags,
          summary: spec.summary || spec.operationId || '',
          description: spec.description || '',
          parameters: spec.parameters || [],
          requestBody: spec.requestBody || null,
          responses: spec.responses || {}
        });
      }
    }
    return result.sort((a, b) => a.path.localeCompare(b.path));
  }

  function groupByTag(endpoints) {
    const map = new Map();
    for (const ep of endpoints) {
      for (const tag of ep.tags) {
        if (!map.has(tag)) map.set(tag, []);
        map.get(tag).push(ep);
      }
    }
    for (const arr of map.values()) arr.sort((a, b) => a.path.localeCompare(b.path));
    return map;
  }

  function renderSidebar() {
    const nav = $('#nav');
    nav.innerHTML = '';
    const q = ($('#search').value || '').toLowerCase();
    const filtered = state.endpoints.filter(e =>
      e.path.toLowerCase().includes(q) || e.method.toLowerCase().includes(q) || (e.summary || '').toLowerCase().includes(q)
    );
    const grouped = groupByTag(filtered);
    for (const [tag, eps] of grouped.entries()) {
      const group = document.createElement('div');
      group.className = 'group';
      const title = document.createElement('div');
      title.className = 'group-title';
      title.textContent = tag;
      group.appendChild(title);
      for (const ep of eps) {
        const btn = document.createElement('button');
        btn.className = 'endpoint';
        btn.textContent = `${ep.method} ${ep.path}`;
        btn.addEventListener('click', () => selectEndpoint(ep));
        group.appendChild(btn);
      }
      nav.appendChild(group);
    }
  }

  function selectEndpoint(ep) {
    state.selected = ep;
    renderEndpointInfo(ep);
    renderRequestForm(ep);
    $('#responseSection').classList.add('hidden');
  }

  function renderEndpointInfo(ep) {
    const c = $('#endpointInfo');
    c.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'section';
    const row = document.createElement('div');
    row.className = 'row';
    const method = document.createElement('span');
    method.className = 'badge method-badge';
    method.textContent = ep.method;
    const path = document.createElement('span');
    path.className = 'badge';
    path.textContent = ep.path;
    row.append(method, path);
    const desc = document.createElement('div');
    desc.className = 'help';
    desc.textContent = ep.summary || ep.description || '';
    wrap.append(row, desc);
    c.appendChild(wrap);
  }

  function renderRequestForm(ep) {
    const c = $('#requestSection');
    c.innerHTML = '';

    const section = document.createElement('div');
    section.className = 'section';

    const paramsWrap = document.createElement('div');
    const paramsTitle = document.createElement('h3');
    paramsTitle.textContent = 'Parameters';
    paramsWrap.appendChild(paramsTitle);
    const grid = document.createElement('div');
    grid.className = 'param-grid';

    const pathParams = ep.parameters.filter(p => p.in === 'path');
    const queryParams = ep.parameters.filter(p => p.in === 'query');

    for (const p of [...pathParams, ...queryParams]) {
      const wrap = document.createElement('div');
      wrap.className = 'kv';
      const label = document.createElement('label');
      label.textContent = `${p.name}${p.required ? ' *' : ''}`;
      const input = document.createElement('input');
      input.type = 'text';
      input.name = p.name;
      input.placeholder = (p.schema && p.schema.type) || 'string';
      input.dataset.location = p.in;
      wrap.append(label, input);
      grid.appendChild(wrap);
    }

    paramsWrap.appendChild(grid);
    section.appendChild(paramsWrap);

    const body = buildBodyEditor(ep);
    if (body) section.appendChild(body);

    const actions = document.createElement('div');
    actions.className = 'row';
    const exec = document.createElement('button');
    exec.className = 'btn';
    exec.textContent = 'Execute';
    exec.addEventListener('click', () => execute(ep, section));
    const copy = document.createElement('button');
    copy.className = 'copy';
    copy.textContent = 'Copy cURL';
    copy.addEventListener('click', () => copyCurl(ep, section));
    actions.append(exec, copy);
    section.appendChild(actions);

    c.appendChild(section);
  }

  function buildBodyEditor(ep) {
    const rb = ep.requestBody;
    if (!rb) return null;
    const content = rb.content || {};
    const ct = Object.keys(content)[0];
    if (!ct) return null;

    const wrap = document.createElement('div');
    wrap.className = 'section';
    const title = document.createElement('h3');
    title.textContent = `Request Body (${ct})`;
    wrap.appendChild(title);

    if (ct.includes('multipart/form-data')) {
      // Best effort: detect file-like fields from schema
      const schema = content[ct].schema || {};
      const props = (schema.properties) || {};
      const keys = Object.keys(props);
      if (keys.length === 0) {
        const p = document.createElement('div');
        p.className = 'help';
        p.textContent = 'Add files/fields below. Unknown multipart schema.';
        wrap.appendChild(p);
      }
      for (const k of keys) {
        const prop = props[k] || {};
        const isFile = prop.format === 'binary' || prop.type === 'string' && prop.format === 'binary';
        const row = document.createElement('div');
        row.className = 'kv';
        const label = document.createElement('label');
        label.textContent = k;
        let input;
        if (isFile) {
          input = document.createElement('input');
          input.type = 'file';
          input.className = 'file-input';
        } else {
          input = document.createElement('input');
          input.type = 'text';
        }
        input.name = k;
        row.append(label, input);
        wrap.appendChild(row);
      }
      return wrap;
    }

    // JSON body
    const ta = document.createElement('textarea');
    ta.rows = 12;
    ta.style.width = '100%';
    const example = content[ct].example || content[ct].examples || defaultExampleFromSchema(content[ct].schema);
    if (example) {
      try { ta.value = JSON.stringify(example, null, 2); } catch { /* noop */ }
    }
    ta.dataset.contentType = ct;
    wrap.appendChild(ta);
    return wrap;
  }

  function defaultExampleFromSchema(schema) {
    if (!schema) return undefined;
    try {
      if (schema.example) return schema.example;
      if (schema.type === 'object' && schema.properties) {
        const o = {};
        for (const [k, v] of Object.entries(schema.properties)) {
          if (v && v.type === 'string') o[k] = '';
          else if (v && v.type === 'number') o[k] = 0;
          else if (v && v.type === 'integer') o[k] = 0;
          else if (v && v.type === 'boolean') o[k] = false;
          else o[k] = null;
        }
        return o;
      }
      return undefined;
    } catch { return undefined; }
  }

  function buildUrl(ep, section) {
    let url = `${state.baseUrl}${ep.path}`;
    const inputs = Array.from(section.querySelectorAll('input[type="text"]'));
    // path replace
    for (const input of inputs.filter(i => i.dataset.location === 'path')) {
      url = url.replace(`{${input.name}}`, encodeURIComponent(input.value));
    }
    // query params
    const query = inputs.filter(i => i.dataset.location === 'query' && i.value !== '')
      .map(i => `${encodeURIComponent(i.name)}=${encodeURIComponent(i.value)}`)
      .join('&');
    if (query) url += (url.includes('?') ? '&' : '?') + query;
    return url;
  }

  function collectBody(ep, section) {
    const rb = ep.requestBody;
    if (!rb) return { body: undefined, headers: {} };
    const content = rb.content || {};
    const ct = Object.keys(content)[0];
    if (!ct) return { body: undefined, headers: {} };

    if (ct.includes('multipart/form-data')) {
      const form = new FormData();
      const inputs = section.querySelectorAll('.section input');
      inputs.forEach((inp) => {
        if (!inp.name) return;
        if (inp.type === 'file') {
          if (inp.files && inp.files[0]) form.append(inp.name, inp.files[0]);
        } else {
          if (inp.value !== '') form.append(inp.name, inp.value);
        }
      });
      return { body: form, headers: {} };
    }

    const ta = section.querySelector('textarea');
    let json = undefined;
    try { json = ta && ta.value ? JSON.parse(ta.value) : undefined; } catch (e) {}
    return { body: json ? JSON.stringify(json) : undefined, headers: { 'Content-Type': 'application/json' } };
  }

  async function execute(ep, section) {
    const url = buildUrl(ep, section);
    const { body, headers } = collectBody(ep, section);
    const init = { method: ep.method, headers };
    if (body !== undefined) init.body = body;

    const started = performance.now();
    let ok = false, text = '', status = 0;
    try {
      const res = await fetch(url, init);
      status = res.status; ok = res.ok;
      const ct = res.headers.get('Content-Type') || '';
      if (ct.includes('application/json')) text = JSON.stringify(await res.json(), null, 2);
      else text = await res.text();
    } catch (e) {
      text = String(e);
    }
    const ms = Math.round(performance.now() - started);
    renderResponse(ok, status, ms, text);
  }

  function copyCurl(ep, section) {
    const url = buildUrl(ep, section);
    const { body, headers } = collectBody(ep, section);
    let cmd = `curl -X ${ep.method} `;
    for (const [k, v] of Object.entries(headers)) {
      cmd += `-H "${k}: ${v}" `;
    }
    if (body instanceof FormData) {
      // Not fully serializable; provide hint
      cmd += [...body.entries()].map(([k, v]) => typeof v === 'string' ? `-F "${k}=${v}" ` : `-F "${k}=@<file>" `).join('');
    } else if (typeof body === 'string') {
      cmd += `-d '${body.replace(/'/g, "'\\''")}' `;
    }
    cmd += `'${url}'`;
    navigator.clipboard.writeText(cmd);
  }

  function renderResponse(ok, status, ms, bodyText) {
    const c = $('#responseSection');
    c.classList.remove('hidden');
    c.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'section';
    const row = document.createElement('div');
    row.className = 'row';
    const s = document.createElement('span');
    s.className = 'badge';
    s.textContent = `Status: ${status}`;
    const t = document.createElement('span');
    t.className = 'badge';
    t.textContent = `Time: ${ms} ms`;
    row.append(s, t);
    const pre = document.createElement('pre');
    pre.textContent = bodyText || '';
    wrap.append(row, pre);
    c.appendChild(wrap);
  }

  async function loadConfig() {
    try {
      const res = await fetch(`${state.baseUrl}/api/v1/config`);
      if (res.ok) {
        const config = await res.json();
        console.log('Configuration loaded:', config);

        // Update base URL if site_url is configured
        if (config.site_url && config.site_url !== state.baseUrl) {
          console.log('Updating base URL from config:', config.site_url);
          state.baseUrl = config.site_url;
          $('#baseUrl').value = state.baseUrl;
        }

        return config;
      }
    } catch (error) {
      console.warn('Could not load configuration:', error);
    }
    return null;
  }

  function init() {
    console.log('Initializing dashboard...');
    state.baseUrl = computeBaseUrl();
    console.log('Base URL:', state.baseUrl);
    $('#baseUrl').value = state.baseUrl;
    $('#baseUrl').addEventListener('change', async () => {
      state.baseUrl = computeBaseUrl();
      await checkHealth();
    });
    $('#refreshBtn').addEventListener('click', async () => {
      try {
        $('#refreshBtn').disabled = true;
        await loadSchema();
      } finally {
        $('#refreshBtn').disabled = false;
      }
    });
    $('#search').addEventListener('input', renderSidebar);

    (async () => {
      try {
        console.log('Starting configuration load...');
        await loadConfig();
        console.log('Starting health check and schema load...');
        await checkHealth();
        await loadSchema();
        console.log('Dashboard initialization complete');
      } catch (error) {
        console.error('Dashboard initialization failed:', error);
      }
    })();
  }

  document.addEventListener('DOMContentLoaded', init);
})();


