#!/usr/bin/env python3
"""md2html.py — render Markdown as a self-contained, styled HTML page (or a multi-doc index).

The page renders client-side with marked.js (GFM tables) + mermaid.js (```mermaid``` fences),
and builds a sticky table-of-contents sidebar with scroll-spy. Includes a print stylesheet
(hides chrome) so the browser's Print → Save as PDF gives a clean export.

Single doc vs. many
-------------------
Pass ONE .md           → a viewer for that file.
Pass SEVERAL .md       → one HTML with a document-switcher dropdown in the header; the content
  (or a DIRECTORY)       area swaps between docs. Deep links: #doc=<file>&s=<section-id>.

Reader-experience features (all client-side, the .md stays the source of truth):
  - light / dark theme toggle (persisted, follows prefers-color-scheme by default)
  - document switcher (multi-doc mode) with per-doc TOC, reading time, and hash deep-links
  - copy-to-clipboard buttons on code blocks
  - GitHub-style callouts from blockquotes: > [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION]
  - hover-reveal heading anchor links
  - scroll progress bar, skip-to-content link, reduced-motion support
  - auto reading-time estimate, mobile TOC drawer
  - localized chrome (TOC label, copy button, callout titles, reading time) via --lang

Modes
-----
--fetch   (default)  The HTML fetch()es each .md at load → live source (edit, refresh),
                     no copy of the content in the HTML. Open it with NO server using a
                     "dev browser" (Chrome with --allow-file-access-from-files; see
                     scripts/open_in_dev_browser.sh). A plain double-click in a normal
                     browser is blocked by file:// CORS and shows a friendly banner.
--inline             Embed every .md in the HTML → opens by double-click in any browser,
                     good for emailing/sharing one file. The HTML carries a snapshot,
                     so regenerate after editing the .md.

Usage
-----
  python md2html.py INPUT.md                       # fetch mode, <input>.html beside it
  python md2html.py *.md                            # one index.html with a doc switcher
  python md2html.py docs/                           # all docs/*.md → one index.html
  python md2html.py *.md --inline -o site.html      # portable multi-doc single file
  python md2html.py INPUT.md --lang vi              # Vietnamese chrome labels
  python md2html.py INPUT.md --title "My Spec" --brand "ACME" --badge "DRAFT v0.1"

Only the standard library is used. CDN scripts load over https even from file:// pages.
"""
import argparse, html, json, os, pathlib, re, sys

