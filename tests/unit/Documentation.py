# ==================================================================================================================== #
# __     ___   _ ____  _     ____                        _                                                             #
# \ \   / / | | |  _ \| |   |  _ \  ___  _ __ ___   __ _(_)_ __                                                        #
#  \ \ / /| |_| | | | | |   | | | |/ _ \| '_ ` _ \ / _` | | '_ \                                                       #
#   \ V / |  _  | |_| | |___| |_| | (_) | | | | | | (_| | | | | |                                                      #
#    \_/  |_| |_|____/|_____|____/ \___/|_| |_| |_|\__,_|_|_| |_|                                                      #
#                                                                                                                      #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Unit tests for the syntax of documentation comments: reStructuredText, CommonMark or GitHub-flavoured Markdown.

The Markdown tests need the extra ``markdown`` (markdown-it-py, mdit-py-plugins); without it, they are skipped.
"""
from importlib.util           import find_spec
from sys                      import modules
from textwrap                 import dedent
from typing                   import ClassVar
from unittest                 import skipUnless
from unittest.mock            import patch

from docutils                 import nodes
from docutils.frontend        import get_default_settings
from docutils.parsers.rst     import Parser
from docutils.utils           import new_document
from sphinx.errors            import ConfigError

from pyTooling.Exceptions     import MissingDependencyError
from pyTooling.Testing        import Testcase

from VHDLDomain.Directive     import VHDLDirective
from VHDLDomain.Documentation import DocumentationSyntax, MarkdownConverter

from tests.unit.Domain        import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


MARKDOWN = find_spec("markdown_it") is not None and find_spec("mdit_py_plugins") is not None
"""Whether the extra ``markdown`` is installed."""

#: A :file:`conf.py` adding design ``Demo``: library ``lib_A`` with an entity documented in GitHub-flavoured Markdown,
#: and one in a syntax both reStructuredText and Markdown read.
CONF = dedent("""\
	from pathlib                import Path

	from pyVHDLModel            import Design, Document
	from pyVHDLModel.Base       import Mode
	from pyVHDLModel.DesignUnit import Entity
	from pyVHDLModel.Interface  import PortSimpleSignalInterfaceItem
	from pyVHDLModel.Name       import SimpleName
	from pyVHDLModel.Symbol     import SimpleSubtypeSymbol

	extensions = ["pyTooling.Sphinx", "VHDLDomain"]


	def demo():
		design =   Design("Demo")
		document = Document(Path("a.vhdl"))
		document._AddDesignUnit(Entity(
			"Display",
			portItems=[
				PortSimpleSignalInterfaceItem(
					("Clock", ), Mode.In, SimpleSubtypeSymbol(SimpleName("std_logic")), documentation="-- The *clock*."
				),
			],
			documentation=(
				"-- **Bold** and `code`, #12, @user.\\n--\\n-- | A | B |\\n-- |---|---|\\n-- | 1 | 2 |\\n--\\n-- - [x] done"
			)
		))
		document._AddDesignUnit(Entity("Plain", documentation="-- `code` and *emphasis*."))
		design.AddDocument(document, design.GetLibrary("lib_A"))

		return design


	def addDesigns(app):
		app.env.get_domain("vhdl").AddDesign("Demo", demo())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")


PAGE = "Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n.. vhdl:library:: lib_A\n   :no-index:\n\n"
"""The page's beginning, in design ``Demo`` and library ``lib_A``."""


class Converter(Testcase):
	_document: nodes.document  #: The document the nodes are put into.

	def setUp(self) -> None:
		self._document = new_document("test", get_default_settings(Parser))

	def test_Checks(self) -> None:
		with self.assertRaises(ValueError):
			MarkdownConverter(None)

		with self.assertRaises(TypeError):
			MarkdownConverter("markdown")

		with self.assertRaises(ValueError) as context:
			MarkdownConverter(DocumentationSyntax.ReST)

		self.assertEqual("Parameter 'syntax' is no Markdown syntax.", str(context.exception))

	@skipUnless(MARKDOWN, "Extra 'markdown' isn't installed.")
	def test_CommonMark(self) -> None:
		"""CommonMark has no tables: the table is a paragraph; a line break in a paragraph is a space."""
		converter = MarkdownConverter(DocumentationSyntax.Markdown)
		result =    converter.Convert("**Bold** and `code`.\nNext line.\n\n| A |\n|---|\n| 1 |", self._document, "loc")

		self.assertEqual(DocumentationSyntax.Markdown, converter.Syntax)
		self.assertFalse(converter.LineBreaks)
		self.assertEqual(2, len(result))
		self.assertEqual("Bold and code.\nNext line.", result[0].astext())
		self.assertEqual(1, len(list(result[0].findall(nodes.strong))))
		self.assertEqual(1, len(list(result[0].findall(nodes.literal))))
		self.assertIsInstance(result[1], nodes.paragraph)

	@skipUnless(MARKDOWN, "Extra 'markdown' isn't installed.")
	def test_GFM(self) -> None:
		"""GitHub-flavoured Markdown has tables and task lists; GitHub's references stay text."""
		converter = MarkdownConverter(DocumentationSyntax.GFM)
		markdown =  "See #12, @user and 1a2b3c4.\n\n| A |\n|---|\n| 1 |\n\n- [ ] open"
		result =    converter.Convert(markdown, self._document, "loc")

		self.assertEqual(3, len(result))
		self.assertEqual("See #12, @user and 1a2b3c4.", result[0].astext())
		self.assertEqual([], list(result[0].findall(nodes.reference)))
		self.assertIsInstance(result[1], nodes.table)
		self.assertIsInstance(result[2], nodes.bullet_list)
		self.assertIn("github-task-list", result[2]["classes"])

	def test_MissingDependency(self) -> None:
		with patch.dict(modules, {"markdown_it": None}):
			with self.assertRaises(MissingDependencyError) as context:
				MarkdownConverter(DocumentationSyntax.Markdown)

		self.assertEqual("Optional dependency 'markdown-it-py' not installed.", str(context.exception))
		self.assertEqual(
			["Install 'markdown-it-py'.", "Or install VHDLDomain with extra 'VHDLDomain[markdown]'."],
			context.exception.__notes__
		)


