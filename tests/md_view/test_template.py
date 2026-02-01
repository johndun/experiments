"""Tests for md_view.template module."""

from md_view.template import MATHJAX_SCRIPT, render_template


class TestRenderTemplate:
    """Tests for the render_template function."""

    def test_basic_render(self):
        """Basic rendering should include content and structure."""
        html = render_template(
            content="<p>Hello World</p>",
            toc="<ul><li>Test</li></ul>",
            title="Test Doc",
        )

        assert "<p>Hello World</p>" in html
        assert "<ul><li>Test</li></ul>" in html
        assert "Test Doc" in html
        assert "<!DOCTYPE html>" in html

    def test_dark_mode(self):
        """Dark mode should set data-theme attribute."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
            dark_mode=True,
        )

        assert 'data-theme="dark"' in html

    def test_light_mode(self):
        """Light mode should set data-theme attribute."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
            dark_mode=False,
        )

        assert 'data-theme="light"' in html

    def test_mathjax_enabled(self):
        """MathJax script should be included when enabled."""
        html = render_template(
            content="<p>$x^2$</p>",
            toc="",
            enable_math=True,
        )

        assert "MathJax" in html
        assert "tex-mml-chtml.js" in html

    def test_mathjax_disabled(self):
        """MathJax script should not be included when disabled."""
        html = render_template(
            content="<p>$x^2$</p>",
            toc="",
            enable_math=False,
        )

        assert "MathJax" not in html
        assert "tex-mml-chtml.js" not in html

    def test_toc_enabled(self):
        """Sidebar should be visible when TOC is enabled."""
        html = render_template(
            content="<p>Content</p>",
            toc="<ul><li>Section</li></ul>",
            enable_toc=True,
        )

        assert "display: flex" in html
        assert "margin-left: 280px" in html

    def test_toc_disabled(self):
        """Sidebar should be hidden when TOC is disabled."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
            enable_toc=False,
        )

        assert "display: none" in html
        assert "margin-left: 0" in html

    def test_theme_toggle_button(self):
        """Theme toggle button should be present."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
        )

        assert "theme-toggle" in html
        assert "toggleTheme" in html

    def test_css_variables(self):
        """CSS variables should be defined for theming."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
        )

        assert "--bg-color" in html
        assert "--text-color" in html
        assert "--sidebar-bg" in html

    def test_responsive_styles(self):
        """Responsive styles should be included."""
        html = render_template(
            content="<p>Content</p>",
            toc="",
        )

        assert "@media" in html
        assert "768px" in html


class TestMathJaxScript:
    """Tests for MathJax configuration."""

    def test_mathjax_config(self):
        """MathJax config should include inline and display math."""
        assert "inlineMath" in MATHJAX_SCRIPT
        assert "displayMath" in MATHJAX_SCRIPT
        assert "['$', '$']" in MATHJAX_SCRIPT
        assert "['$$', '$$']" in MATHJAX_SCRIPT

    def test_mathjax_skip_tags(self):
        """MathJax should skip code and pre tags."""
        assert "skipHtmlTags" in MATHJAX_SCRIPT
        assert "'code'" in MATHJAX_SCRIPT
        assert "'pre'" in MATHJAX_SCRIPT
