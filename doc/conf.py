# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from sys                 import path as sys_path
from os                  import environ
from os.path             import abspath
from pathlib             import Path
from textwrap            import dedent
from typing              import Any, Optional as Nullable

from sphinx.application  import Sphinx

from pyTooling.Packaging import extractVersionInformation

# ==============================================================================
# Project configuration
# ==============================================================================
githubNamespace = "VHDL"
githubProject = pythonProject = "VHDLDomain"
directoryName = pythonProject.replace('.', '/')


# ==============================================================================
# Project paths
# ==============================================================================
ROOT = Path(__file__).resolve().parent

sys_path.insert(0, abspath("."))
sys_path.insert(0, abspath(".."))
sys_path.insert(0, abspath(f"../{directoryName}"))


# ==============================================================================
# Project information and versioning
# ==============================================================================
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
packageInformationFile = Path(f"../{directoryName}/__init__.py")
versionInformation = extractVersionInformation(packageInformationFile)

project =   pythonProject
author =    versionInformation.Author
copyright = versionInformation.Copyright
version =   ".".join(versionInformation.Version.split(".")[:2])  # e.g. 2.3    The short X.Y version.
release =   versionInformation.Version


# ==============================================================================
# Miscellaneous settings
# ==============================================================================
# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
	"_build",
	"_theme",
	"Thumbs.db",
	".DS_Store",
	"StopWatch"
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "manni"


# ==============================================================================
# Restructured Text settings
# ==============================================================================
prologPath = Path("prolog.inc")
try:
	with prologPath.open("r", encoding="utf-8") as fileHandle:
		rst_prolog = fileHandle.read()
except Exception as ex:
	print(f"[ERROR:] While reading '{prologPath}'.")
	print(ex)
	rst_prolog = ""


# ==============================================================================
# Options for HTML output
# ==============================================================================
html_theme = "sphinx_rtd_theme"
html_theme_options = {
	"logo_only": True,
	"vcs_pageview_mode": 'blob',
	"navigation_depth": -1,
}
html_css_files = [
	'css/override.css',
]

# GoatCounter counts the page views of the published documentation, which is built on GitHub Actions.
if environ.get("GITHUB_ACTIONS") == "true":
	html_js_files = [
		("https://gc.zgo.at/count.js", {"async": "async", "data-goatcounter": "https://vhdl.goatcounter.com/count"}),
	]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = str(Path(html_static_path[0]) / "logo.svg")
html_favicon = str(Path(html_static_path[0]) / "favicon.svg")

# Output file base name for HTML help builder.
htmlhelp_basename = f"{project}Doc"

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
html_last_updated_fmt = "%d.%m.%Y"

# ==============================================================================
# Python settings
# ==============================================================================
modindex_common_prefix = [
	f"{project}."
]

# ==============================================================================
# Options for LaTeX / PDF output
# ==============================================================================
latex_engine = "lualatex"
latex_use_xindy = False
latex_elements = {
	"papersize":   "a4paper",      # The paper size ('letterpaper' or 'a4paper').
	"pointsize":   "10pt",         # The font size ('10pt', '11pt' or '12pt').
	"inputenc":    "",             # Let LuaLaTeX handle input encoding
	"utf8extra":   "",
	"polyglossia": "",
	"babel":      r"\usepackage[english]{babel}",
	"fontenc":    r"\usepackage{fontspec}",  # Disable the default T1 font encoding (Essential for LuaLaTeX)
	"fontpkg":    dedent("""\
		\\usepackage[fontfamily=libertinus]{pytooling}
	"""),
	"passoptionstopackages": dedent("""\
		\\PassOptionsToPackage{verbatimvisiblespace=\\ }{sphinx}
	"""),
# "sphinxsetup": "verbatimvisiblespace=\\textvisiblespace"
# "figure_align": "htbp",     # Latex figure (float) alignment
	"makeindex":  r"\usepackage[columns=1]{idxlayout}\makeindex",
	"printindex": r"\def\twocolumn[#1]{#1}\printindex",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
	( master_doc,
		f"{pythonProject}.tex",
		f"The {pythonProject.replace("_", r"\_")} Documentation",
		 "Patrick Lehmann",
		 "manual"
	),
]


