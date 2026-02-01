"""HTML template with CSS/JS for markdown rendering."""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #24292e;
            --sidebar-bg: #f6f8fa;
            --border-color: #e1e4e8;
            --link-color: #0366d6;
            --code-bg: #f6f8fa;
            --heading-color: #24292e;
        }}

        [data-theme="dark"] {{
            --bg-color: #0d1117;
            --text-color: #c9d1d9;
            --sidebar-bg: #161b22;
            --border-color: #30363d;
            --link-color: #58a6ff;
            --code-bg: #161b22;
            --heading-color: #f0f6fc;
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
            display: flex;
        }}

        .sidebar {{
            width: 280px;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            padding: 20px;
            overflow-y: auto;
            display: {sidebar_display};
            flex-direction: column;
        }}

        .sidebar h2 {{
            margin: 0 0 15px 0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-color);
            opacity: 0.7;
        }}

        .sidebar .toc {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .sidebar .toc li {{
            margin: 5px 0;
        }}

        .sidebar .toc a {{
            color: var(--text-color);
            text-decoration: none;
            font-size: 14px;
            display: block;
            padding: 4px 0;
            opacity: 0.8;
            transition: opacity 0.2s;
        }}

        .sidebar .toc a:hover {{
            opacity: 1;
            color: var(--link-color);
        }}

        .sidebar .toc .toc-h2 {{
            padding-left: 0;
        }}

        .sidebar .toc .toc-h3 {{
            padding-left: 15px;
            font-size: 13px;
        }}

        .sidebar .toc .toc-h4 {{
            padding-left: 30px;
            font-size: 12px;
        }}

        .content {{
            flex: 1;
            margin-left: {content_margin};
            padding: 40px 60px;
            max-width: 900px;
        }}

        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--sidebar-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 16px;
            z-index: 1000;
            transition: background-color 0.2s;
        }}

        .theme-toggle:hover {{
            background: var(--border-color);
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--heading-color);
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}

        h1 {{
            font-size: 2em;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3em;
        }}

        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3em;
        }}

        h3 {{
            font-size: 1.25em;
        }}

        a {{
            color: var(--link-color);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        code {{
            background-color: var(--code-bg);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono",
                Menlo, monospace;
        }}

        pre {{
            background-color: var(--code-bg);
            padding: 16px;
            overflow-x: auto;
            border-radius: 6px;
            line-height: 1.45;
        }}

        pre code {{
            background: none;
            padding: 0;
            font-size: 85%;
        }}

        blockquote {{
            border-left: 4px solid var(--border-color);
            margin: 0;
            padding-left: 16px;
            color: var(--text-color);
            opacity: 0.8;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}

        th, td {{
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            text-align: left;
        }}

        th {{
            background-color: var(--sidebar-bg);
            font-weight: 600;
        }}

        img {{
            max-width: 100%;
            height: auto;
        }}

        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 24px 0;
        }}

        ul, ol {{
            padding-left: 2em;
        }}

        li {{
            margin: 4px 0;
        }}

        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}
            .content {{
                margin-left: 0;
                padding: 20px;
            }}
        }}
    </style>
    {mathjax}
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <span class="theme-icon">🌙</span>
    </button>

    <nav class="sidebar">
        <h2>Contents</h2>
        {toc}
    </nav>

    <main class="content">
        {content}
    </main>

    <script>
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            const icon = newTheme === 'dark' ? '☀️' : '🌙';
            document.querySelector('.theme-icon').textContent = icon;
            localStorage.setItem('mdview-theme', newTheme);
        }}

        // Restore theme from localStorage
        (function() {{
            const savedTheme = localStorage.getItem('mdview-theme');
            if (savedTheme) {{
                document.documentElement.setAttribute('data-theme', savedTheme);
                const icon = savedTheme === 'dark' ? '☀️' : '🌙';
                document.querySelector('.theme-icon').textContent = icon;
            }}
        }})();
    </script>
</body>
</html>
"""

MATHJAX_SCRIPT = """
    <script>
        MathJax = {
            tex: {
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                processEscapes: true
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
            }
        };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
        async></script>
"""


def render_template(
    content: str,
    toc: str,
    title: str = "Markdown Viewer",
    dark_mode: bool = False,
    enable_math: bool = True,
    enable_toc: bool = True,
) -> str:
    """Render the HTML template with the given content and options."""
    theme = "dark" if dark_mode else "light"
    mathjax = MATHJAX_SCRIPT if enable_math else ""
    sidebar_display = "flex" if enable_toc else "none"
    content_margin = "280px" if enable_toc else "0"

    return HTML_TEMPLATE.format(
        title=title,
        theme=theme,
        mathjax=mathjax,
        toc=toc,
        content=content,
        sidebar_display=sidebar_display,
        content_margin=content_margin,
    )
