from importlib.metadata import version as get_package_version


def _version_getter() -> tuple[str, str]:
    v = get_package_version("game_state").split(".")
    level_types = {"a": "alpha", "b": "beta"}
    level = level_types.get(v[-1], "final")
    return f"{v[0]}.{v[1]}", f"{v[0]}.{v[1]}.{v[2]} - {level}"


# -- Project information
project = "Game-State"
copyright = "2024-present, Jiggly Balls"
author = "Jiggly Balls"

# version = f"{version_info.major}.{version_info.minor}"
# release = f"{version_info.major}.{version_info.minor}.{version_info.patch} - {version_info.release_level}"

version, release = _version_getter()

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
always_document_param_types = True
toc_object_entries_show_parents = "hide"
autosectionlabel_prefix_document = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

templates_path = ["_templates"]

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
