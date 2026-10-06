#!/usr/bin/env node
/**
 * MyHP Website Content Builder (Node.js version)
 * =============================================
 * Usage: node builder/build.js
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const CONTENT_DIR = path.join(ROOT_DIR, 'content');
const COLUMNS_DIR = path.join(CONTENT_DIR, 'columns');

function readText(filePath) {
    if (!fs.existsSync(filePath)) return '';
    return fs.readFileSync(filePath, 'utf-8').trim();
}

function writeText(filePath, content) {
    fs.writeFileSync(filePath, content, 'utf-8');
}

function parseNews(filePath) {
    const raw = readText(filePath);
    const items = [];
    raw.split(/\r?\n/).forEach(line => {
        line = line.trim();
        if (!line || line.startsWith('#')) return;
        if (line.includes('|')) {
            const parts = line.split('|');
            const date = parts[0].trim();
            const text = parts.slice(1).join('|').trim();
            items.push({ date, text });
        }
    });
    return items;
}

function generateNewsHtml(items) {
    return items.map(item => {
        return `                    <article class="news-item">
                        <span class="news-date">${item.date}</span>
                        <p class="news-content">${item.text}</p>
                    </article>`;
    }).join('\n');
}

function updateNews(htmlPath, txtPath) {
    if (!fs.existsSync(htmlPath) || !fs.existsSync(txtPath)) return;
    const items = parseNews(txtPath);
    if (!items.length) return;
    const newsHtml = generateNewsHtml(items);
    let content = readText(htmlPath);
    content = content.replace(/(<div class="news-scroll glass-card fade-in-observe">)[\s\S]*?(<\/div>)/, `$1\n${newsHtml}\n                $2`);
    writeText(htmlPath, content);
    console.log(`Updated news in: ${path.basename(htmlPath)}`);
}

function updateBlueHorse(htmlPath, txtPath) {
    if (!fs.existsSync(htmlPath) || !fs.existsSync(txtPath)) return;
    const textScript = readText(txtPath);
    if (!textScript) return;
    let content = readText(htmlPath);
    content = content.replace(/(<p class="modal-placeholder-text">)[\s\S]*?(<\/p>)/, `$1\n                    ${textScript}\n                $2`);
    writeText(htmlPath, content);
    console.log(`Updated Why Blue Horse text in: ${path.basename(htmlPath)}`);
}

function parseColumnFile(filePath) {
    const raw = readText(filePath);
    const metadata = {};
    let body = raw;
    if (raw.includes('---')) {
        const parts = raw.split('---');
        const metaLines = parts[0].split(/\r?\n/);
        body = parts.slice(1).join('---').trim();
        metaLines.forEach(line => {
            if (line.includes(':')) {
                const kv = line.split(':');
                const k = kv[0].trim().toLowerCase();
                const v = kv.slice(1).join(':').trim();
                metadata[k] = v;
            }
        });
    }

    return {
        title: metadata.title || 'Untitled Column',
        date: metadata.date || '2026.04',
        tag: metadata.tag || 'Column',
        summary: metadata.summary || '',
        body: body
    };
}

function formatMarkdownBody(bodyText) {
    const blocks = bodyText.split(/\r?\n\r?\n/);
    return blocks.map(block => {
        block = block.trim();
        if (!block) return '';
        if (block.startsWith('###')) {
            return `                    <h3>${block.replace(/^###\s*/, '')}</h3>`;
        } else if (block.startsWith('##')) {
            return `                    <h2>${block.replace(/^##\s*/, '')}</h2>`;
        } else {
            return `                    <p>\n                        ${block}\n                    </p>`;
        }
    }).filter(Boolean).join('\n\n');
}

function processColumns() {
    if (!fs.existsSync(COLUMNS_DIR)) return;
    const files = fs.readdirSync(COLUMNS_DIR).filter(f => f.endsWith('.txt')).sort();
    
    const enCols = [];
    const jpCols = [];

    files.forEach(file => {
        const filePath = path.join(COLUMNS_DIR, file);
        const colData = parseColumnFile(filePath);
        const colId = path.basename(file, '.txt');
        
        if (colId.endsWith('_jp')) {
            const baseId = colId.slice(0, -3);
            const targetHtml = path.join(ROOT_DIR, `${baseId}_jp.html`);
            jpCols.push({ baseId, data: colData });
            generateColumnHtml(targetHtml, colData, baseId, 'jp');
        } else {
            const baseId = colId.replace(/_en$/, '');
            const targetHtml = path.join(ROOT_DIR, `${baseId}.html`);
            enCols.push({ baseId, data: colData });
            generateColumnHtml(targetHtml, colData, baseId, 'en');
        }
    });

    updateResearchColumnsList(path.join(ROOT_DIR, 'research.html'), enCols, 'en');
    updateResearchColumnsList(path.join(ROOT_DIR, 'research_jp.html'), jpCols, 'jp');
}

