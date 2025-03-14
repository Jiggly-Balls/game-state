import os
import sys

sys.path.insert(0, os.path.abspath("../../src/"))

# from src.game_state import version_info

# -- Project information
project = "Game-State"
copyright = "2024-present, Jiggly Balls"
author = "Jiggly Balls"

# version = f"{version_info.major}.{version_info.minor}"
# release = f"{version_info.major}.{version_info.minor}.{version_info.patch} - {version_info.releaselevel}"


version = "1.1"
release = "1.1.0 - final"

# -- General configuration
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

toc_object_entries = False
always_document_param_types = True
toc_object_entries_show_parents = "hide"
autosectionlabel_prefix_document = True
autosummary_generate = True
autosummary_generate_overwrite = False
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"
autoclass_content = "both"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

templates_path = ["_templates"]
modindex_common_prefix = ["src."]

# -- Options for HTML output
html_title = f"{project} v{version} Documentation"
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/Jiggly-Balls/game-state",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "top_of_page_buttons": ["view", "edit"],
}
htmlhelp_basename = "game_state_doc"

# -- Options for EPUB output
epub_show_urls = "footnote"
