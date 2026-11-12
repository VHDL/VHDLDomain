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
The syntax of documentation comments: reStructuredText, CommonMark or GitHub-flavoured Markdown.

``vhdl_doc_syntax`` and the option ``:doc-syntax:`` of the design-unit directives name the syntax, a member of
:class:`DocumentationSyntax`. A comment in reStructuredText is parsed as a Python doc-string is; a comment in Markdown
is converted by a :class:`MarkdownConverter`: markdown-it-py parses it, and pyTooling.Sphinx'
:class:`~pyTooling.Sphinx.Markdown.MarkdownTranslator` translates the tokens into docutils nodes - a heading into a
topic or a rubric, raw HTML element by element.

.. attention::

   Packages ``markdown_it`` and ``mdit_py_plugins`` are imported when a :class:`MarkdownConverter` is created, not when
   this module is imported. They are installed with the extra ``markdown``.
"""
from __future__                import annotations

from typing                    import TYPE_CHECKING

from docutils                  import nodes
from docutils.nodes            import Node

from pyTooling.Common          import StringEnum, getFullyQualifiedName
from pyTooling.Decorators      import export, readonly
from pyTooling.Exceptions      import MissingDependencyError
from pyTooling.MetaClasses     import ExtendedType
from pyTooling.Sphinx.Markdown import MarkdownTranslator

if TYPE_CHECKING:  # pragma: no cover
	from markdown_it             import MarkdownIt


@export
class DocumentationSyntax(StringEnum):
	"""
	The syntax of documentation comments, as ``vhdl_doc_syntax`` and option ``:doc-syntax:`` state it.
	"""

	ReST =     "rest"      #: reStructuredText, as a Python doc-string.
	Markdown = "markdown"  #: CommonMark: markdown-it-py's preset ``commonmark``.
	GFM =      "gfm"       #: GitHub-flavoured Markdown: CommonMark, tables, strikethrough, task lists, alerts, footnotes.

	DEFAULT =  ReST        #: Without a value, a comment is reStructuredText.


@export
class MarkdownConverter(metaclass=ExtendedType, slots=True):
	"""
	A converter of documentation comments in Markdown - CommonMark or GitHub-flavoured - into docutils nodes.

	The converter is the one :class:`~pyTooling.Sphinx.Markdown.MarkdownTranslator` asks for the text between the
	Markdown: a comment's text stays text - GitHub's references, e.g. ``#12`` and ``@user``, are not linked, and emoji
	stay their shortcodes -, and a line break in a paragraph is a space, as in CommonMark.
	"""

	_syntax: DocumentationSyntax  #: The Markdown syntax, ``markdown`` or ``gfm``.
	_parser: MarkdownIt           #: The Markdown parser.

	def __init__(self, syntax: DocumentationSyntax) -> None:
		"""
		Initializes a converter for a Markdown syntax.

		:param syntax:                  The Markdown syntax.
		:raises ValueError:             If parameter 'syntax' is ``None``.
		:raises TypeError:              If parameter 'syntax' is not of type :class:`DocumentationSyntax`.
		:raises ValueError:             If parameter 'syntax' is no Markdown syntax.
		:raises MissingDependencyError: If the extra ``markdown`` isn't installed. |br|
		                                Install VHDLDomain with extra ``VHDLDomain[markdown]``.
		"""
		if syntax is None:
			raise ValueError("Parameter 'syntax' is None.")
		elif not isinstance(syntax, DocumentationSyntax):
			ex = TypeError("Parameter 'syntax' is not of type 'DocumentationSyntax'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(syntax)}'.")
			raise ex
		elif syntax is DocumentationSyntax.ReST:
			ex = ValueError("Parameter 'syntax' is no Markdown syntax.")
			ex.add_note(f"Got value '{syntax}'.")
			raise ex

		try:
			from markdown_it         import MarkdownIt
		except ImportError as cause:
			ex = MissingDependencyError(dependency="markdown-it-py")
			ex.add_note("Or install VHDLDomain with extra 'VHDLDomain[markdown]'.")
			raise ex from cause

		parser = MarkdownIt("commonmark", {"html": True})
		if syntax is DocumentationSyntax.GFM:
			try:
				from mdit_py_plugins.gfm import gfm_plugin
			except ImportError as cause:
				ex = MissingDependencyError(dependency="mdit-py-plugins")
				ex.add_note("Or install VHDLDomain with extra 'VHDLDomain[markdown]'.")
				raise ex from cause

			parser.use(gfm_plugin)

		self._syntax = syntax
		self._parser = parser

	@readonly
	def Syntax(self) -> DocumentationSyntax:
		"""
		Read-only property to access the Markdown syntax (:attr:`_syntax`).

		:returns: The syntax, ``markdown`` or ``gfm``.
		"""
		return self._syntax

	@readonly
	def LineBreaks(self) -> bool:
		"""
		Read-only property to return whether a line break in a paragraph is written as a line break.

		:returns: ``False``: a line break in a paragraph is a space, as in CommonMark.
		"""
		return False

	def Convert(self, markdown: str, document: nodes.document, location: str) -> list[Node]:
		"""
		Convert a documentation comment in Markdown into docutils nodes.

		The nodes are body elements a directive returns; a heading becomes a topic or a rubric, never a section. The
		translator warns about Markdown without docutils counterpart, with type ``github`` and subtype ``markdown``.

		:param markdown: The comment's text, without the comment markers.
		:param document: The document the nodes are put into.
		:param location: Location the warnings are reported at, e.g. ``index.rst:12``.
		:returns:        The nodes.
		"""
		translator = MarkdownTranslator(self, document, location)  # type: ignore[arg-type]
		return translator.Translate(self._parser.parse(markdown))

	def Parse(self, text: str, references: bool = True) -> list[Node]:
		"""
		Write a text between the Markdown as text, for :class:`~pyTooling.Sphinx.Markdown.MarkdownTranslator`.

		A documentation comment has no GitHub references and no emoji: the text is one text node.

		:param text:       The text.
		:param references: Optional, whether GitHub's references would be linked; a documentation comment has none.
		                   Default: ``True``.
		:returns:          The text node.
		"""
		return [nodes.Text(text)]