function updateResearchColumnsList(researchHtmlPath, cols, lang) {
    if (!fs.existsSync(researchHtmlPath) || !cols.length) return;
    let content = readText(researchHtmlPath);

    const cardsHtml = cols.map(c => {
        const linkTarget = lang === 'jp' ? `${c.baseId}_jp.html` : `${c.baseId}.html`;
        const readMoreText = lang === 'jp' ? 'コラムを読む →' : 'Read Column →';
        return `                            <article class="column-item-card">
                                <div class="column-header-row">
                                    <span class="column-tag">${c.data.tag}</span>
                                    <span class="column-date">${c.data.date}</span>
                                </div>
                                <h4><a href="${linkTarget}">${c.data.title}</a></h4>
                                <p class="column-summary">
                                    ${c.data.summary}
                                </p>
                                <a href="${linkTarget}" class="read-column-link">${readMoreText}</a>
                            </article>`;
    }).join('\n');

    content = content.replace(/(<div class="columns-list">)[\s\S]*?(<\/div>\s*<\/div>\s*<\/div>)/, `$1\n${cardsHtml}\n                        $2`);
    writeText(researchHtmlPath, content);
    console.log(`Updated columns list in: ${path.basename(researchHtmlPath)}`);
}

function generateColumnHtml(targetHtmlPath, colData, baseId, lang) {
    const bodyHtml = formatMarkdownBody(colData.body);
    const langAttr = lang === 'jp' ? 'ja' : 'en';
    const switchHref = lang === 'jp' ? `${baseId}.html` : `${baseId}_jp.html`;
    const switchLabel = lang === 'jp' ? 'EN' : 'JP';
    const switchTitle = lang === 'jp' ? 'Switch to English' : '日本語ページへ';
    const backHref = lang === 'jp' ? 'research_jp.html' : 'research.html';
    const backLabel = lang === 'jp' ? '← 研究一覧へ戻る' : '← Back to Research';
    const returnLabel = lang === 'jp' ? '← 研究一覧に戻る' : '← Return to Research List';
    const navHome = lang === 'jp' ? 'ホーム' : 'Home';
    const navAbout = lang === 'jp' ? '経歴' : 'About';
    const navResearch = lang === 'jp' ? '研究' : 'Research';
    const navPubs = lang === 'jp' ? '業績' : 'Publications';
    const navContact = lang === 'jp' ? '連絡先' : 'Contact';

    const homeFile = lang === 'jp' ? 'index_jp.html' : 'index.html';
    const aboutFile = lang === 'jp' ? 'about_jp.html' : 'about.html';
    const researchFile = lang === 'jp' ? 'research_jp.html' : 'research.html';
    const pubsFile = lang === 'jp' ? 'publications_jp.html' : 'publications.html';
    const contactFile = lang === 'jp' ? 'contact_jp.html' : 'contact.html';

    const htmlContent = `<!DOCTYPE html>
<html lang="${langAttr}">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${colData.title} — Kosuke Yoshida</title>
    <meta name="description" content="${colData.summary}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>

<body class="page-body">
    <div class="background-canvas" id="canvas-container"></div>
    <nav class="glass-nav">
        <div class="nav-content">
            <ul class="nav-links">
                <li><a href="${homeFile}">${navHome}</a></li>
                <li><a href="${aboutFile}">${navAbout}</a></li>
                <li><a href="${researchFile}" class="active">${navResearch}</a></li>
                <li><a href="${pubsFile}">${navPubs}</a></li>
                <li><a href="${contactFile}">${navContact}</a></li>
            </ul>
            <div class="lang-switch-container">
                <a href="${switchHref}" class="lang-switch-btn" title="${switchTitle}">${switchLabel}</a>
            </div>
        </div>
    </nav>

    <main class="page-shell">
        <section class="page-hero">
            <div class="container">
                <a class="concept-link back-home" href="${backHref}">${backLabel}</a>
                <span class="column-meta-badge">${colData.tag} • ${colData.date}</span>
                <h1 class="column-article-title">${colData.title}</h1>
            </div>
        </section>

        <section>
            <div class="container">
                <article class="card glass-card page-card column-article-body fade-in-observe">
${bodyHtml}

                    <div class="column-footer-nav">
                        <a href="${backHref}" class="concept-link">${returnLabel}</a>
                    </div>
                </article>
            </div>
        </section>
    </main>

    <script src="script.js"></script>
</body>

</html>
`;
    writeText(targetHtmlPath, htmlContent);
    console.log(`Generated column article HTML: ${path.basename(targetHtmlPath)}`);
}

function main() {
    console.log('--- MyHP Website Content Builder (Node.js) ---');
    updateNews(path.join(ROOT_DIR, 'index.html'), path.join(CONTENT_DIR, 'news_en.txt'));
    updateNews(path.join(ROOT_DIR, 'index_jp.html'), path.join(CONTENT_DIR, 'news_jp.txt'));
    updateBlueHorse(path.join(ROOT_DIR, 'index.html'), path.join(CONTENT_DIR, 'why_blue_horse_en.txt'));
    updateBlueHorse(path.join(ROOT_DIR, 'index_jp.html'), path.join(CONTENT_DIR, 'why_blue_horse_jp.txt'));
    processColumns();
    console.log('Content build completed successfully!');
}

main();
