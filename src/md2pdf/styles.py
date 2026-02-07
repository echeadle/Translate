"""PDF styling and CSS generation."""

from md2pdf.config import Config


def get_default_css(config: Config) -> str:
    """Generate default CSS for PDF styling.

    Args:
        config: Configuration settings for styling.

    Returns:
        CSS string with complete styling rules.
    """
    return f"""
@page {{
    size: {config.page_size};
    margin-top: {config.margin_top};
    margin-bottom: {config.margin_bottom};
    margin-left: {config.margin_left};
    margin-right: {config.margin_right};
}}

body {{
    font-family: {config.font_family};
    font-size: {config.font_size};
    line-height: 1.6;
    color: #333;
}}

/* Headers */
h1 {{
    font-size: 2em;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
    font-weight: bold;
    border-bottom: 2px solid #eaecef;
    padding-bottom: 0.3em;
}}

h2 {{
    font-size: 1.5em;
    margin-top: 0.83em;
    margin-bottom: 0.83em;
    font-weight: bold;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3em;
}}

h3 {{
    font-size: 1.17em;
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
}}

h4 {{
    font-size: 1em;
    margin-top: 1.33em;
    margin-bottom: 1.33em;
    font-weight: bold;
}}

h5 {{
    font-size: 0.83em;
    margin-top: 1.67em;
    margin-bottom: 1.67em;
    font-weight: bold;
}}

h6 {{
    font-size: 0.67em;
    margin-top: 2.33em;
    margin-bottom: 2.33em;
    font-weight: bold;
    color: #6a737d;
}}

/* Paragraphs */
p {{
    margin-top: 0;
    margin-bottom: 16px;
}}

/* Code blocks */
pre {{
    background-color: #f6f8fa;
    border-radius: 3px;
    padding: 16px;
    overflow-x: auto;
    font-family: {config.code_font};
    font-size: 85%;
    line-height: 1.45;
    margin-bottom: 16px;
}}

code {{
    font-family: {config.code_font};
    font-size: 85%;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}}

pre code {{
    background-color: transparent;
    padding: 0;
}}

/* Tables */
table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}}

table th {{
    font-weight: bold;
    background-color: #f6f8fa;
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
    text-align: left;
}}

table td {{
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
}}

table tr:nth-child(2n) {{
    background-color: #f6f8fa;
}}

/* Lists */
ul, ol {{
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 2em;
}}

li {{
    margin-bottom: 0.25em;
}}

li > p {{
    margin-bottom: 0;
}}

/* Blockquotes */
blockquote {{
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}}

blockquote > :first-child {{
    margin-top: 0;
}}

blockquote > :last-child {{
    margin-bottom: 0;
}}

/* Horizontal rules */
hr {{
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #e1e4e8;
    border: 0;
}}

/* Links */
a {{
    color: #0366d6;
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* Strong and emphasis */
strong {{
    font-weight: bold;
}}

em {{
    font-style: italic;
}}
"""
