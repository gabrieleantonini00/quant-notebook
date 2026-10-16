(() => {
  const article = document.querySelector('main > article');
  if (!article) return;
  const progress = document.createElement('div');
  progress.className = 'reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.prepend(progress);
  const headings = [...article.querySelectorAll('h2')];
  const isFinance = document.body.classList.contains('finance-note');
  const contents = document.createElement('details');
  contents.className = 'article-contents';
  const summary = document.createElement('summary');
  summary.textContent = 'Sections';
  const nav = document.createElement('nav');
  nav.className = 'contents-links';
  nav.setAttribute('aria-label', 'Article sections');
  headings.forEach((heading, i) => {
    if (!heading.id) heading.id = 'section-' + (i + 1);
    const link = document.createElement('a');
    link.href = '#' + heading.id;
    link.textContent = heading.textContent;
    nav.append(link);
  });
  const header = article.querySelector('.article-header');
  if (headings.length > 1 && header) {
    contents.append(summary, nav);
    if (!isFinance) {
      const print = document.createElement('button');
      print.className = 'contents-print';
      print.type = 'button';
      print.textContent = 'Print or save as PDF';
      print.addEventListener('click', () => window.print());
      contents.append(print);
    }
    header.after(contents);
    if (!isFinance) nav.addEventListener('click', event => {
      if (event.target.closest('a')) contents.open = false;
    });
  }
  let updateSections = () => {};
  if (isFinance && headings.length > 1 && header) {
    document.body.classList.add('has-section-nav');
    contents.open = true;
    contents.classList.add('finance-contents');
    const dock = document.createElement('aside');
    dock.className = 'sections-dock';
    dock.hidden = true;
    dock.setAttribute('aria-label', 'Reading navigation');
    const panel = document.createElement('details');
    const toggle = document.createElement('summary');
    const label = document.createElement('span');
    label.className = 'sections-label';
    label.textContent = 'Sections';
    const position = document.createElement('span');
    position.className = 'sections-position';
    const current = document.createElement('span');
    current.className = 'sections-current';
    toggle.append(label, position, current);
    const dockNav = nav.cloneNode(true);
    dockNav.setAttribute('aria-label', 'Article sections while reading');
    panel.append(toggle, dockNav);
    dock.append(panel);
    document.body.append(dock);
    const links = [...nav.querySelectorAll('a')];
    const dockLinks = [...dockNav.querySelectorAll('a')];
    [links, dockLinks].forEach(list => list.forEach((link, i) => {
      const number = document.createElement('span');
      number.className = 'section-number';
      number.setAttribute('aria-hidden', 'true');
      number.textContent = String(i + 1).padStart(2, '0');
      link.prepend(number);
    }));
    let active = -1;
    updateSections = () => {
      const shouldHide = contents.getBoundingClientRect().bottom > 88;
      if (shouldHide && !dock.hidden) panel.open = false;
      dock.hidden = shouldHide;
      let index = 0;
      headings.forEach((heading, i) => {
        if (heading.getBoundingClientRect().top <= 150) index = i;
      });
      if (scrollY + innerHeight >= document.documentElement.scrollHeight - 8) index = headings.length - 1;
      if (index === active) return;
      active = index;
      [links, dockLinks].forEach(list => list.forEach((link, i) => {
        if (i === index) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }));
      position.textContent = `${String(index + 1).padStart(2, '0')} / ${String(headings.length).padStart(2, '0')}`;
      current.textContent = headings[index].textContent;
    };
    dockNav.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link) return;
      panel.open = false;
      // Retain keyboard focus at the chosen section when the panel closes.
      const heading = headings[dockLinks.indexOf(link)];
      heading.setAttribute('tabindex', '-1');
      heading.focus({preventScroll: true});
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && panel.open) {
        panel.open = false;
        toggle.focus();
      }
    });
    document.addEventListener('click', event => {
      if (panel.open && !dock.contains(event.target)) panel.open = false;
    });
    contents.addEventListener('toggle', updateSections);
    // Fonts, figures, and formula rendering can change the section positions.
    new ResizeObserver(() => updateSections()).observe(article);
  }
  article.querySelectorAll('table').forEach(table => {
    if (!table.parentElement.classList.contains('table-wrap')) {
      const wrap = document.createElement('div'); wrap.className = 'table-wrap';
      table.before(wrap); wrap.append(table);
    }
  });
  const update = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = (max > 0 ? Math.min(100, scrollY / max * 100) : 100) + '%';
    updateSections();
  };
  let ticking = false;
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => {update(); ticking = false;}); } }, {passive:true});
  addEventListener('resize', update); update();
  if (location.hash) requestAnimationFrame(() => document.getElementById(location.hash.slice(1))?.scrollIntoView());
})();
