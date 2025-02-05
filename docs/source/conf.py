# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "Game-State"
copyright = "2024-present, Jiggly Balls"
author = "Jiggly Balls"


version = "1.0"
release = "1.0.0"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

toc_object_entries = False

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "furo"
html_theme_options = {
    "top_of_page_buttons": ["view", "edit"],
}

# -- Options for EPUB output
epub_show_urls = "footnote"