class Directive(Project):
	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	def setUp(self) -> None:
		super().setUp()
		VHDLDirective._markdownConverters.clear()

	def tearDown(self) -> None:
		VHDLDirective._markdownConverters.clear()
		super().tearDown()

	def test_Default(self) -> None:
		"""By default, a documentation comment is reStructuredText: single backquotes are interpreted text."""
		self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n"})

		self.assertEqual([], self._warningLines())
		self.assertIn("<p><cite>code</cite> and <em>emphasis</em>.</p>", self._html("page"))

	@skipUnless(MARKDOWN, "Extra 'markdown' isn't installed.")
	def test_Configuration(self) -> None:
		"""With ``vhdl_doc_syntax = "gfm"``, every comment is GitHub-flavoured Markdown, also an item's."""
		self._build({"page": f"{PAGE}.. vhdl:entity:: Display\n"}, vhdl_doc_syntax="gfm")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for text in (
			'<p><strong>Bold</strong> and <code class="docutils literal notranslate"><span class="pre">code</span></code>, '
			'#12, &#64;user.</p>',
			'<table class="github-table docutils align-default">',
			'<ul class="github-task-list simple">',
			'<strong>Clock</strong> : <em>in std_logic</em> – The <em>clock</em>.</p>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	@skipUnless(MARKDOWN, "Extra 'markdown' isn't installed.")
	def test_Option(self) -> None:
		"""Option ``:doc-syntax:`` overrides ``vhdl_doc_syntax``; CommonMark has no tables."""
		self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n   :doc-syntax: markdown\n\n"
			".. vhdl:entity:: Display\n   :doc-syntax: markdown\n"})

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIn(
			'<p><code class="docutils literal notranslate"><span class="pre">code</span></code> and <em>emphasis</em>.</p>',
			html
		)
		self.assertNotIn("<table", html)

	def test_MissingDependency(self) -> None:
		"""Without the extra ``markdown``, a comment in Markdown is text, warned about once."""
		with patch.dict(modules, {"markdown_it": None}):
			self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n\n.. vhdl:entity:: Display\n"}, vhdl_doc_syntax="gfm")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:entity: Documentation comments in 'gfm' written as text: Optional "
				"dependency 'markdown-it-py' not installed. Install 'markdown-it-py'. Or install VHDLDomain with extra "
				"'VHDLDomain[markdown]'. [vhdl.markdown]"
			],
			self._warningLines()
		)
		self.assertIn("<p>`code` and *emphasis*.</p>", self._html("page"))

	def test_Invalid(self) -> None:
		self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n   :doc-syntax: asciidoc\n"})

		self.assertEqual(
			[
				"/src/page.rst:10: ERROR: Error in \"vhdl:entity\" directive:",
				"invalid option value: (option: \"doc-syntax\"; value: 'asciidoc')",
				"'asciidoc' is not a valid DocumentationSyntax..",
			],
			self._warningLines()[:3]
		)

	def test_InvalidConfiguration(self) -> None:
		with self.assertRaises(ConfigError) as context:
			self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n"}, vhdl_doc_syntax="asciidoc")

		self.assertEqual(
			"conf.py: vhdl_doc_syntax: 'asciidoc' is not a syntax of documentation comments.", str(context.exception)
		)
		self.assertEqual(["Allowed values: rest, markdown, gfm."], context.exception.__notes__)


class WithoutExtension(Project):
	_CONF: ClassVar[str] = CONF.replace(
		'extensions = ["pyTooling.Sphinx", "VHDLDomain"]', 'extensions = ["VHDLDomain"]'
	)  #: The project's :file:`conf.py`, without extension ``pyTooling.Sphinx``.

	def test_Markdown(self) -> None:
		"""Without extension ``pyTooling.Sphinx``, a comment in Markdown is text, warned about once."""
		self._build({"page": f"{PAGE}.. vhdl:entity:: Plain\n\n.. vhdl:entity:: Display\n"}, vhdl_doc_syntax="gfm")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:entity: Documentation comments in 'gfm' written as text: Extension "
				"'pyTooling.Sphinx' isn't loaded. [vhdl.markdown]"
			],
			self._warningLines()
		)
		self.assertIn("<p>`code` and *emphasis*.</p>", self._html("page"))