# Chrome strings localized per --lang. Body content always renders in the source language;
# only these few UI labels change. Vietnamese carries full diacritics on purpose.
LANGS = {
    'en': dict(contents='Contents', copy='Copy', copied='Copied!', skip='Skip to content',
               read='%s min read', theme='Toggle theme', menu='Contents', doc='Document',
               cNOTE='Note', cTIP='Tip', cIMPORTANT='Important', cWARNING='Warning', cCAUTION='Caution'),
    'vi': dict(contents='Mục lục', copy='Sao chép', copied='Đã chép!', skip='Đến nội dung',
               read='%s phút đọc', theme='Đổi giao diện', menu='Mục lục', doc='Tài liệu',
               cNOTE='Ghi chú', cTIP='Mẹo', cIMPORTANT='Quan trọng', cWARNING='Cảnh báo', cCAUTION='Thận trọng'),
    'zh': dict(contents='目录', copy='复制', copied='已复制!', skip='跳到内容',
               read='阅读约 %s 分钟', theme='切换主题', menu='目录', doc='文档',
               cNOTE='注意', cTIP='提示', cIMPORTANT='重要', cWARNING='警告', cCAUTION='当心'),
    'ja': dict(contents='目次', copy='コピー', copied='コピーしました!', skip='本文へスキップ',
               read='読了 %s 分', theme='テーマ切替', menu='目次', doc='ドキュメント',
               cNOTE='メモ', cTIP='ヒント', cIMPORTANT='重要', cWARNING='警告', cCAUTION='注意'),
    'ko': dict(contents='목차', copy='복사', copied='복사됨!', skip='본문으로 건너뛰기',
               read='%s분 분량', theme='테마 전환', menu='목차', doc='문서',
               cNOTE='참고', cTIP='팁', cIMPORTANT='중요', cWARNING='경고', cCAUTION='주의'),
    'es': dict(contents='Contenido', copy='Copiar', copied='¡Copiado!', skip='Saltar al contenido',
               read='%s min de lectura', theme='Cambiar tema', menu='Contenido', doc='Documento',
               cNOTE='Nota', cTIP='Consejo', cIMPORTANT='Importante', cWARNING='Advertencia', cCAUTION='Precaución'),
    'fr': dict(contents='Sommaire', copy='Copier', copied='Copié !', skip='Aller au contenu',
               read='%s min de lecture', theme='Changer de thème', menu='Sommaire', doc='Document',
               cNOTE='Note', cTIP='Astuce', cIMPORTANT='Important', cWARNING='Avertissement', cCAUTION='Attention'),
    'de': dict(contents='Inhalt', copy='Kopieren', copied='Kopiert!', skip='Zum Inhalt springen',
               read='%s Min. Lesezeit', theme='Thema wechseln', menu='Inhalt', doc='Dokument',
               cNOTE='Hinweis', cTIP='Tipp', cIMPORTANT='Wichtig', cWARNING='Warnung', cCAUTION='Vorsicht'),
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="__LANG__">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<script>
  /* Set theme before paint to avoid a flash; honors a saved choice then the OS preference. */
  (function(){try{var t=localStorage.getItem('mdv-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.setAttribute('data-theme',t);}catch(e){document.documentElement.setAttribute('data-theme','light');}})();
</script>
<style>
  :root{
    --primary:#0B4F8A; --primary-d:#083A66; --accent:#0E9F8A;
    --bg:#F4F6FA; --text:#1A2433; --muted:#6B7A90; --line:#E3E8F0;
    --card:#fff; --code-bg:#F6F8FB; --code-text:#243049; --quote-bg:#EEF4FB;
    --th-bg:#F0F4FA; --stripe:#FAFBFD; --link:#2563EB;
    --header-bg:#083A66; --header-text:#fff; --h1:#083A66; --h2:#0B4F8A; --h3:#083A66;
    --help-bg:#FBF0DC; --help-line:#EBD9B4; --help-text:#7C5A14; --btn-border:rgba(255,255,255,.22);
  }
  [data-theme="dark"]{
    --primary:#5BA3E0; --primary-d:#9CC4EA; --accent:#2DD4BF;
    --bg:#0F1419; --text:#DCE3EC; --muted:#8696AC; --line:#27313F;
    --card:#161D26; --code-bg:#1B2330; --code-text:#CDD6E4; --quote-bg:#15202E;
    --th-bg:#1E2735; --stripe:#1A2330; --link:#7FB0F0;
    --header-bg:#0A1622; --header-text:#E8EEF6; --h1:#9CC4EA; --h2:#6BB0EF; --h3:#9CC4EA;
    --help-bg:#2A2310; --help-line:#4A3D17; --help-text:#E3C77A; --btn-border:rgba(255,255,255,.16);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,-apple-system,Roboto,Arial,sans-serif;font-size:15px;line-height:1.65;transition:background .2s,color .2s}
  .skip{position:absolute;left:-999px;top:0;z-index:100;background:var(--accent);color:#fff;padding:10px 16px;border-radius:0 0 8px 0;text-decoration:none;font-size:13px;font-weight:600}
  .skip:focus{left:0}
  #progress{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--accent),var(--primary));z-index:60;transition:width .08s linear}
  .brand{position:sticky;top:0;z-index:30;background:var(--header-bg);color:var(--header-text);display:flex;align-items:center;gap:12px;padding:11px 22px;box-shadow:0 2px 10px rgba(8,58,102,.25)}
  .brand .mark{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#15B8A0,#0B4F8A);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0}
  .brand b{font-size:15px}
  .brand small{display:block;font-size:11px;color:#9FB6CC;font-weight:400}
  .brand .sp{flex:1}
  .brand .badge{background:#B7791F;color:#fff;font-size:10.5px;padding:3px 10px;border-radius:20px;font-weight:700;white-space:nowrap}
  .brand .readtime{color:#9FB6CC;font-size:11.5px;white-space:nowrap}
  .brand a{color:#C9D8E8;text-decoration:none;font-size:12.5px;padding:6px 12px;border:1px solid var(--btn-border);border-radius:7px;margin-left:8px}
  .brand a:hover{background:rgba(255,255,255,.1)}
  .docpicker{background:rgba(255,255,255,.10);color:var(--header-text);border:1px solid var(--btn-border);border-radius:7px;font-size:12.5px;padding:5px 9px;max-width:280px;font-family:inherit;cursor:pointer}
  .docpicker:hover{background:rgba(255,255,255,.16)}
  .docpicker option{color:#1A2433;background:#fff}
  .icon-btn{display:inline-flex;align-items:center;justify-content:center;background:transparent;color:var(--header-text);border:1px solid var(--btn-border);border-radius:7px;width:34px;height:32px;margin-left:8px;cursor:pointer;padding:0}
  .icon-btn:hover{background:rgba(255,255,255,.1)}
  .tocbtn{display:none}
  .helpbox{display:none;padding:13px 22px;background:var(--help-bg);border-bottom:1px solid var(--help-line);color:var(--help-text);font-size:13px;line-height:1.6}
  .helpbox code{background:var(--card);border:1px solid var(--help-line);border-radius:5px;padding:2px 7px;font-family:Consolas,monospace;color:var(--primary-d);font-weight:600}
  .helpbox b{color:var(--help-text)}
  .layout{display:flex;gap:0;align-items:flex-start;max-width:1280px;margin:0 auto}
  .toc{position:sticky;top:58px;align-self:flex-start;width:280px;flex-shrink:0;max-height:calc(100vh - 58px);overflow-y:auto;padding:22px 14px 40px 22px;font-size:13px}
  .toc .toc-h{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);font-weight:700;margin:0 0 10px}
  .toc a{display:block;color:var(--text);text-decoration:none;padding:3px 8px;border-left:2px solid transparent;border-radius:0 4px 4px 0;opacity:.85}
  .toc a:hover{background:color-mix(in srgb,var(--primary) 14%,var(--card));color:var(--primary);opacity:1}
  .toc a.lvl1{font-weight:700;margin-top:8px;opacity:1}
  .toc a.lvl2{padding-left:18px}
  .toc a.lvl3{padding-left:30px;font-size:12px;color:var(--muted)}
  .toc a.active{border-left-color:var(--accent);background:color-mix(in srgb,var(--accent) 16%,var(--card));color:var(--primary-d);font-weight:600;opacity:1}
  .backdrop{display:none}
  .content{flex:1;min-width:0;background:var(--card);margin:18px 22px 60px;padding:36px 48px;border:1px solid var(--line);border-radius:12px;box-shadow:0 1px 3px rgba(10,30,60,.04)}
  .content h1{font-size:25px;color:var(--h1);border-bottom:2px solid var(--line);padding-bottom:10px;margin:34px 0 14px}
  .content h1:first-child{margin-top:0}
  .content h2{font-size:20px;color:var(--h2);margin:30px 0 12px}
  .content h3{font-size:16.5px;color:var(--h3);margin:22px 0 9px}
  .content h4{font-size:14.5px;color:var(--text);margin:18px 0 8px}
  .content h1,.content h2,.content h3{scroll-margin-top:70px}
  .content p{margin:10px 0}
  .content a{color:var(--link);text-decoration:none}
  .content a:hover{text-decoration:underline}
  .content ul,.content ol{margin:10px 0;padding-left:24px}
  .content li{margin:4px 0}
  .content code{background:var(--code-bg);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:12.8px;color:var(--primary-d)}
  .content pre{position:relative;background:var(--code-bg);border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow-x:auto;margin:14px 0}
  .content pre code{background:none;border:none;padding:0;color:var(--code-text);font-size:12.6px;line-height:1.55;display:block;white-space:pre}
  .content pre.mermaid{background:var(--card);text-align:center;border-style:dashed}
  .copy-btn{position:absolute;top:8px;right:8px;background:var(--card);color:var(--muted);border:1px solid var(--line);border-radius:6px;font-size:11px;padding:3px 9px;cursor:pointer;opacity:0;transition:opacity .15s;font-family:inherit}
  .content pre:hover .copy-btn,.copy-btn:focus{opacity:1}
  .copy-btn:hover{color:var(--primary);border-color:var(--primary)}
  .content table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.2px;display:block;overflow-x:auto}
  .content th{background:var(--th-bg);color:var(--primary-d);text-align:left;padding:9px 12px;border:1px solid var(--line);font-weight:700;white-space:nowrap}
  .content td{padding:9px 12px;border:1px solid var(--line);vertical-align:top}
  .content tr:nth-child(even) td{background:var(--stripe)}
  .content blockquote{margin:14px 0;padding:12px 18px;background:var(--quote-bg);border-left:4px solid var(--accent);border-radius:0 8px 8px 0;color:var(--text)}
  .content blockquote p{margin:6px 0}
  /* GitHub-style callouts (a blockquote tagged [!NOTE] etc.) */
  .callout{margin:16px 0;padding:12px 16px 12px 18px;border-left:4px solid var(--c);border-radius:0 8px 8px 0;background:color-mix(in srgb,var(--c) 9%,var(--card));color:var(--text)}
  .callout p{margin:6px 0}.callout p:last-child{margin-bottom:0}
  .callout-title{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--c);margin-bottom:6px;font-size:13.5px}
  .callout-title svg{flex-shrink:0}
  .callout-note{--c:#2563EB}.callout-tip{--c:#0E9F8A}.callout-important{--c:#8B5CF6}.callout-warning{--c:#B7791F}.callout-caution{--c:#DC2626}
  [data-theme="dark"] .callout-note{--c:#60A5FA}[data-theme="dark"] .callout-tip{--c:#2DD4BF}[data-theme="dark"] .callout-important{--c:#A78BFA}[data-theme="dark"] .callout-warning{--c:#E0A82E}[data-theme="dark"] .callout-caution{--c:#F87171}
  .content hr{border:none;border-top:1px solid var(--line);margin:28px 0}
  .anchor{margin-left:8px;color:var(--muted);text-decoration:none;opacity:0;font-weight:400;font-size:.8em}
  .content h1:hover .anchor,.content h2:hover .anchor,.content h3:hover .anchor{opacity:.6}
  .anchor:hover{opacity:1 !important;color:var(--accent)}
  .loaderr{padding:30px 6px;color:var(--help-text);font-size:14px;line-height:1.7}
  .loaderr code{background:var(--help-bg);border:1px solid var(--help-line);border-radius:5px;padding:2px 7px;font-family:Consolas,monospace;color:var(--primary-d);font-weight:600}
  @media print{
    .brand,.toc,.helpbox,#progress,.skip,.copy-btn,.icon-btn,.docpicker,.anchor,.backdrop{display:none !important}
    .content{margin:0;border:none;box-shadow:none;border-radius:0;max-width:100%;background:#fff}
    body{background:#fff;color:#000;font-size:11pt}
    .content pre,.content table,.content blockquote,.callout,.content img{break-inside:avoid}
  }
  @media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto} *{transition:none !important} }
  @media(max-width:1000px){
    .tocbtn{display:inline-flex}
    .docpicker{max-width:150px}
    .toc{position:fixed;top:0;left:0;height:100vh;width:282px;z-index:50;background:var(--bg);transform:translateX(-100%);transition:transform .22s ease;box-shadow:2px 0 22px rgba(0,0,0,.28);padding-top:58px;display:block}
    .toc.open{transform:none}
    .backdrop.open{display:block;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:40}
    .content{margin:14px}
  }
</style>
</head>
<body>
  <a class="skip" id="skip" href="#content">Skip to content</a>
  <div id="progress"></div>
  <header class="brand">
    <button class="icon-btn tocbtn" id="tocToggle" type="button" aria-label="Contents"></button>
    <div class="mark">__MARK__</div>
    <div><b>__BRAND__</b><small>__SUBTITLE__</small></div>
    <select class="docpicker" id="docpicker" aria-label="Select document" style="display:none"></select>
    __BADGE__
    <div class="sp"></div>
    <span class="readtime" id="readtime"></span>
    __LINKS__
    <button class="icon-btn" id="themeBtn" type="button" aria-label="Toggle theme"></button>
  </header>
__HELPBOX__
  <div class="backdrop" id="backdrop"></div>
  <div class="layout">
    <nav class="toc" id="toc"><div class="toc-h" id="toc-h">Contents</div></nav>
    <main class="content" id="content" tabindex="-1"><p style="color:var(--muted)">Loading…</p></main>
  </div>
__MD_SCRIPT__
  <script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    var LANG = __LANGOBJ__;
    var DOCS = __DOCS__;        // [{file, label, id}]  — id is the inline <script> id, or null in fetch mode
    var loadedDoc = null;       // file of the doc currently rendered (shared so render() can build hrefs)
    function curDocFile(){ return loadedDoc || (DOCS[0] && DOCS[0].file) || ''; }
    function sectionHref(id){ return '#doc=' + encodeURIComponent(curDocFile()) + '&s=' + id; }
    var SVG = {
      sun:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19"/></svg>',
      moon:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
      menu:'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
      info:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>',
      tip:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.6.6 1 1.3 1 2.1V16h6v-.4c0-.8.4-1.5 1-2.1A6 6 0 0 0 12 3z"/></svg>',
      important:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M12 8v3M12 14h.01"/></svg>',
      warning:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>'
    };
    var ICON = { NOTE:SVG.info, TIP:SVG.tip, IMPORTANT:SVG.important, WARNING:SVG.warning, CAUTION:SVG.warning };

    __BOOTSTRAP__

    function mermaidTheme(){ return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral'; }
    function runMermaid(){
      document.querySelectorAll('.content .mermaid').forEach(function(m){
        if (m.dataset.src){ m.removeAttribute('data-processed'); m.innerHTML = m.dataset.src; }
      });
      try {
        mermaid.initialize({ startOnLoad:false, theme:mermaidTheme(), securityLevel:'loose', flowchart:{useMaxWidth:true} });
        mermaid.run({ querySelector:'.content .mermaid' });
      } catch(e){ console.warn('mermaid', e); }
    }

    function render(src){
      var content = document.getElementById('content');
      content.innerHTML = marked.parse(src, { gfm:true, breaks:false });

      // ```mermaid``` fences → live diagrams (keep source for re-theming)
      content.querySelectorAll('code.language-mermaid').forEach(function(c){
        var pre = c.closest('pre');
        var holder = document.createElement('pre');
        holder.className = 'mermaid';
        holder.dataset.src = c.textContent;
        holder.textContent = c.textContent;
        pre.replaceWith(holder);
      });
      runMermaid();

      // GitHub-style callouts: blockquote whose first line is [!NOTE] / [!TIP] / ...
      var CALLOUT = /^\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(<br\s*\/?>)?/i;
      content.querySelectorAll('blockquote').forEach(function(bq){
        var first = bq.querySelector('p');
        if (!first) return;
        var m = first.innerHTML.match(CALLOUT);
        if (!m) return;
        var type = m[1].toUpperCase();
        first.innerHTML = first.innerHTML.replace(CALLOUT, '');
        if (!first.innerHTML.trim()) first.remove();
        bq.className = 'callout callout-' + type.toLowerCase();
        var title = document.createElement('div');
        title.className = 'callout-title';
        title.innerHTML = (ICON[type] || '') + '<span>' + (LANG['c' + type] || type) + '</span>';
        bq.insertBefore(title, bq.firstChild);
      });

      // Copy buttons on real code blocks (not mermaid)
      content.querySelectorAll('pre:not(.mermaid)').forEach(function(pre){
        var btn = document.createElement('button');
        btn.className = 'copy-btn'; btn.type = 'button'; btn.textContent = LANG.copy;
        btn.addEventListener('click', function(){
          var code = pre.querySelector('code');
          var txt = code ? code.textContent : pre.textContent;
          navigator.clipboard.writeText(txt).then(function(){
            btn.textContent = LANG.copied;
            setTimeout(function(){ btn.textContent = LANG.copy; }, 1500);
          }).catch(function(){ btn.textContent = '×'; });
        });
        pre.appendChild(btn);
      });

      // Build TOC + heading anchors, with scroll-spy. Hrefs carry the current doc so
      // clicking them never clobbers the selected document (#doc=<file>&s=<id>).
      var toc = document.getElementById('toc');
      toc.innerHTML = '<div class="toc-h" id="toc-h">' + LANG.contents + '</div>';
      var heads = content.querySelectorAll('h1, h2, h3');
      var entries = [];
      heads.forEach(function(h, i){
        var id = 'sec-' + i; h.id = id;
        var label = h.textContent;
        var a = document.createElement('a');
        a.href = sectionHref(id); a.textContent = label;
        a.className = 'lvl' + h.tagName.substring(1);
        toc.appendChild(a);
        var anchor = document.createElement('a');
        anchor.className = 'anchor'; anchor.href = sectionHref(id);
        anchor.setAttribute('aria-label', 'Link to ' + label); anchor.textContent = '#';
        h.appendChild(anchor);
        entries.push({ el:h, link:a });
      });
      var spy = function(){
        var top = window.scrollY + 90, cur = null;
        entries.forEach(function(e){ if (e.el.offsetTop <= top) cur = e; });
        entries.forEach(function(e){ e.link.classList.toggle('active', e === cur); });
      };
      window.removeEventListener('scroll', window.__mdvSpy || function(){});
      window.__mdvSpy = spy;
      window.addEventListener('scroll', spy, { passive:true });
      spy();
    }

    function showReadTime(src){
      var words = (src.trim().match(/\S+/g) || []).length;
      var mins = Math.max(1, Math.round(words / 200));
      document.getElementById('readtime').textContent = LANG.read.replace('%s', mins);
    }

    // --- Chrome wiring (runs once; independent of which doc is shown) ---
    (function(){
      var root = document.documentElement;
      var themeBtn = document.getElementById('themeBtn');
      function paintThemeBtn(){ themeBtn.innerHTML = root.getAttribute('data-theme') === 'dark' ? SVG.sun : SVG.moon; }
      themeBtn.title = LANG.theme; themeBtn.setAttribute('aria-label', LANG.theme); paintThemeBtn();
      themeBtn.addEventListener('click', function(){
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        try { localStorage.setItem('mdv-theme', next); } catch(e){}
        paintThemeBtn(); runMermaid();
      });

      document.getElementById('toc-h').textContent = LANG.contents;
      document.getElementById('skip').textContent = LANG.skip;
      var tocBtn = document.getElementById('tocToggle');
      tocBtn.innerHTML = SVG.menu; tocBtn.setAttribute('aria-label', LANG.menu);
      var toc = document.getElementById('toc'), backdrop = document.getElementById('backdrop');
      function closeToc(){ toc.classList.remove('open'); backdrop.classList.remove('open'); }
      tocBtn.addEventListener('click', function(){ toc.classList.toggle('open'); backdrop.classList.toggle('open'); });
      backdrop.addEventListener('click', closeToc);
      toc.addEventListener('click', function(e){ if (e.target.closest('a')) closeToc(); });

      var bar = document.getElementById('progress');
      function prog(){ var d = document.documentElement; var max = d.scrollHeight - d.clientHeight; bar.style.width = (max > 0 ? (d.scrollTop / max * 100) : 0) + '%'; }
      window.addEventListener('scroll', prog, { passive:true });
      window.addEventListener('resize', prog); prog();

      // --- Document switcher (multi-doc) + hash routing (#doc=<file>&s=<section>) ---
      var picker = document.getElementById('docpicker');
      function parseHash(){
        var h = location.hash.replace(/^#/, ''), o = {};
        h.split('&').forEach(function(p){ var i = p.indexOf('='); if (i > 0) o[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); });
        return o;
      }
      function validDoc(f){ for (var i = 0; i < DOCS.length; i++) if (DOCS[i].file === f) return true; return false; }
      if (DOCS.length > 1){
        DOCS.forEach(function(d){ var o = document.createElement('option'); o.value = d.file; o.textContent = d.label; picker.appendChild(o); });
        picker.style.display = '';
        picker.addEventListener('change', function(){ location.hash = 'doc=' + encodeURIComponent(picker.value); });
      }
      function go(){
        var hp = parseHash();
        var f = (hp.doc && validDoc(hp.doc)) ? hp.doc : DOCS[0].file;
        var sec = hp.s;
        function after(){
          if (sec){ var t = document.getElementById(sec); if (t) t.scrollIntoView(); }
          else { window.scrollTo(0, 0); }
        }
        if (f !== loadedDoc){
          loadedDoc = f;
          if (picker) picker.value = f;
          loadDoc(f).then(after);
        } else { after(); }
      }
      window.addEventListener('hashchange', go);
      go();
    })();
  </script>
</body>
</html>
"""

# loadDoc(file) — mode-specific; returns a Promise that resolves once the doc is rendered.
INLINE_BOOTSTRAP = """function loadDoc(file){
      var id = null;
      for (var i = 0; i < DOCS.length; i++) if (DOCS[i].file === file) id = DOCS[i].id;
      var el = id ? document.getElementById(id) : null;
      var src = el ? el.textContent : '';
      render(src); showReadTime(src);
      return Promise.resolve();
    }"""

FETCH_BOOTSTRAP = """function loadDoc(file){
      var content = document.getElementById('content');
      content.innerHTML = '<p style="color:var(--muted)">Loading…</p>';
      var isFile = location.protocol === 'file:';
      return fetch(file, { cache: 'no-store' })
        .then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
        .then(function(src){ render(src); showReadTime(src); })
        .catch(function(e){
          if (isFile) document.getElementById('helpbox').style.display = 'block';
          content.innerHTML = isFile
            ? '<div class="loaderr">Could not load <code>' + file + '</code> because this is a normal browser opening <code>file://</code> (fetch is blocked).' +
              '<br><br>View with <b>no server</b> in either of two ways:' +
              '<br>• <b>Dev browser:</b> open this file in Chrome started with <code>--allow-file-access-from-files</code> (see <code>scripts/open_in_dev_browser.sh</code>).' +
              '<br>• <b>Portable copy:</b> regenerate with <code>--inline</code> to embed the Markdown, then double-click.' +
              '<br><br>(Or serve over HTTP: <code>python3 -m http.server 8080</code>.)</div>'
            : '<div class="loaderr">Could not load <code>' + file + '</code>: ' + e.message + '</div>';
        });
    }"""


def first_h1(md_text, fallback):
    for line in md_text.splitlines():
        m = re.match(r'#\s+(.*)', line.strip())
        if m:
            return m.group(1).strip()
    return fallback


def build(inputs, out_path, mode, title, brand, subtitle, badge, mark, links, lang):
    out_dir = pathlib.Path(out_path).resolve().parent
    docs, md_scripts = [], []
    for i, mp in enumerate(inputs):
        mp = pathlib.Path(mp)
        text = mp.read_text(encoding='utf-8')
        label = first_h1(text, mp.stem)
        rel = os.path.relpath(mp.resolve(), out_dir).replace(os.sep, '/')
        entry = {'file': rel, 'label': label, 'id': None}
        if mode == 'inline':
            sid = f'md-{i}'
            entry['id'] = sid
            safe_md = re.sub(r'</(script)', r'<\\/\1', text, flags=re.I)
            md_scripts.append(
                f'  <script id="{sid}" type="text/markdown" data-file="{html.escape(rel)}">\n{safe_md}\n</script>'
            )
        docs.append(entry)

    multi = len(docs) > 1
    if title is None:
        title = docs[0]['label'] if not multi else (out_dir.name or 'Documents')
    if subtitle is None:
        subtitle = title if not multi else f'{len(docs)} documents'

    badge_html = f'<span class="badge">{html.escape(badge)}</span>' if badge else ''
    links_html = ''.join(
        f'<a href="{html.escape(href)}">{html.escape(label)}</a>'
        for href, label in links
    )

    if mode == 'fetch':
        md_script = ''
        bootstrap = FETCH_BOOTSTRAP
        first = html.escape(docs[0]['file'])
        helpbox = (
            '  <div class="helpbox" id="helpbox">⚠️ Opened via <code>file://</code> — '
            f'the browser blocked loading <code>{first}</code> (CORS). '
            'Serve the folder over HTTP, or regenerate with <code>--inline</code> for double-click viewing.</div>'
        )
    else:  # inline
        md_script = '\n'.join(md_scripts)
        bootstrap = INLINE_BOOTSTRAP
        helpbox = ''

    out = (TEMPLATE
           .replace('__TITLE__', html.escape(title))
           .replace('__LANG__', html.escape(lang))
           .replace('__BRAND__', html.escape(brand))
           .replace('__SUBTITLE__', html.escape(subtitle))
           .replace('__MARK__', html.escape(mark))
           .replace('__BADGE__', badge_html)
           .replace('__LINKS__', links_html)
           .replace('__HELPBOX__', helpbox)
           .replace('__MD_SCRIPT__', md_script)
           .replace('__LANGOBJ__', json.dumps(LANGS.get(lang, LANGS['en']), ensure_ascii=False))
           .replace('__DOCS__', json.dumps(docs, ensure_ascii=False))
           .replace('__BOOTSTRAP__', bootstrap))
    pathlib.Path(out_path).write_text(out, encoding='utf-8')
    return out_path


def collect_inputs(paths):
    """Expand each path: a directory → its *.md (sorted), a file → itself. Dedupe, README first."""
    found = []
    for p in paths:
        pp = pathlib.Path(p)
        if pp.is_dir():
            found.extend(sorted(pp.glob('*.md'), key=lambda x: x.name.lower()))
        elif pp.suffix.lower() in ('.md', '.markdown') or pp.is_file():
            found.append(pp)
        else:
            sys.exit(f'not a .md file or directory: {p}')
    # dedupe preserving order
    seen, uniq = set(), []
    for f in found:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key); uniq.append(f)
    # bring any README to the front
    uniq.sort(key=lambda x: (0 if x.stem.lower() == 'readme' else 1))
    if not uniq:
        sys.exit('no .md files found')
    return uniq


def main():
    ap = argparse.ArgumentParser(description='Render Markdown as a self-contained styled HTML page (single file or multi-doc index).')
    ap.add_argument('input', nargs='+', help='one or more .md files, or a directory of .md files')
    ap.add_argument('-o', '--out', help='output .html (default: <input>.html for one file, index.html for many)')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--fetch', action='store_const', const='fetch', dest='mode',
                      help='fetch each .md at load (default) — live source, no inline copy; '
                           'view with no server via a dev browser, or serve over http')
    mode.add_argument('--inline', action='store_const', const='inline', dest='mode',
                      help='embed the Markdown — portable single file, double-click in any browser')
    ap.set_defaults(mode='fetch')
    ap.add_argument('--title', help='page <title> / header subtitle (default: first H1, or dir name for multi-doc)')
    ap.add_argument('--brand', default='Document', help='brand name shown in the header')
    ap.add_argument('--subtitle', help='header subtitle (default: title, or "N documents" for multi-doc)')
    ap.add_argument('--badge', help='small badge text, e.g. "DRAFT v0.1"')
    ap.add_argument('--mark', default='❖', help='1-3 char glyph in the header logo box')
    ap.add_argument('--lang', default='en', choices=sorted(LANGS),
                    help='language for chrome labels (TOC, copy button, callout titles, reading time)')
    ap.add_argument('--link', action='append', default=[], metavar='HREF|LABEL',
                    help='header nav link, repeatable, e.g. --link "design.html|Design →"')
    args = ap.parse_args()

    inputs = collect_inputs(args.input)

    links = []
    for spec in args.link:
        if '|' not in spec:
            sys.exit(f'--link must be "HREF|LABEL", got: {spec}')
        href, label = spec.split('|', 1)
        links.append((href.strip(), label.strip()))

    if args.out:
        out_path = args.out
    elif len(inputs) == 1:
        out_path = str(inputs[0].with_suffix('.html'))
    else:
        out_path = str(inputs[0].resolve().parent / 'index.html')

    build(inputs, out_path, args.mode, args.title, args.brand,
          args.subtitle, args.badge, args.mark, links, args.lang)
    print(f'wrote {out_path}  (mode={args.mode}, lang={args.lang}, docs={len(inputs)})')


if __name__ == '__main__':
    main()
