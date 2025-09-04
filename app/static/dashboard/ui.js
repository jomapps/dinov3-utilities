(() => {
  'use strict';

  // DOM Utilities
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  // Application State
  const state = {
    schema: null,
    endpoints: [],
    selected: null,
    baseUrl: '',
    requestHistory: [],
    favorites: new Set(),
    searchQuery: '',
    uploadedAssets: new Map(), // Store uploaded assets with their IDs
    assetHistory: [] // Track asset uploads for easy access
  };

  // Toast Notification System
  class ToastManager {
    constructor() {
      this.container = $('#toastContainer');
    }

    show(message, type = 'info', title = '') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      
      const icon = this.getIcon(type);
      const closeBtn = document.createElement('button');
      closeBtn.className = 'toast-close';
      closeBtn.innerHTML = '×';
      closeBtn.onclick = () => this.remove(toast);

      toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
          ${title ? `<div class="toast-title">${title}</div>` : ''}
          <div class="toast-message">${message}</div>
        </div>
      `;
      
      toast.appendChild(closeBtn);
      this.container.appendChild(toast);

      // Auto remove after 5 seconds
      setTimeout(() => this.remove(toast), 5000);
    }

    getIcon(type) {
      const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
      };
      return icons[type] || icons.info;
    }

    remove(toast) {
      toast.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }
  }

  const toast = new ToastManager();

  // Loading Overlay Manager
  class LoadingManager {
    constructor() {
      this.overlay = $('#loadingOverlay');
    }

    show(message = 'Loading...') {
      this.overlay.querySelector('p').textContent = message;
      this.overlay.classList.remove('hidden');
    }

    hide() {
      this.overlay.classList.add('hidden');
    }
  }

  const loading = new LoadingManager();

  // Asset Management
  class AssetManager {
    constructor() {
      this.loadAssets();
    }

    addAsset(assetData) {
      const asset = {
        id: assetData.asset_id,
        filename: assetData.filename,
        public_url: assetData.public_url,
        content_type: assetData.content_type,
        file_size: assetData.file_size,
        width: assetData.width,
        height: assetData.height,
        format: assetData.format,
        upload_timestamp: assetData.upload_timestamp,
        processing_status: assetData.processing_status
      };
      
      state.uploadedAssets.set(asset.id, asset);
      state.assetHistory.unshift(asset);
      
      // Keep only last 20 assets
      if (state.assetHistory.length > 20) {
        state.assetHistory = state.assetHistory.slice(0, 20);
      }
      
      this.saveAssets();
      this.updateAssetSelector();
      return asset;
    }

    getAsset(assetId) {
      return state.uploadedAssets.get(assetId);
    }

    getAllAssets() {
      return Array.from(state.uploadedAssets.values());
    }

    getRecentAssets(limit = 10) {
      return state.assetHistory.slice(0, limit);
    }

    updateAssetSelector() {
      const selectors = $$('.asset-selector');
      selectors.forEach(selector => {
        const currentValue = selector.value;
        selector.innerHTML = '<option value="">Select an asset...</option>';
        
        this.getRecentAssets().forEach(asset => {
          const option = document.createElement('option');
          option.value = asset.id;
          option.textContent = `${asset.filename} (${asset.id.slice(0, 8)}...)`;
          option.dataset.assetId = asset.id;
          selector.appendChild(option);
        });
        
        if (currentValue && state.uploadedAssets.has(currentValue)) {
          selector.value = currentValue;
        }
      });
      
      // Update sidebar assets list
      this.updateSidebarAssets();
    }

    updateSidebarAssets() {
      const assetsList = $('#recentAssetsList');
      if (!assetsList) return;
      
      const recentAssets = this.getRecentAssets(5);
      
      if (recentAssets.length === 0) {
        assetsList.innerHTML = '<div class="no-assets">No assets uploaded yet</div>';
        return;
      }
      
      assetsList.innerHTML = '';
      recentAssets.forEach(asset => {
        const assetItem = document.createElement('div');
        assetItem.className = 'asset-item';
        assetItem.innerHTML = `
          <div class="asset-item-info">
            <div class="asset-item-name">${asset.filename}</div>
            <div class="asset-item-id">${asset.id.slice(0, 8)}...</div>
          </div>
          <div class="asset-item-actions">
            <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${asset.id}'); this.style.background='var(--accent-success)'; setTimeout(() => this.style.background='', 1000)" title="Copy Asset ID">📋</button>
            <a href="${asset.public_url}" target="_blank" class="btn btn-secondary btn-sm" title="View Image">👁️</a>
          </div>
        `;
        assetsList.appendChild(assetItem);
      });
    }

    saveAssets() {
      try {
        localStorage.setItem('dinov3-dashboard-assets', JSON.stringify(state.assetHistory));
      } catch (e) {
        console.warn('Failed to save assets:', e);
      }
    }

    loadAssets() {
      try {
        const saved = localStorage.getItem('dinov3-dashboard-assets');
        if (saved) {
          const assets = JSON.parse(saved);
          assets.forEach(asset => {
            state.uploadedAssets.set(asset.id, asset);
          });
          state.assetHistory = assets;
        }
      } catch (e) {
        console.warn('Failed to load assets:', e);
      }
    }

    createAssetSelector(name, required = false) {
      const group = document.createElement('div');
      group.className = 'param-group';
      
      const label = document.createElement('label');
      label.className = 'param-label';
      label.innerHTML = `
        Asset ID
        ${required ? '<span class="param-required">*</span>' : ''}
      `;
      
      const container = document.createElement('div');
      container.className = 'asset-input-container';
      
      const selector = document.createElement('select');
      selector.className = 'param-input asset-selector';
      selector.name = name;
      selector.dataset.required = required;
      
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'param-input asset-id-input';
      input.name = name;
      input.placeholder = 'Enter asset ID or select from recent uploads';
      input.dataset.required = required;
      
      const toggleBtn = document.createElement('button');
      toggleBtn.type = 'button';
      toggleBtn.className = 'btn btn-secondary asset-toggle';
      toggleBtn.innerHTML = '📋';
      toggleBtn.title = 'Toggle between dropdown and text input';
      toggleBtn.onclick = () => this.toggleAssetInput(container, selector, input);
      
      container.appendChild(selector);
      container.appendChild(input);
      container.appendChild(toggleBtn);
      
      group.append(label, container);
      
      // Initialize with dropdown
      selector.style.display = 'block';
      input.style.display = 'none';
      this.updateAssetSelector();
      
      return group;
    }

    toggleAssetInput(container, selector, input) {
      const isSelectorVisible = selector.style.display !== 'none';
      
      if (isSelectorVisible) {
        selector.style.display = 'none';
        input.style.display = 'block';
        input.value = selector.value;
        input.focus();
      } else {
        input.style.display = 'none';
        selector.style.display = 'block';
        selector.value = input.value;
      }
    }
  }

  const assetManager = new AssetManager();

  // URL and Configuration Management
  function computeBaseUrl() {
    const input = $('#baseUrl');
    if (input && input.value.trim()) return input.value.trim();

    const { protocol, host } = window.location;
    const currentUrl = `${protocol}//${host}`;

    if (host.includes('dino.ft.tc')) {
      return 'https://dino.ft.tc';
    }

    return currentUrl;
  }

  // Health Status Management
  function setHealthStatus(status) {
    const indicator = $('#healthStatus');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');

    indicator.className = 'status-indicator';
    
    switch (status) {
      case 'connected':
        indicator.classList.add('connected');
        text.textContent = 'Connected';
        break;
      case 'error':
        indicator.classList.add('error');
        text.textContent = 'Connection Error';
        break;
      default:
        text.textContent = 'Connecting...';
    }
  }

  async function checkHealth() {
    setHealthStatus('connecting');
    try {
      const res = await fetch(`${state.baseUrl}/api/v1/health`);
      if (res.ok) {
        setHealthStatus('connected');
        toast.show('Successfully connected to API', 'success', 'Connection Established');
      } else {
        setHealthStatus('error');
        toast.show(`Health check failed: ${res.status}`, 'error', 'Connection Error');
      }
    } catch (error) {
      setHealthStatus('error');
      toast.show(`Failed to connect: ${error.message}`, 'error', 'Connection Error');
    }
  }

  // Schema Loading and Endpoint Extraction
  async function loadSchema() {
    loading.show('Loading API schema...');
    try {
      const url = `${state.baseUrl}/openapi.json`;
      console.log('Loading schema from:', url);
      
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Failed to load OpenAPI schema: ${res.status} ${res.statusText}`);
      }
      
      const json = await res.json();
      console.log('Schema loaded successfully:', json);
      
      state.schema = json;
      state.endpoints = extractEndpoints(json);
      console.log('Extracted endpoints:', state.endpoints.length);
      
      renderSidebar();
      updateStats();
      
      toast.show(`Loaded ${state.endpoints.length} endpoints`, 'success', 'Schema Loaded');
    } catch (error) {
      console.error('Error loading schema:', error);
      renderError(error.message);
      toast.show(`Failed to load schema: ${error.message}`, 'error', 'Schema Error');
    } finally {
      loading.hide();
    }
  }

  function extractEndpoints(schema) {
    const paths = schema.paths || {};
    const result = [];
    
    for (const [path, methods] of Object.entries(paths)) {
      for (const [method, spec] of Object.entries(methods)) {
        if (typeof spec !== 'object' || !spec) continue;
        
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
          responses: spec.responses || {},
          deprecated: spec.deprecated || false
        });
      }
    }
    
    return result.sort((a, b) => {
      // Sort by tag first, then by path
      const tagA = a.tags[0] || 'General';
      const tagB = b.tags[0] || 'General';
      if (tagA !== tagB) return tagA.localeCompare(tagB);
      return a.path.localeCompare(b.path);
    });
  }

  function groupByTag(endpoints) {
    const map = new Map();
    for (const ep of endpoints) {
      for (const tag of ep.tags) {
        if (!map.has(tag)) map.set(tag, []);
        map.get(tag).push(ep);
      }
    }
    for (const arr of map.values()) {
      arr.sort((a, b) => a.path.localeCompare(b.path));
    }
    return map;
  }

  // Sidebar Rendering
  function renderSidebar() {
    const nav = $('#nav');
    nav.innerHTML = '';
    
    const filtered = filterEndpoints(state.endpoints);
    const grouped = groupByTag(filtered);
    
    if (filtered.length === 0) {
      nav.innerHTML = `
        <div class="nav-group">
          <div style="padding: var(--space-4); text-align: center; color: var(--text-muted);">
            No endpoints found matching "${state.searchQuery}"
          </div>
        </div>
      `;
      return;
    }
    
    for (const [tag, eps] of grouped.entries()) {
      const group = document.createElement('div');
      group.className = 'nav-group';
      
      const title = document.createElement('div');
      title.className = 'nav-group-title';
      title.textContent = tag;
      group.appendChild(title);
      
      for (const ep of eps) {
        const btn = document.createElement('button');
        btn.className = 'nav-endpoint';
        if (state.selected && state.selected.id === ep.id) {
          btn.classList.add('active');
        }
        
        // Remove /api/v1 prefix for display to save space
        const displayPath = ep.path.replace(/^\/api\/v1/, '') || '/';
        
        btn.innerHTML = `
          <span class="method-badge ${ep.method.toLowerCase()}">${ep.method}</span>
          <span class="endpoint-path">${displayPath}</span>
        `;
        
        btn.addEventListener('click', () => selectEndpoint(ep));
        group.appendChild(btn);
      }
      
      nav.appendChild(group);
    }
  }

  function filterEndpoints(endpoints) {
    if (!state.searchQuery) return endpoints;
    
    const query = state.searchQuery.toLowerCase();
    return endpoints.filter(ep => 
      ep.path.toLowerCase().includes(query) ||
      ep.method.toLowerCase().includes(query) ||
      (ep.summary || '').toLowerCase().includes(query) ||
      (ep.description || '').toLowerCase().includes(query) ||
      ep.tags.some(tag => tag.toLowerCase().includes(query))
    );
  }

  function updateStats() {
    const endpointCount = $('#endpointCount');
    const categoryCount = $('#categoryCount');
    
    if (endpointCount) endpointCount.textContent = state.endpoints.length;
    if (categoryCount) {
      const categories = new Set(state.endpoints.flatMap(ep => ep.tags));
      categoryCount.textContent = categories.size;
    }
  }

  // Endpoint Selection and Rendering
  function selectEndpoint(ep) {
    state.selected = ep;
    renderSidebar(); // Re-render to update active state
    showEndpointContent();
    renderEndpointInfo(ep);
    renderRequestForm(ep);
    hideResponse();
    updateBreadcrumb(ep);
  }

  function showEndpointContent() {
    $('#welcomeState').style.display = 'none';
    $('#endpointContent').style.display = 'block';
  }

  function hideEndpointContent() {
    $('#welcomeState').style.display = 'block';
    $('#endpointContent').style.display = 'none';
    state.selected = null;
    updateBreadcrumb();
  }

  function updateBreadcrumb(ep = null) {
    const breadcrumb = $('#breadcrumbText');
    if (ep) {
      breadcrumb.textContent = `${ep.method} ${ep.path}`;
    } else {
      breadcrumb.textContent = 'Select an endpoint to get started';
    }
  }

  function renderEndpointInfo(ep) {
    const container = $('#endpointInfo');
    container.innerHTML = '';
    
    const section = document.createElement('div');
    section.className = 'endpoint-info';
    
    const header = document.createElement('div');
    header.className = 'endpoint-header';
    
    const method = document.createElement('span');
    method.className = `endpoint-method ${ep.method.toLowerCase()}`;
    method.textContent = ep.method;
    
    const path = document.createElement('span');
    path.className = 'endpoint-path';
    path.textContent = ep.path;
    
    header.append(method, path);
    
    const description = document.createElement('div');
    description.className = 'endpoint-description';
    description.textContent = ep.summary || ep.description || 'No description available';
    
    section.append(header, description);
    container.appendChild(section);
  }

  // Request Form Rendering
  function renderRequestForm(ep) {
    const container = $('#requestSection');
    container.innerHTML = '';
    
    const section = document.createElement('div');
    section.className = 'request-section';
    
    const title = document.createElement('h2');
    title.className = 'section-title';
    title.textContent = 'Request Parameters';
    section.appendChild(title);
    
    // Special handling for upload-media endpoint
    if (ep.path === '/api/v1/upload-media') {
      section.appendChild(createFileUploadForm());
    } else {
      // Path and Query Parameters
      const pathParams = ep.parameters.filter(p => p.in === 'path');
      const queryParams = ep.parameters.filter(p => p.in === 'query');
      
      if (pathParams.length > 0 || queryParams.length > 0) {
        const paramsContainer = document.createElement('div');
        paramsContainer.className = 'param-grid';
        
        [...pathParams, ...queryParams].forEach(param => {
          const group = createParameterGroup(param);
          paramsContainer.appendChild(group);
        });
        
        section.appendChild(paramsContainer);
      }
      
      // Request Body
      const bodySection = buildBodyEditor(ep);
      if (bodySection) {
        section.appendChild(bodySection);
      }
    }
    
    // Action Buttons
    const actions = document.createElement('div');
    actions.className = 'main-actions';
    
    const executeBtn = document.createElement('button');
    executeBtn.className = 'btn btn-primary';
    executeBtn.innerHTML = `
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5,3 19,12 5,21"/>
      </svg>
      Execute Request
    `;
    executeBtn.addEventListener('click', () => executeRequest(ep, section));
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'btn btn-secondary';
    copyBtn.innerHTML = `
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
      </svg>
      Copy cURL
    `;
    copyBtn.addEventListener('click', () => copyCurl(ep, section));
    
    actions.append(executeBtn, copyBtn);
    section.appendChild(actions);
    
    container.appendChild(section);
  }

  function createParameterGroup(param) {
    const group = document.createElement('div');
    group.className = 'param-group';
    
    const label = document.createElement('label');
    label.className = 'param-label';
    label.innerHTML = `
      ${param.name}
      ${param.required ? '<span class="param-required">*</span>' : ''}
    `;
    
    let input;
    
    // Special handling for asset_id parameters
    if (param.name === 'asset_id') {
      group.appendChild(assetManager.createAssetSelector(param.name, param.required));
      return group;
    }
    
    // Regular input fields
    if (param.schema && param.schema.type === 'boolean') {
      input = document.createElement('select');
      input.className = 'param-input';
      input.innerHTML = `
        <option value="">Select...</option>
        <option value="true">True</option>
        <option value="false">False</option>
      `;
    } else if (param.schema && param.schema.enum) {
      input = document.createElement('select');
      input.className = 'param-input';
      input.innerHTML = '<option value="">Select...</option>';
      param.schema.enum.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        input.appendChild(option);
      });
    } else {
      input = document.createElement('input');
      input.type = getInputType(param);
      input.className = 'param-input';
      input.placeholder = getPlaceholder(param);
    }
    
    input.name = param.name;
    input.dataset.location = param.in;
    input.dataset.required = param.required || false;
    
    if (param.description) {
      const help = document.createElement('div');
      help.className = 'param-help';
      help.textContent = param.description;
      group.appendChild(help);
    }
    
    group.append(label, input);
    return group;
  }

  function createFileUploadForm() {
    const container = document.createElement('div');
    container.className = 'file-upload-container';
    
    const title = document.createElement('h3');
    title.className = 'section-subtitle';
    title.textContent = 'Upload Media File';
    container.appendChild(title);
    
    const uploadArea = document.createElement('div');
    uploadArea.className = 'file-upload-area';
    uploadArea.innerHTML = `
      <div class="upload-icon">📁</div>
      <div class="upload-text">
        <strong>Click to upload</strong> or drag and drop
      </div>
      <div class="upload-subtitle">
        Images (JPG, PNG, GIF, WebP) up to 50MB
      </div>
      <input type="file" id="fileInput" accept="image/*" style="display: none;">
    `;
    
    const fileInput = uploadArea.querySelector('#fileInput');
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('drag-over');
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        updateFileDisplay(files[0]);
      }
    });
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        updateFileDisplay(e.target.files[0]);
      }
    });
    
    const fileDisplay = document.createElement('div');
    fileDisplay.className = 'file-display hidden';
    fileDisplay.innerHTML = `
      <div class="file-info">
        <div class="file-name"></div>
        <div class="file-size"></div>
      </div>
      <button type="button" class="btn btn-secondary btn-sm remove-file">Remove</button>
    `;
    
    fileDisplay.querySelector('.remove-file').addEventListener('click', () => {
      fileInput.value = '';
      fileDisplay.classList.add('hidden');
      uploadArea.classList.remove('has-file');
    });
    
    container.appendChild(uploadArea);
    container.appendChild(fileDisplay);
    
    function updateFileDisplay(file) {
      const fileName = fileDisplay.querySelector('.file-name');
      const fileSize = fileDisplay.querySelector('.file-size');
      
      fileName.textContent = file.name;
      fileSize.textContent = formatFileSize(file.size);
      
      fileDisplay.classList.remove('hidden');
      uploadArea.classList.add('has-file');
    }
    
    return container;
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function getInputType(param) {
    if (param.schema && param.schema.type === 'integer') return 'number';
    if (param.schema && param.schema.type === 'number') return 'number';
    if (param.schema && param.schema.format === 'email') return 'email';
    if (param.schema && param.schema.format === 'password') return 'password';
    return 'text';
  }

  function getPlaceholder(param) {
    if (param.schema && param.schema.type) {
      return `${param.schema.type}${param.schema.format ? ` (${param.schema.format})` : ''}`;
    }
    return 'string';
  }

  function buildBodyEditor(ep) {
    const rb = ep.requestBody;
    if (!rb) return null;
    
    const content = rb.content || {};
    const contentType = Object.keys(content)[0];
    if (!contentType) return null;
    
    const section = document.createElement('div');
    section.className = 'request-section';
    
    const title = document.createElement('h2');
    title.className = 'section-title';
    title.textContent = `Request Body (${contentType})`;
    section.appendChild(title);
    
    if (contentType.includes('multipart/form-data')) {
      const schema = content[contentType].schema || {};
      const props = schema.properties || {};
      
      if (Object.keys(props).length === 0) {
        const help = document.createElement('div');
        help.className = 'param-help';
        help.textContent = 'Add files/fields below. Schema not available.';
        section.appendChild(help);
      }
      
      const grid = document.createElement('div');
      grid.className = 'param-grid';
      
      Object.entries(props).forEach(([key, prop]) => {
        const group = document.createElement('div');
        group.className = 'param-group';
        
        const label = document.createElement('label');
        label.className = 'param-label';
        label.textContent = key;
        
        let input;
        if (prop.format === 'binary' || (prop.type === 'string' && prop.format === 'binary')) {
          input = document.createElement('input');
          input.type = 'file';
          input.className = 'param-input';
        } else {
          input = document.createElement('input');
          input.type = 'text';
          input.className = 'param-input';
        }
        
        input.name = key;
        group.append(label, input);
        grid.appendChild(group);
      });
      
      section.appendChild(grid);
    } else {
      // JSON body
      const textarea = document.createElement('textarea');
      textarea.className = 'param-input';
      textarea.rows = 12;
      textarea.style.width = '100%';
      textarea.style.fontFamily = 'var(--font-mono)';
      textarea.style.resize = 'vertical';
      
      const example = content[contentType].example || 
                     content[contentType].examples || 
                     defaultExampleFromSchema(content[contentType].schema);
      
      if (example) {
        try {
          textarea.value = JSON.stringify(example, null, 2);
        } catch (e) {
          console.warn('Failed to stringify example:', e);
        }
      }
      
      textarea.dataset.contentType = contentType;
      section.appendChild(textarea);
    }
    
    return section;
  }

  function defaultExampleFromSchema(schema) {
    if (!schema) return undefined;
    
    try {
      if (schema.example) return schema.example;
      
      if (schema.type === 'object' && schema.properties) {
        const obj = {};
        Object.entries(schema.properties).forEach(([key, prop]) => {
          if (prop.type === 'string') obj[key] = '';
          else if (prop.type === 'number') obj[key] = 0;
          else if (prop.type === 'integer') obj[key] = 0;
          else if (prop.type === 'boolean') obj[key] = false;
          else if (prop.type === 'array') obj[key] = [];
          else obj[key] = null;
        });
        return obj;
      }
      
      return undefined;
    } catch (e) {
      return undefined;
    }
  }

  // Request Execution
  async function executeRequest(ep, section) {
    const url = buildUrl(ep, section);
    const { body, headers } = collectBody(ep, section);
    
    const startTime = performance.now();
    let success = false;
    let status = 0;
    let responseText = '';
    let responseData = null;
    
    try {
      loading.show('Executing request...');
      
      const init = { 
        method: ep.method, 
        headers: { ...headers }
      };
      
      if (body !== undefined) {
        init.body = body;
      }
      
      const response = await fetch(url, init);
      status = response.status;
      success = response.ok;
      
      const contentType = response.headers.get('Content-Type') || '';
      
      if (contentType.includes('application/json')) {
        responseData = await response.json();
        responseText = JSON.stringify(responseData, null, 2);
      } else {
        responseText = await response.text();
      }
      
      // Special handling for upload-media endpoint
      if (ep.path === '/api/v1/upload-media' && success && responseData) {
        const asset = assetManager.addAsset(responseData);
        toast.show(`File uploaded successfully! Asset ID: ${asset.id}`, 'success', 'Upload Complete');
        
        // Show asset info
        showAssetInfo(asset);
      }
      
      // Add to history
      addToHistory({
        endpoint: ep,
        url,
        method: ep.method,
        status,
        success,
        responseTime: Math.round(performance.now() - startTime),
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      responseText = `Error: ${error.message}`;
      toast.show(`Request failed: ${error.message}`, 'error', 'Request Error');
    } finally {
      loading.hide();
    }
    
    const responseTime = Math.round(performance.now() - startTime);
    renderResponse(success, status, responseTime, responseText);
    
    if (success) {
      toast.show(`Request completed successfully (${responseTime}ms)`, 'success', 'Request Complete');
    } else {
      toast.show(`Request failed with status ${status}`, 'error', 'Request Failed');
    }
  }

  function showAssetInfo(asset) {
    const container = $('#requestSection');
    
    // Create asset info display
    const assetInfo = document.createElement('div');
    assetInfo.className = 'asset-info-display';
    assetInfo.innerHTML = `
      <div class="asset-info-header">
        <h3>📁 Uploaded Asset</h3>
        <button type="button" class="btn btn-secondary btn-sm" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
      <div class="asset-details">
        <div class="asset-detail">
          <span class="detail-label">Asset ID:</span>
          <span class="detail-value asset-id" onclick="navigator.clipboard.writeText('${asset.id}'); this.style.background='var(--accent-success)'; setTimeout(() => this.style.background='', 1000)">${asset.id}</span>
        </div>
        <div class="asset-detail">
          <span class="detail-label">Filename:</span>
          <span class="detail-value">${asset.filename}</span>
        </div>
        <div class="asset-detail">
          <span class="detail-label">Size:</span>
          <span class="detail-value">${formatFileSize(asset.file_size)}</span>
        </div>
        <div class="asset-detail">
          <span class="detail-label">Dimensions:</span>
          <span class="detail-value">${asset.width} × ${asset.height}</span>
        </div>
        <div class="asset-detail">
          <span class="detail-label">Public URL:</span>
          <a href="${asset.public_url}" target="_blank" class="detail-value link">View Image</a>
        </div>
      </div>
    `;
    
    // Insert after the form
    const form = container.querySelector('.request-section');
    form.insertAdjacentElement('afterend', assetInfo);
  }

  function buildUrl(ep, section) {
    let url = `${state.baseUrl}${ep.path}`;
    
    // Replace path parameters (including asset selectors)
    const pathInputs = section.querySelectorAll('input[data-location="path"], select[data-location="path"]');
    pathInputs.forEach(input => {
      const value = input.value || input.selectedOptions[0]?.value || '';
      if (value) {
        url = url.replace(`{${input.name}}`, encodeURIComponent(value));
      }
    });
    
    // Add query parameters (including asset selectors)
    const queryInputs = section.querySelectorAll('input[data-location="query"], select[data-location="query"]');
    const queryParams = Array.from(queryInputs)
      .filter(input => {
        const value = input.value || input.selectedOptions[0]?.value || '';
        return value.trim() !== '';
      })
      .map(input => {
        const value = input.value || input.selectedOptions[0]?.value || '';
        return `${encodeURIComponent(input.name)}=${encodeURIComponent(value)}`;
      });
    
    if (queryParams.length > 0) {
      url += (url.includes('?') ? '&' : '?') + queryParams.join('&');
    }
    
    return url;
  }

  function collectBody(ep, section) {
    // Special handling for upload-media endpoint
    if (ep.path === '/api/v1/upload-media') {
      const fileInput = section.querySelector('#fileInput');
      if (fileInput && fileInput.files && fileInput.files[0]) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        return { body: formData, headers: {} };
      } else {
        toast.show('Please select a file to upload', 'error', 'File Required');
        return { body: undefined, headers: {} };
      }
    }
    
    const rb = ep.requestBody;
    if (!rb) return { body: undefined, headers: {} };
    
    const content = rb.content || {};
    const contentType = Object.keys(content)[0];
    if (!contentType) return { body: undefined, headers: {} };
    
    if (contentType.includes('multipart/form-data')) {
      const formData = new FormData();
      const inputs = section.querySelectorAll('input');
      
      inputs.forEach(input => {
        if (!input.name) return;
        
        if (input.type === 'file') {
          if (input.files && input.files[0]) {
            formData.append(input.name, input.files[0]);
          }
        } else if (input.value.trim() !== '') {
          formData.append(input.name, input.value);
        }
      });
      
      return { body: formData, headers: {} };
    }
    
    // JSON body
    const textarea = section.querySelector('textarea');
    if (textarea && textarea.value.trim()) {
      try {
        const json = JSON.parse(textarea.value);
        return { 
          body: JSON.stringify(json), 
          headers: { 'Content-Type': 'application/json' } 
        };
      } catch (e) {
        toast.show('Invalid JSON in request body', 'error', 'JSON Error');
        return { body: undefined, headers: {} };
      }
    }
    
    return { body: undefined, headers: {} };
  }

  function copyCurl(ep, section) {
    const url = buildUrl(ep, section);
    const { body, headers } = collectBody(ep, section);
    
    let curl = `curl -X ${ep.method}`;
    
    // Add headers
    Object.entries(headers).forEach(([key, value]) => {
      curl += ` -H "${key}: ${value}"`;
    });
    
    // Add body
    if (body instanceof FormData) {
      // FormData is complex to serialize, provide a template
      curl += ` -F "field=value"`;
    } else if (typeof body === 'string') {
      curl += ` -d '${body.replace(/'/g, "'\\''")}'`;
    }
    
    curl += ` '${url}'`;
    
    navigator.clipboard.writeText(curl).then(() => {
      toast.show('cURL command copied to clipboard', 'success', 'Copied');
    }).catch(() => {
      toast.show('Failed to copy to clipboard', 'error', 'Copy Error');
    });
  }

  // Response Rendering
  function renderResponse(success, status, responseTime, responseText) {
    const container = $('#responseSection');
    container.classList.remove('hidden');
    container.innerHTML = '';
    
    const section = document.createElement('div');
    section.className = 'response-section';
    
    const header = document.createElement('div');
    header.className = 'response-header';
    
    const statusContainer = document.createElement('div');
    statusContainer.className = 'response-status';
    
    const statusBadge = document.createElement('div');
    statusBadge.className = `status-badge ${success ? 'success' : 'error'}`;
    statusBadge.innerHTML = `
      <span>${success ? '✓' : '✗'}</span>
      <span>${status}</span>
    `;
    
    const timeBadge = document.createElement('div');
    timeBadge.className = 'response-time';
    timeBadge.textContent = `${responseTime}ms`;
    
    statusContainer.append(statusBadge, timeBadge);
    header.appendChild(statusContainer);
    
    const content = document.createElement('div');
    content.className = 'response-content';
    
    const pre = document.createElement('pre');
    pre.textContent = responseText || 'No response body';
    content.appendChild(pre);
    
    section.append(header, content);
    container.appendChild(section);
  }

  function hideResponse() {
    $('#responseSection').classList.add('hidden');
  }

  // History Management
  function addToHistory(request) {
    state.requestHistory.unshift(request);
    if (state.requestHistory.length > 50) {
      state.requestHistory = state.requestHistory.slice(0, 50);
    }
    saveHistory();
  }

  function saveHistory() {
    try {
      localStorage.setItem('dinov3-dashboard-history', JSON.stringify(state.requestHistory));
    } catch (e) {
      console.warn('Failed to save history:', e);
    }
  }

  function loadHistory() {
    try {
      const saved = localStorage.getItem('dinov3-dashboard-history');
      if (saved) {
        state.requestHistory = JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Failed to load history:', e);
    }
  }

  // Error Rendering
  function renderError(message) {
    const nav = $('#nav');
    nav.innerHTML = `
      <div class="nav-group">
        <div style="padding: var(--space-4); text-align: center;">
          <div style="color: var(--accent-error); margin-bottom: var(--space-2);">⚠️</div>
          <div style="color: var(--text-muted); font-size: var(--text-sm);">
            ${message}
          </div>
        </div>
      </div>
    `;
  }

  // Configuration Loading
  async function loadConfig() {
    try {
      const res = await fetch(`${state.baseUrl}/api/v1/config`);
      if (res.ok) {
        const config = await res.json();
        console.log('Configuration loaded:', config);
        
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

  // Event Handlers
  function setupEventHandlers() {
    // Base URL input
    $('#baseUrl').addEventListener('change', async () => {
      state.baseUrl = computeBaseUrl();
      await checkHealth();
    });
    
    // Refresh button
    $('#refreshBtn').addEventListener('click', async () => {
      try {
        $('#refreshBtn').disabled = true;
        await loadSchema();
      } finally {
        $('#refreshBtn').disabled = false;
      }
    });
    
    // Search input
    $('#search').addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderSidebar();
    });
    
    // Clear history button
    $('#clearHistoryBtn').addEventListener('click', () => {
      state.requestHistory = [];
      saveHistory();
      toast.show('Request history cleared', 'success', 'History Cleared');
    });
    
    // Clear assets button
    $('#clearAssetsBtn').addEventListener('click', () => {
      state.uploadedAssets.clear();
      state.assetHistory = [];
      assetManager.saveAssets();
      assetManager.updateAssetSelector();
      toast.show('Asset history cleared', 'success', 'Assets Cleared');
    });
  }

  // Initialization
  async function init() {
    console.log('Initializing modern DINOv3 dashboard...');
    
    // Load saved history and assets
    loadHistory();
    assetManager.loadAssets();
    
    // Set initial base URL
    state.baseUrl = computeBaseUrl();
    $('#baseUrl').value = state.baseUrl;
    
    // Setup event handlers
    setupEventHandlers();
    
    // Initialize dashboard
    try {
      console.log('Loading configuration...');
      await loadConfig();
      
      console.log('Checking health...');
      await checkHealth();
      
      console.log('Loading schema...');
      await loadSchema();
      
      console.log('Dashboard initialization complete');
      toast.show('Dashboard ready!', 'success', 'Welcome');
    } catch (error) {
      console.error('Dashboard initialization failed:', error);
      toast.show('Dashboard initialization failed', 'error', 'Startup Error');
    }
  }

  // Start the application
  document.addEventListener('DOMContentLoaded', init);
})();