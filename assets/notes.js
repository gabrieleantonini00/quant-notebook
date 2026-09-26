(() => {
  const article = document.querySelector('main > article');
  if (!article) return;
  const progress = document.createElement('div');
  progress.className = 'reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.prepend(progress);
  const headings = [...article.querySelectorAll('h2')];
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
    const print = document.createElement('button');
    print.className = 'contents-print';
    print.type = 'button';
    print.textContent = 'Print or save as PDF';
    print.addEventListener('click', () => window.print());
    contents.append(summary, nav, print);
    header.after(contents);
    nav.addEventListener('click', event => {
      if (event.target.closest('a')) contents.open = false;
    });
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
  };
  let ticking = false;
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => {update(); ticking = false;}); } }, {passive:true});
  addEventListener('resize', update); update();
  if (location.hash) requestAnimationFrame(() => document.getElementById(location.hash.slice(1))?.scrollIntoView());
})();
