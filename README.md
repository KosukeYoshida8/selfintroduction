# Kosuke Yoshida — Personal Homepage Repository (`MyHP`)

This repository contains the source code and content generator for the personal academic homepage of **Kosuke Yoshida** (PhD Student in Cognitive Computational Neuroscience).

---

## 🌟 Features

- **Bright & Clean Modern Academic Design**: Off-white ambient styling, soft elevated cards, and clean typography.
- **Side-by-Side Responsive Hero Layout**: Portrait artwork on the left with anchored interactive modal trigger (`🎨 Why Blue Horse?`) and bio/affiliation on the right.
- **Bilingual English & Japanese Support**: Dedicated Japanese pages (`index_jp.html`, `about_jp.html`, `research_jp.html`, etc.) with a `JP` / `EN` toggle switch in the navigation header.
- **Columns & Essays System**: Dedicated section on the Research page leading to full column article pages (`column-1.html`, `column-1_jp.html`).
- **Plain Text Content Manager**: Easily update news, Why Blue Horse text, or create new column articles by editing plain text files in `content/` without writing HTML!

---

## 📂 Repository Structure

```
MyHP/
├── content/                     <-- Plain text content files (EDIT THESE!)
│   ├── news_en.txt
│   ├── news_jp.txt
│   ├── why_blue_horse_en.txt
│   ├── why_blue_horse_jp.txt
│   └── columns/
│       ├── column-1_en.txt
│       └── column-1_jp.txt
├── builder/                     <-- Site update scripts & guide
│   ├── build.py                 <-- Python updater script
│   ├── build.js                 <-- Node.js updater script
│   ├── build.ps1                <-- PowerShell updater script
│   └── README.md
├── images/                      <-- Image assets
├── index.html                   <-- English Home Page
├── index_jp.html                <-- Japanese Home Page
├── about.html                   <-- English About Page
├── about_jp.html                <-- Japanese About Page
├── research.html                <-- English Research Page
├── research_jp.html             <-- Japanese Research Page
├── publications.html            <-- English Publications Page
├── publications_jp.html         <-- Japanese Publications Page
├── contact.html                 <-- English Contact Page
├── contact_jp.html              <-- Japanese Contact Page
├── column-1.html                <-- English Column #1 Article
├── column-1_jp.html             <-- Japanese Column #1 Article
├── style.css                    <-- Main CSS stylesheet
├── script.js                    <-- Client-side JavaScript
└── README.md                    <-- Repository guide
```

---

## ✏️ How to Update Content (Plain Text Workflow)

### 1. Update News
Edit `content/news_en.txt` (English) or `content/news_jp.txt` (Japanese) with lines formatted as:
```text
YYYY.MM.DD | News text goes here
```

### 2. Update Why Blue Horse Story
Edit `content/why_blue_horse_en.txt` or `content/why_blue_horse_jp.txt`.

### 3. Add a New Column
Create a text file in `content/columns/` (e.g. `column-2_en.txt` and `column-2_jp.txt`) with metadata:
```text
title: Your Column Title
date: 2026.05
tag: Column #2
summary: A brief summary of the column.
---
Write your column article text here.
```

### 4. Run the Builder Script
Run any of the build scripts to automatically generate and update all HTML files:

- **Python**: `python builder/build.py`
- **Node.js**: `node builder/build.js`
- **PowerShell (Windows)**: `powershell -ExecutionPolicy Bypass -File builder/build.ps1`

---

## 🚀 Pushing to Remote Repository (GitHub / Git)

This repository uses relative paths everywhere and is 100% portable for remote hosting (GitHub Pages, Vercel, Netlify, Pantheon).

To push your changes to your remote repository:
```bash
git add .
git commit -m "Update site content and layout"
git push origin main
```
