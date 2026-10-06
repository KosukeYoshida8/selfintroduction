# PowerShell Website Content Builder for Windows
# Usage: powershell -ExecutionPolicy Bypass -File builder/build.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$ContentDir = Join-Path $RootDir "content"
$ColumnsDir = Join-Path $ContentDir "columns"

Write-Host "--- MyHP Website Content Builder (PowerShell) ---" -ForegroundColor Cyan

# 1. Update News (English & Japanese)
function Update-NewsHtml {
    param(
        [string]$HtmlPath,
        [string]$TxtPath
    )
    if ((-not (Test-Path $HtmlPath)) -or (-not (Test-Path $TxtPath))) { return }
    
    $lines = Get-Content $TxtPath -Encoding UTF8
    $itemsHtml = @()
    foreach ($line in $lines) {
        $l = $line.Trim()
        if ((-not $l) -or $l.StartsWith("#")) { continue }
        if ($l.Contains("|")) {
            $parts = $l.Split("|", 2)
            $date = $parts[0].Trim()
            $text = $parts[1].Trim()
            $itemsHtml += "                    <article class=`"news-item`">"
            $itemsHtml += "                        <span class=`"news-date`">$date</span>"
            $itemsHtml += "                        <p class=`"news-content`">$text</p>"
            $itemsHtml += "                    </article>"
        }
    }
    
    $replacementNews = $itemsHtml -join "`n"
    $htmlContent = Get-Content $HtmlPath -Raw -Encoding UTF8
    $pattern = '(?s)(<div class="news-scroll[^"]*">)(.*?)(</div>\s*</div>)'
    $updatedHtml = [regex]::Replace($htmlContent, $pattern, '$1' + "`n" + $replacementNews + "`n            " + '$3')
    [System.IO.File]::WriteAllText($HtmlPath, $updatedHtml, [System.Text.Encoding]::UTF8)
    $fileName = Split-Path $HtmlPath -Leaf
    Write-Host "Updated news in: $fileName" -ForegroundColor Green
}

# 2. Update Why Blue Horse Modal Script
function Update-BlueHorseHtml {
    param(
        [string]$HtmlPath,
        [string]$TxtPath
    )
    if ((-not (Test-Path $HtmlPath)) -or (-not (Test-Path $TxtPath))) { return }
    $textScript = (Get-Content $TxtPath -Raw -Encoding UTF8).Trim()
    if (-not $textScript) { return }
    
    $htmlContent = Get-Content $HtmlPath -Raw -Encoding UTF8
    $pattern = '(?s)(<p class="modal-placeholder-text">)(.*?)(</p>)'
    $updatedHtml = [regex]::Replace($htmlContent, $pattern, '$1' + "`n                    " + $textScript + "`n                " + '$3')
    [System.IO.File]::WriteAllText($HtmlPath, $updatedHtml, [System.Text.Encoding]::UTF8)
    $fileName = Split-Path $HtmlPath -Leaf
    Write-Host "Updated Why Blue Horse text in: $fileName" -ForegroundColor Green
}

$enIndex = Join-Path $RootDir "index.html"
$jpIndex = Join-Path $RootDir "index_jp.html"
$enNews = Join-Path $ContentDir "news_en.txt"
$jpNews = Join-Path $ContentDir "news_jp.txt"
$enHorse = Join-Path $ContentDir "why_blue_horse_en.txt"
$jpHorse = Join-Path $ContentDir "why_blue_horse_jp.txt"

Update-NewsHtml -HtmlPath $enIndex -TxtPath $enNews
Update-NewsHtml -HtmlPath $jpIndex -TxtPath $jpNews
Update-BlueHorseHtml -HtmlPath $enIndex -TxtPath $enHorse
Update-BlueHorseHtml -HtmlPath $jpIndex -TxtPath $jpHorse

# 3. Process Columns
if (Test-Path $ColumnsDir) {
    $colFiles = Get-ChildItem -Path $ColumnsDir -Filter "*.txt"
    foreach ($colFile in $colFiles) {
        $raw = Get-Content $colFile.FullName -Raw -Encoding UTF8
        $meta = @{}
        $body = $raw
        if ($raw.Contains("---")) {
            $parts = $raw -split "---", 2
            $metaLines = $parts[0] -split "`r?`n"
            $body = $parts[1].Trim()
            foreach ($mline in $metaLines) {
                if ($mline.Contains(":")) {
                    $mparts = $mline.Split(":", 2)
                    $meta[$mparts[0].Trim().ToLower()] = $mparts[1].Trim()
                }
            }
        }
        
        $title = "Untitled Column"
        if ($meta.ContainsKey("title")) { $title = $meta["title"] }
        $date = "2026.04"
        if ($meta.ContainsKey("date")) { $date = $meta["date"] }
        $tag = "Column"
        if ($meta.ContainsKey("tag")) { $tag = $meta["tag"] }
        $summary = ""
        if ($meta.ContainsKey("summary")) { $summary = $meta["summary"] }
        
        $colId = $colFile.BaseName
        $isJp = $colId.EndsWith("_jp")
        $baseId = $colId
        if ($isJp) { $baseId = $colId.Substring(0, $colId.Length - 3) } else { $baseId = $colId.Replace("_en", "") }
        
        $outHtmlName = "${baseId}.html"
        if ($isJp) { $outHtmlName = "${baseId}_jp.html" }
        $outHtmlPath = Join-Path $RootDir $outHtmlName
        
        # Build Body HTML
        $blocks = $body -split "`r?`n`r?`n"
        $bodyHtmlList = @()
        foreach ($block in $blocks) {
            $b = $block.Trim()
            if (-not $b) { continue }
            if ($b.StartsWith("###")) {
                $htext = $b.Replace("###", "").Trim()
                $bodyHtmlList += "                    <h3>$htext</h3>"
            } elseif ($b.StartsWith("##")) {
                $htext = $b.Replace("##", "").Trim()
                $bodyHtmlList += "                    <h2>$htext</h2>"
            } else {
                $bodyHtmlList += "                    <p>`n                        $b`n                    </p>"
            }
        }
        $bodyHtml = $bodyHtmlList -join "`n`n"
        
        $langAttr = "en"
        $switchHref = "${baseId}_jp.html"
        $switchLabel = "JP"
        $switchTitle = "日本語ページへ"
        $backHref = "research.html"
        $backLabel = [char]0x2190 + " Back to Research"
        $returnLabel = [char]0x2190 + " Return to Research List"
        $navHome = "Home"
        $navAbout = "About"
        $navResearch = "Research"
        $navPubs = "Publications"
        $navContact = "Contact"
        $homeFile = "index.html"
        $aboutFile = "about.html"
        $researchFile = "research.html"
        $pubsFile = "publications.html"
        $contactFile = "contact.html"

        if ($isJp) {
            $langAttr = "ja"
            $switchHref = "${baseId}.html"
            $switchLabel = "EN"
            $switchTitle = "Switch to English"
            $backHref = "research_jp.html"
            $backLabel = [char]0x2190 + " 研究一覧へ戻る"
            $returnLabel = [char]0x2190 + " 研究一覧に戻る"
            $navHome = "ホーム"
            $navAbout = "経歴"
            $navResearch = "研究"
            $navPubs = "業績"
            $navContact = "連絡先"
            $homeFile = "index_jp.html"
            $aboutFile = "about_jp.html"
            $researchFile = "research_jp.html"
            $pubsFile = "publications_jp.html"
            $contactFile = "contact_jp.html"
        }
        
        $tmpl = @"
<!DOCTYPE html>
<html lang="__LANG__">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITLE__ — Kosuke Yoshida</title>
    <meta name="description" content="__SUMMARY__">
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
                <li><a href="__HOME_FILE__">__NAV_HOME__</a></li>
                <li><a href="__ABOUT_FILE__">__NAV_ABOUT__</a></li>
                <li><a href="__RESEARCH_FILE__" class="active">__NAV_RESEARCH__</a></li>
                <li><a href="__PUBS_FILE__">__NAV_PUBS__</a></li>
                <li><a href="__CONTACT_FILE__">__NAV_CONTACT__</a></li>
            </ul>
            <div class="lang-switch-container">
                <a href="__SWITCH_HREF__" class="lang-switch-btn" title="__SWITCH_TITLE__">__SWITCH_LABEL__</a>
            </div>
        </div>
    </nav>

    <main class="page-shell">
        <section class="page-hero">
            <div class="container">
                <a class="concept-link back-home" href="__BACK_HREF__">__BACK_LABEL__</a>
                <span class="column-meta-badge">__TAG__ • __DATE__</span>
                <h1 class="column-article-title">__TITLE__</h1>
            </div>
        </section>

        <section>
            <div class="container">
                <article class="card glass-card page-card column-article-body fade-in-observe">
__BODY_HTML__

                    <div class="column-footer-nav">
                        <a href="__BACK_HREF__" class="concept-link">__RETURN_LABEL__</a>
                    </div>
                </article>
            </div>
        </section>
    </main>

    <script src="script.js"></script>
</body>

</html>
"@
        $res = $tmpl.Replace("__LANG__", $langAttr).Replace("__TITLE__", $title).Replace("__SUMMARY__", $summary).Replace("__HOME_FILE__", $homeFile).Replace("__NAV_HOME__", $navHome).Replace("__ABOUT_FILE__", $aboutFile).Replace("__NAV_ABOUT__", $navAbout).Replace("__RESEARCH_FILE__", $researchFile).Replace("__NAV_RESEARCH__", $navResearch).Replace("__PUBS_FILE__", $pubsFile).Replace("__NAV_PUBS__", $navPubs).Replace("__CONTACT_FILE__", $contactFile).Replace("__NAV_CONTACT__", $navContact).Replace("__SWITCH_HREF__", $switchHref).Replace("__SWITCH_TITLE__", $switchTitle).Replace("__SWITCH_LABEL__", $switchLabel).Replace("__BACK_HREF__", $backHref).Replace("__BACK_LABEL__", $backLabel).Replace("__TAG__", $tag).Replace("__DATE__", $date).Replace("__BODY_HTML__", $bodyHtml).Replace("__RETURN_LABEL__", $returnLabel)

        [System.IO.File]::WriteAllText($outHtmlPath, $res, [System.Text.Encoding]::UTF8)
        Write-Host "Generated column article HTML: $outHtmlName" -ForegroundColor Green
    }
}

Write-Host "Content build completed successfully!" -ForegroundColor Cyan
