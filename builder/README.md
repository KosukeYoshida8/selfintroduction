# MyHP Content Updater Guide

This directory contains the automated site update scripts. Instead of manually editing HTML files when you have a new news item, a new column, or an updated story script, you can write simple plain text files in the `content/` folder and run the build script!

---

## 📂 Folder Structure

```
MyHP/
├── content/
│   ├── news_en.txt            <-- English News list
│   ├── news_jp.txt            <-- Japanese News list (ニュース)
│   ├── why_blue_horse_en.txt  <-- English "Why Blue Horse?" modal text
│   ├── why_blue_horse_jp.txt  <-- Japanese "青い馬とは？" modal text
│   └── columns/
│       ├── column-1_en.txt    <-- Column #1 English text
│       ├── column-1_jp.txt    <-- Column #1 Japanese text
│       ├── column-2_en.txt    <-- (Optional) Column #2 English text
│       └── column-2_jp.txt    <-- (Optional) Column #2 Japanese text
└── builder/
    ├── build.py               <-- Python build script
    ├── build.js               <-- Node.js build script
    ├── build.ps1              <-- PowerShell build script (Windows)
    └── README.md              <-- This guide
```

---

## 📝 How to Edit Content

### 1. Adding/Updating News Items
Open `content/news_en.txt` (or `content/news_jp.txt`) in any text editor.
Write news items using the format: `YYYY.MM.DD | Content`

**Example `content/news_en.txt`:**
```text
2026.04.15 | Published new preprint on bioRxiv.
2026.03.25 | Presented recent work at Symposium on Contrarianism in Kyoto.
2026.01.10 | Got a grant for organizing a conference from Japanese Neural Network Society.
```

### 2. Updating "Why Blue Horse?" Modal Script
Open `content/why_blue_horse_en.txt` (or `content/why_blue_horse_jp.txt`) and type your story text directly.

### 3. Adding a New Column
Inside `content/columns/`, create a new pair of text files, e.g., `column-2_en.txt` and `column-2_jp.txt`.

**Example `content/columns/column-2_en.txt`:**
```text
title: Perspectives on Self-Control and Decision Dynamics
date: 2026.05
tag: Column #2
summary: Exploring how cognitive control mechanisms are represented in neural circuits.
---
Write your column article here.

### Heading Section
Paragraph text...
```

---

## 🚀 How to Run the Update Script

Choose any of the following commands depending on your operating system or installed tools:

### Option A: Python (Cross-platform)
```bash
python builder/build.py
```
*(or `python3 builder/build.py` on macOS / Linux)*

### Option B: Node.js (Cross-platform)
```bash
node builder/build.js
```

### Option C: Windows PowerShell (Native)
```powershell
powershell -ExecutionPolicy Bypass -File builder/build.ps1
```

---

## 🌐 Deploying to Git / Remote Repository

When you push the `MyHP` folder to GitHub or your remote Git repository:
1. Commit all updated files including `content/`, `builder/`, and the generated `.html` files.
2. Push to your repository:
   ```bash
   git add .
   git commit -m "Update site content"
   git push origin main
   ```
3. Your website hosted on GitHub Pages, Vercel, Netlify, or Pantheon will immediately display the updated content!
