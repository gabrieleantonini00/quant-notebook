(() => {
  const $ = id => document.getElementById(id);
  const data = typeof areaContent !== 'undefined' ? areaContent : (window.areaContent || {});

  /* ── colour palette per subject ─────────────────────────────────── */
  const colors = {
    statistics:    '#2563eb',
    learning:      '#7c3aed',
    nlp:           '#0d9488',
    finance:       '#d97706',
    econometrics:  '#475569',
    bayesian:      '#db2777',
    setup:         '#0284c7'
  };

  const shortNames = {
    statistics:    'Probability & Statistics',
    learning:      'Statistical Learning',
    nlp:           'Natural Language Processing',
    finance:       'Quantitative Finance',
    econometrics:  'Econometrics',
    bayesian:      'Bayesian Statistics',
    setup:         'Machine Setup'
  };

  const areaIcons = {
    statistics:    '𝒫',
    learning:      'ℒ',
    nlp:           '𝒩',
    finance:       '𝔼',
    econometrics:  '∑',
    bayesian:      'β',
    setup:         '⚙'
  };

  const areaDescriptions = {
    statistics:    'Probability, random variables, inference, ANOVA, and multiple hypothesis testing.',
    learning:      'Model evaluation, explainability, and the behavior of trained learning systems.',
    nlp:           'Bag-of-words, TF-IDF, word embeddings, Word2Vec, transformer self-attention, BERT, and large language models.',
    finance:       'Value-at-Risk, Expected Shortfall, GARCH volatility, Sharpe ratio, Sortino ratio, and risk-adjusted performance.',
    econometrics:  'Spatial dependence, neighboring outcomes, spillovers, and econometric model choice.',
    bayesian:      'Bayesian inference, prior/posterior distributions, MCMC methods, and hierarchical models.',
    setup:         'Development environment, tools, and technical workflow configuration.'
  };

  /* ── topic summaries & full titles ──────────────────────────────── */
  const summaries = {
    'probability-theory':    'Set calculus, De Morgan laws, Kolmogorov axioms, conditional probability, and Bayes\u2019 theorem.',
    'random-variables':      'CDF, PMF, PDF, quantiles, discrete & continuous distributions, and the Jacobian transformation method.',
    'statistical-operators': 'Expectation, variance, covariance, correlation, and bivariate portfolio shortfall risk.',
    'parametric-inference':  'Bias, consistency, efficiency, Method of Moments, Maximum Likelihood, and asymptotic CLT tests.',
    'anova':                 'Compare several group means using between- and within-group variation and the F test.',
    'multiple-hypothesis-testing': 'Control false discoveries across many tests with FWER, FDP, and FDR procedures.',
    'model-evaluation':      'Confusion matrices, precision-recall asymmetric trade-offs, F1-score, and the class imbalance paradox.',
    'explainable-ai':        'Local and global explanations: LIME, SHAP, PDP, ICE, ALE, counterfactuals, and their limits.',
    'bag-of-words':          'Discrete text representations, term-document matrices, TF-IDF weighting schemes, and geometric vectors.',
    'lsa-lda':               'Uncovering latent topics via truncated SVD matrix factorization and Bayesian Dirichlet distributions.',
    'embeddings-word2vec':   'Distributed representations, CBOW vs. Skip-Gram architectures, weight matrices, and vector arithmetic.',
    'transformers':          'Scaled dot-product self-attention, multi-head projection, positional encoding, and BERT pre-training.',
    'llms':                  'Scale dynamics, fine-tuning (LoRA), 3 training stages, RAG architecture, and agent tool execution.',
    'value-at-risk':         'Location-scale frameworks, GARCH volatility, historical simulation, CAViaR, and Basel traffic light testing.',
    'expected-shortfall':    'Artzner coherence axioms, subadditivity proofs, tail expectation, and joint estimation with VaR.',
    'sharpe-ratio':          'Excess return over risk-free benchmark: total standard deviation vs. downside semi-deviation (Sortino).',
    'spatial-econometrics':  'Spatial weights, SAR feedback, direct and indirect effects, and SEM, SLX, and SDM models.'
  };

  const titles = {
    'probability-theory':    'Probability and events',
    'random-variables':      'Random variables',
    'statistical-operators': 'Expectation and variance',
    'parametric-inference':  'Estimation and hypothesis testing',
    'anova':                 'ANOVA',
    'multiple-hypothesis-testing': 'Multiple hypothesis testing',
    'model-evaluation':      'Model evaluation',
    'explainable-ai':        'Explainable AI (XAI)',
    'bag-of-words':          'Bag of words',
    'lsa-lda':               'LSA and LDA',
    'embeddings-word2vec':   'Word embeddings',
    'transformers':          'Transformers',
    'llms':                  'Large language models',
    'value-at-risk':         'Value at risk',
    'expected-shortfall':    'Expected shortfall',
    'sharpe-ratio':          'Sharpe and Sortino ratios',
    'spatial-econometrics':  'Spatial econometrics'
  };

  /* ── flat topic list ─────────────────────────────────────────────── */
  const topics = Object.entries(data).flatMap(([key, area]) =>
    (area.sections || []).filter(n => n.link).map(n => ({
      ...n, key,
      slug: n.link.split('/').pop().replace('.html', '')
    }))
  );

  /* ── update hero counters ────────────────────────────────────────── */
  const totalEl  = $('total-notes');
  if (totalEl)  totalEl.textContent  = topics.length;
  const subEl   = $('total-subjects');
  if (subEl)    subEl.textContent    = Object.values(data).filter(a => a.has_notes).length;

  /* ── DOM helpers ─────────────────────────────────────────────────── */
  const node = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls)             e.className   = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  };

  /* ── view state ──────────────────────────────────────────────────── */
  let currentSubject = 'home'; // 'home' | subject key
  let currentPath = []; // category names beneath the subject
  const slugify = value => value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const hasPath = (topic, path) => path.every((name, i) => topic.category_path?.[i] === name);

  /* ── render: subject area overview — minimal editorial list ──────── */
  function renderHome() {
    const grid = $('note-grid');
    if (!grid) return;

    grid.className = 'subject-list-view';

    // hide toolbar completely on home
    const toolbar = document.querySelector('.topic-toolbar');
    if (toolbar) toolbar.hidden = true;
    const backBtn = $('back-btn');
    if (backBtn) backBtn.hidden = true;

    const items = Object.entries(data)
      .filter(([, a]) => a.has_notes)
      .map(([key, area]) => {
        const color  = colors[key] || '#2563eb';
        const count  = (area.sections || []).filter(s => s.link).length;

        const btn = document.createElement('button');
        btn.className = 'subject-row';
        btn.type = 'button';
        btn.style.setProperty('--area-color', color);
        btn.setAttribute('aria-label', `${shortNames[key] || area.title}, ${count} topics`);

        btn.append(
          node('span', 'sr-name',  shortNames[key] || area.title),
          node('span', 'sr-count', `${count} topics`),
          node('span', 'sr-arrow', '→')
        );

        btn.addEventListener('click', () => setView(key));
        btn.addEventListener('keydown', e => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setView(key); }
        });
        return btn;
      });

    grid.replaceChildren(...items);

    const emptyEl = $('empty-state');
    if (emptyEl) emptyEl.hidden = true;
  }

  /* ── render: topic list for one subject ─────────────────────────── */
  function renderSubjectTopics(key) {
    const grid = $('note-grid');
    if (!grid) return;

    // show toolbar
    const toolbar = document.querySelector('.topic-toolbar');
    if (toolbar) toolbar.hidden = false;

    let backBtn = $('back-btn');
    if (!backBtn) {
      backBtn = document.createElement('button');
      backBtn.id   = 'back-btn';
      backBtn.type = 'button';
      backBtn.className = 'back-btn';
      const toolbar = document.querySelector('.topic-toolbar');
      if (toolbar) toolbar.before(backBtn);
    }
    backBtn.hidden = false;
    const parentName = currentPath.length
      ? (currentPath.length === 1 ? shortNames[key] || data[key]?.title : currentPath.at(-2))
      : 'All subjects';
    backBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M19 12H5"/><path d="M12 5l-7 7 7 7"/></svg>`;
    backBtn.append(document.createTextNode(' ' + parentName));
    backBtn.onclick = () => currentPath.length
      ? setView(key, currentPath.slice(0, -1))
      : setView('home');

    // show search
    const searchWrap = $('search-box-wrap');
    if (searchWrap) searchWrap.hidden = false;

    // filter
    const searchEl = $('search');
    const query = searchEl ? searchEl.value.trim().toLowerCase() : '';

    const subTopics = topics.filter(t => t.key === key && hasPath(t, currentPath));
    const filtered  = subTopics.filter(t => {
      if (!query) return true;
      return [t.title, titles[t.slug] || '', summaries[t.slug] || '', t.summary, ...(t.topics || [])].join(' ').toLowerCase().includes(query);
    });
    const categories = new Map();
    if (!query) {
      subTopics.forEach(topic => {
        const name = topic.category_path?.[currentPath.length];
        if (name) categories.set(name, (categories.get(name) || 0) + 1);
      });
    }
    const directTopics = query ? filtered : filtered.filter(t => (t.category_path || []).length === currentPath.length);

    // title
    const titleEl = $('library-title');
    if (titleEl) {
      titleEl.textContent = currentPath.at(-1) || shortNames[key] || data[key]?.title || 'Topics';
    }
    const countEl = $('result-count');
    if (countEl) {
      countEl.textContent = `${filtered.length} ${filtered.length === 1 ? 'topic' : 'topics'}${query ? ` matching "${query}"` : ''}`;
    }

    const rows = [];
    if (categories.size) {
      const shownCategories = new Set();
      filtered.forEach(topic => {
        const category = topic.category_path?.[currentPath.length];
        if (category && !shownCategories.has(category)) {
          rows.push(renderCategoryRow(key, category, categories.get(category)));
          shownCategories.add(category);
        } else if (!category && (topic.category_path || []).length === currentPath.length) {
          rows.push(renderTopicRow(topic, key));
        }
      });
    } else {
      rows.push(...directTopics.map(t => renderTopicCard(t, colors[key] || '#2563eb')));
    }
    grid.className = categories.size ? 'subject-list-view' : 'note-grid';
    grid.replaceChildren(...rows);

    const emptyEl = $('empty-state');
    if (emptyEl) {
      emptyEl.hidden = rows.length > 0;
      if (!rows.length) {
        emptyEl.replaceChildren(
          node('h3', '', 'No matching topics'),
          node('p', '', 'Try a broader search term or clear the filter.')
        );
        const clr = node('button', '', 'Clear search');
        clr.type = 'button';
        clr.addEventListener('click', () => { if (searchEl) searchEl.value = ''; renderSubjectTopics(key); });
        emptyEl.append(clr);
      }
    }
  }

  function renderCategoryRow(key, name, count) {
    const btn = node('button', 'subject-row');
    btn.type = 'button';
    btn.style.setProperty('--area-color', colors[key] || '#2563eb');
    btn.setAttribute('aria-label', `${name}, ${count} ${count === 1 ? 'topic' : 'topics'}`);
    btn.append(
      node('span', 'sr-name', name),
      node('span', 'sr-count', `${count} ${count === 1 ? 'topic' : 'topics'}`),
      node('span', 'sr-arrow', '→')
    );
    const nextPath = [...currentPath, name];
    btn.addEventListener('click', () => setView(key, nextPath));
    return btn;
  }

  function renderTopicRow(topic, key) {
    const link = node('a', 'subject-row');
    link.href = topic.link;
    link.style.setProperty('--area-color', colors[key] || '#2563eb');
    link.append(
      node('span', 'sr-name', titles[topic.slug] || topic.title),
      node('span', 'sr-count', 'Topic'),
      node('span', 'sr-arrow', '↗')
    );
    return link;
  }

  /* ── render: single topic card ───────────────────────────────────── */
  function renderTopicCard(topic, accentColor) {
    const color = accentColor || colors[topic.key] || '#2563eb';
    const card  = node('article', 'note-card');
    card.style.setProperty('--accent', color);

    const heading = node('h3', 'card-heading');
    const link = node('a', '', titles[topic.slug] || topic.title);
    link.href = topic.link;
    heading.append(link);
    card.append(heading, node('span', 'read-arrow', '↗'));
    return card;
  }

  /* ── main render dispatcher ──────────────────────────────────────── */
  function render() {
    if (currentSubject === 'home') {
      renderHome();
    } else {
      renderSubjectTopics(currentSubject);
    }
  }

  function setView(key, path = []) {
    const valid = key && data[key]?.has_notes && topics.some(t => t.key === key && hasPath(t, path));
    currentSubject = valid ? key : 'home';
    currentPath = valid ? path : [];
    if (searchInput) searchInput.value = '';
    history.replaceState(null, '', currentSubject === 'home' ? '#' : '#' + [key, ...path.map(slugify)].join('/'));
    render();
    // scroll to topics section
    const topicsEl = document.getElementById('topics');
    if (topicsEl && currentSubject !== 'home') {
      setTimeout(() => topicsEl.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
    }
  }

  /* ── keyboard shortcut: '/' focuses search ───────────────────────── */
  const searchInput = $('search');
  if (searchInput) {
    searchInput.addEventListener('input', render);
  }
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== searchInput && !['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)) {
      if (currentSubject !== 'home') {
        e.preventDefault();
        if (searchInput) { searchInput.focus(); searchInput.select(); }
      }
    } else if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.value = '';
      render();
      searchInput.blur();
    }
  });

  /* ── hash routing ────────────────────────────────────────────────── */
  function readHash() {
    let parts;
    try { parts = location.hash.slice(1).split('/').map(decodeURIComponent); }
    catch { parts = []; }
    const [key, ...slugs] = parts;
    const match = topics.find(t => t.key === key && slugs.every((slug, i) => slugify(t.category_path?.[i] || '') === slug));
    currentSubject = match ? key : 'home';
    currentPath = match ? slugs.map((_, i) => match.category_path[i]) : [];
    render();
  }

  addEventListener('hashchange', readHash);
  readHash();
})();