# ==============================================================================
# Extensions
# ==============================================================================
extensions = [
# Standard Sphinx extensions
	"sphinx.ext.autodoc",
	"sphinx.ext.extlinks",
	"sphinx.ext.intersphinx",
	"sphinx.ext.inheritance_diagram",
	"sphinx.ext.todo",
	"sphinx.ext.graphviz",
	"sphinx.ext.mathjax",
	"sphinx.ext.ifconfig",
	"sphinx.ext.viewcode",
# SphinxContrib extensions
	"sphinxcontrib.mermaid",
# Other extensions
	"sphinx_design",
	"sphinx_copybutton",
	"sphinx_autodoc_typehints",
	"autoapi.sphinx",
# User defined extensions
	"pyTooling.Sphinx",
	"VHDLDomain",
]


# ==============================================================================
# Sphinx.Ext.InterSphinx
# ==============================================================================
intersphinx_mapping = {
	"python":       ("https://docs.python.org/3", None),
	"pyTool":       ("https://pyTooling.github.io/pyTooling/", None),
	"pyToolSphinx": ("https://pyTooling.github.io/pyTooling.Sphinx/", None),
	"sphinx":       ("https://www.sphinx-doc.org/en/master", None),
	"vasg":         ("https://IEEE-P1076.gitlab.io/", None),
	"vhdl":         ("https://VHDL.github.io/pyVHDLModel/", None),
	"ghdl":         ("https://GHDL.github.io/ghdl/", None),
}


# ==============================================================================
# Suppressed warnings
# ==============================================================================
# ExtendedType adds '__getstate__'/'__setstate__' to every class with slots. sphinx_autodoc_typehints can't read their
# type hints, as they are created by the meta-class rather than defined in the class, and warns once per method.
suppress_warnings = [
	"sphinx_autodoc_typehints.local_function",
]


# ==============================================================================
# Sphinx.Ext.AutoDoc
# ==============================================================================
# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration
#autodoc_default_options = {
#	"private-members": True,
#	"special-members": True,
#	"inherited-members": True,
#	"exclude-members": "__weakref__"
#}
#autodoc_class_signature = "separated"
autodoc_member_order = "bysource"       # alphabetical, groupwise, bysource
autodoc_typehints = "both"
#autoclass_content = "both"


# ==============================================================================
# Sphinx.Ext.ExtLinks
# ==============================================================================
extlinks = {
	"gh":          ("https://GitHub.com/%s", "%s"),
	"ghissue":     (f"https://GitHub.com/{githubNamespace}/{project}/issues/%s", "issue #%s"),
	"ghpull":      (f"https://GitHub.com/{githubNamespace}/{project}/pull/%s", "pull request #%s"),
	"ghsrc":       (f"https://GitHub.com/{githubNamespace}/{project}/blob/main/%s", None),
	"pypi":        ("https://PyPI.org/project/%s", "%s"),
	"wiki":        ("https://en.wikipedia.org/wiki/%s", None),
}


# ==============================================================================
# Sphinx.Ext.Graphviz
# ==============================================================================
graphviz_output_format = "svg"


# ==============================================================================
# SphinxContrib.Mermaid
# ==============================================================================
mermaid_params = [
	'--backgroundColor', 'transparent',
]
mermaid_verbose = True


# ==============================================================================
# Sphinx.Ext.Inheritance_Diagram
# ==============================================================================
inheritance_node_attrs = {
#	"shape": "ellipse",
#	"fontsize": 14,
#	"height": 0.75,
	"color": "dodgerblue1",
	"style": "filled"
}


# ==============================================================================
# Sphinx.Ext.ToDo
# ==============================================================================
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
todo_link_only = True


# ==============================================================================
# pyTooling.Sphinx - reports of domain 'report'
# ==============================================================================
pyTooling_Unittest_Testsuites = {
	"src": {
		"xml_report":  "../report/unit/unittest.xml",
		"pages":       "unittests/src",
	},
}
pyTooling_CodeCoverage_Packages = {
	"src": {
		"name":        f"{pythonProject}",
		"json_report": "../report/coverage/coverage.json",
		"sources":     "..",
		"pages":       "coverage/src",
		"fail_below":  80,
		"levels":      "default"
	},
}
pyTooling_DocCoverage_Packages = {
	"src": {
		"name":       f"{pythonProject}",
		"directory":  f"../{directoryName}",
		"pages":      "doccoverage/src",
		"fail_below": 80,
		"levels":     "default"
	},
}


