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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for the generated pages of a design: a page per library and design unit."""
from pathlib                import Path
from typing                 import ClassVar

from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document
from pyVHDLModel.DesignUnit import Entity

from VHDLDomain             import VHDLDomain
from VHDLDomain.Pages       import DesignPages

from tests.unit.DesignUnit  import CONF, DesignUnitProject


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: The warning of the generated page of entity ``Wide``, whose port default pyVHDLModel can't write yet. The page's
#: source is the Sphinx source directory, as the hand-built design's files don't exist.
WIDE = "/src:4: WARNING: vhdl:entity: pyVHDLModel can't write a 'FunctionCall' yet, written as '...'. [vhdl.writer]"


class GeneratedPages(DesignUnitProject):
	"""Design ``Demo`` with pages below ``designs/Demo``, listed by the ``vhdl:design`` of document ``index``."""

	_CONF: ClassVar[str] = CONF.replace('AddDesign("Demo", demo())', 'AddDesign("Demo", demo(), "designs/Demo")')

	def _buildDesign(self, index: str = "", **pages: str) -> VHDLDomain:
		"""
		Build the project, the document ``index`` holding ``vhdl:design``.

		:param index: Text following ``vhdl:design`` in the document ``index``.
		:param pages: Further documents by name.
		:returns:     The domain after the build.
		"""
		app = self._build({"index": f"Index\n#####\n\n.. vhdl:design:: Demo\n\n{index}", **pages})

		return app.env.get_domain("vhdl")

	def test_Pages(self) -> None:
		self._buildDesign()

		self.assertEqual([WIDE], self._warningLines())
		for docName, text in (
			("designs/Demo/lib_A",           '<span class="pre">Utilities</span>'),
			("designs/Demo/lib_A/Counter",   "<p>A counter.</p>"),
			("designs/Demo/lib_A/Utilities", "<p>Utilities.</p>"),
			("designs/Demo/lib_A/ctx",       "IEEE"),
			("designs/Demo/lib_A/cfg",       "Configures entity"),
		):
			with self.subTest(document=docName):
				self.assertIn(text, self._html(docName))

	def test_Objects(self) -> None:
		domain = self._buildDesign()

		for key, docName in (
			(("library",   "demo.lib_a"),                         "designs/Demo/lib_A"),
			(("entity",    "demo.lib_a.counter"),                 "designs/Demo/lib_A/Counter"),
			(("port",      "demo.lib_a.counter.clock"),           "designs/Demo/lib_A/Counter"),
			(("function",  "demo.lib_a.utilities.to_index(natural)"), "designs/Demo/lib_A/Utilities"),
		):
			with self.subTest(key=key):
				self.assertEqual(docName, domain.Objects[key][0])

	def test_References(self) -> None:
		self._buildDesign(":vhdl:ent:`Counter` :vhdl:lib:`lib_A`\n")

		self.assertEqual([WIDE], self._warningLines())
		html = self._html("index")
		self.assertIn('href="designs/Demo/lib_A/Counter.html#vhdl-entity-demo.lib_a.counter"', html)
		self.assertIn('href="designs/Demo/lib_A.html#vhdl-library-demo.lib_a"', html)

	def test_Navigation(self) -> None:
		"""The library pages are below the design's document, the unit pages below their library's."""
		self._buildDesign()

		self.assertIn('href="designs/Demo/lib_A.html"', self._html("index"))
		library = self._html("designs/Demo/lib_A")
		self.assertIn('href="lib_A/ctx.html" title="ctx (lib_A)"\n             accesskey="N">next</a>', library)

	def test_Duplicate(self) -> None:
		"""A directive describing an object of a generated page again is warned about."""
		self._buildDesign(page="Page\n####\n\n.. vhdl:entity:: lib_A.Counter\n   :design: Demo\n")

		self.assertIn(
			"/src/page.rst:4: WARNING: Duplicate description of vhdl:entity 'Demo.lib_A.Counter', other instance in "
			"'designs/Demo/lib_A/Counter'. [vhdl.duplicate]",
			self._warningLines()
		)


class Libraries(Testcase):
	"""The pages of a design, without Sphinx."""

	def test_DocNames(self) -> None:
		design =   Design("Demo")
		document = Document(Path("a.vhdl"))
		document._AddDesignUnit(Entity("Counter"))
		document._AddDesignUnit(Entity("Adder"))
		design.AddDocument(document, design.GetLibrary("lib_A"))

		pages = DesignPages("Demo", design, "designs/Demo", Path("."))

		self.assertEqual(("designs/Demo/lib_A", "designs/Demo/lib_A/Adder", "designs/Demo/lib_A/Counter"), pages.DocNames)

	def test_PredefinedLibraries(self) -> None:
		"""The predefined libraries get no pages."""
		design = Design("Demo")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		document = Document(Path("a.vhdl"))
		document._AddDesignUnit(Entity("Counter"))
		design.AddDocument(document, design.GetLibrary("lib_A"))

		pages = DesignPages("Demo", design, "designs/Demo", Path("."))

		self.assertEqual(("designs/Demo/lib_A", "designs/Demo/lib_A/Counter"), pages.DocNames)