# ==============================================================================
# pyTooling.Sphinx - abbreviations
# ==============================================================================
pyTooling_Abbreviation_ShowSummary = True


# ==============================================================================
# pyTooling.Sphinx - dependency tables
# ==============================================================================
pyTooling_Dependency_Requirements = {
	"package":       {"file": "../requirements.txt"},
	"unittest":      {"file": "../tests/unit/requirements.txt"},
	"typing":        {"file": "../tests/typing/requirements.txt"},
	"documentation": {"file": "requirements.txt"},
}
pyTooling_Dependency_PackageOverrides = "Dependency.PackageOverrides.yaml"


# ==============================================================================
# pyTooling.Sphinx - external link icons
# ==============================================================================
pyTooling_ExternalLink_Icons = "all"


# ==============================================================================
# VHDLDomain
# ==============================================================================
vhdl_designs = {
#	"StopWatch": {
#		"directory": "../examples/StopWatch",
#		"libraries": {
#			"lib_Utilities": ["Utilities.pkg.vhdl", "Utilities.ctx.vhdl", "Counter.vhdl", "sync_Bits.vhdl", "Debouncer.vhdl"],
#			"lib_StopWatch": [
#				"StopWatch.pkg.vhdl", "StopWatch.ctx.vhdl", "seg7_Encoder.vhdl", "seg7_Display.vhdl", "seg7_Display.cfg.vhdl",
#				"StopWatch.vhdl", "toplevel.vhdl"
#			],
#		},
#	},
}


# ==============================================================================
# Sphinx_Design
# ==============================================================================
# sd_fontawesome_latex = True


# ==============================================================================
# AutoAPI.Sphinx
# ==============================================================================
autoapi_modules = {
	f"{project}":  {
		"template": "package",
		"output":   project,
		"override": True
	}
}

# sub-packages are directories, modules are files - both get the module template, which documents their members
for module in Path(f"../{project.replace('.', '/')}").iterdir():
	if module.is_dir() and module.name != "__pycache__":
		name = module.name
	elif module.suffix == ".py" and module.name != "__init__.py":
		name = module.stem
	else:
		continue

	print(f"Adding module rule for '{project}.{name}'")
	autoapi_modules[f"{project}.{name}"] = {
		"template": "module",
		"output":   project,
		"override": True
	}


# ==============================================================================
# Sphinx.Ext.AutoDoc - skipped members
# ==============================================================================
def skipForeignMembers(
	app: Sphinx,
	what: str,
	name: str,
	obj: Any,
	skip: bool,
	options: Any
) -> Nullable[bool]:
	"""
	Skip a member inherited from :mod:`docutils`, :mod:`sphinx`, :mod:`enum` or a built-in type, e.g. :class:`str`.

	``:inherited-members:`` in the module template would render each of them: the methods of Sphinx' domain, directive,
	index and role classes, which the classes of :mod:`VHDLDomain` derive from, are documented in docutils' or Sphinx'
	own format, with an error per malformed reference; and a :class:`~pyTooling.Common.StringEnum` would list every
	method of a string.

	:param app:     The Sphinx application.
	:param what:    Kind of the object the member belongs to, e.g. ``class``.
	:param name:    Name of the member.
	:param obj:     The member.
	:param skip:    Whether autodoc skips the member already.
	:param options: The options of the autodoc directive.
	:returns:       ``True`` to skip the member, ``None`` to leave the decision to autodoc.
	"""
	module = getattr(obj, "__module__", None)
	if module is not None and module.partition(".")[0] in ("docutils", "sphinx", "enum", "builtins"):
		return True
	elif getattr(obj, "__objclass__", None) is str:
		return True

	return None


def setup(app: Sphinx) -> None:
	"""
	Connect the handlers above.

	:param app: The Sphinx application.
	"""
	app.connect("autodoc-skip-member", skipForeignMembers)
