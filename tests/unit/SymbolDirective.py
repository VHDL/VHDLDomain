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
Unit tests for the directive ``vhdl:symbol`` and the visitors of its node.

The renderers are replaced by mocks: a test checks what the visitors write around the renderers' output.
"""
from sys                 import modules
from textwrap            import dedent
from types               import ModuleType
from typing              import ClassVar
from unittest.mock       import MagicMock, patch

from sphinx.testing.util import SphinxTestApp

from VHDLDomain.Symbol   import InterfaceSymbol

from tests.unit.Domain   import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: A :file:`conf.py` adding design ``Demo``: library ``lib_A`` with entities, a package and an architecture declaring
#: components, and library ``lib_B`` with an entity named as a component of package ``lib_B`` in ``lib_A``.
CONF = dedent("""\
	from pathlib                   import Path

	from pyVHDLModel               import Design, Document
	from pyVHDLModel.Base          import Direction, Mode, SimpleRange
	from pyVHDLModel.DesignUnit    import Architecture, Component, Entity, Package
	from pyVHDLModel.Expression    import FunctionCall, IntegerLiteral
	from pyVHDLModel.Interface     import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem
	from pyVHDLModel.Name          import SimpleName
	from pyVHDLModel.Symbol        import ConstrainedArraySubtypeSymbol, EntitySymbol, SimpleSubtypeSymbol

	extensions = ["VHDLDomain"]


	def subtype(name):
		return SimpleSubtypeSymbol(SimpleName(name))


	def adder(kind, name):
		return kind(
			name,
			portItems=[
				PortSimpleSignalInterfaceItem(("a", "b"), Mode.In, subtype("bit")),
				PortSimpleSignalInterfaceItem(("s", ), Mode.Out, subtype("bit")),
			]
		)


	def demo():
		design = Design("Demo")

		documentA = Document(Path("a.vhdl"))
		documentA._AddDesignUnit(Entity(
			"Counter",
			genericItems=[
				GenericConstantInterfaceItem(("MODULO", ), Mode.In, subtype("positive")),
				GenericConstantInterfaceItem(("BITS", ), Mode.In, subtype("natural"), IntegerLiteral(8)),
			],
			portItems=[
				PortSimpleSignalInterfaceItem(("Clock", "Reset_n"), Mode.In, subtype("std_logic")),
				PortSimpleSignalInterfaceItem(
					("Value", ), Mode.Out,
					ConstrainedArraySubtypeSymbol(
						SimpleName("unsigned"), [SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)]
					)
				),
			]
		))
		documentA._AddDesignUnit(Entity(
			"Wide", genericItems=[GenericConstantInterfaceItem(("N", ), Mode.In, subtype("natural"), FunctionCall())]
		))
		documentA._AddDesignUnit(Package("Components", declaredItems=[adder(Component, "Adder")]))
		documentA._AddDesignUnit(Package("lib_B", declaredItems=[adder(Component, "Adder")]))
		documentA._AddDesignUnit(Architecture(
			"rtl", EntitySymbol(SimpleName("Counter")), declaredItems=[adder(Component, "Sub")]
		))
		design.AddDocument(documentA, design.GetLibrary("lib_A"))

		documentB = Document(Path("b.vhdl"))
		documentB._AddDesignUnit(adder(Entity, "Adder"))
		design.AddDocument(documentB, design.GetLibrary("lib_B"))

		design.CreateDependencyGraph()
		design.LinkArchitectures()

		return design


	def addDesigns(app):
		app.env.get_domain("vhdl").AddDesign("Demo", demo())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")

#: The beginning of a page: design ``Demo`` and library ``lib_A`` are current.
HEAD = "Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n.. vhdl:library:: lib_A\n   :no-index:\n\n"


class SymbolProject(Project):
	"""A project with design ``Demo``, whose renderers are mocks."""

	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	_svgRenderer:  MagicMock  #: Mock of class ``SVGRenderer``.
	_tikzRenderer: MagicMock  #: Mock of class ``TikZRenderer``.

	def setUp(self) -> None:
		super().setUp()

		self._svgRenderer = MagicMock()
		self._svgRenderer.return_value.Render.side_effect = lambda symbol: f"<svg>{symbol.Name}</svg>"
		self._tikzRenderer = MagicMock()
		self._tikzRenderer.TIKZ_LIBRARIES = ("positioning", "arrows.meta")
		self._tikzRenderer.return_value.Render.side_effect = \
			lambda symbol: f"\\begin{{tikzpicture}}{symbol.Name}\\end{{tikzpicture}}"

		svgModule = ModuleType("VHDLDomain.Symbol.SVG")
		svgModule.SVGRenderer = self._svgRenderer  # type: ignore[attr-defined]
		tikzModule = ModuleType("VHDLDomain.Symbol.TikZ")
		tikzModule.TikZRenderer = self._tikzRenderer  # type: ignore[attr-defined]

		renderers = patch.dict(modules, {"VHDLDomain.Symbol.SVG": svgModule, "VHDLDomain.Symbol.TikZ": tikzModule})
		renderers.start()
		self.addCleanup(renderers.stop)

	def _symbols(self, body: str, builder: str = "html", **pages: str) -> SphinxTestApp:
		"""
		Build a page placing the body after ``vhdl:design`` and ``vhdl:library``, and further pages as given.

		:param body:    The page's body.
		:param builder: Optional, name of the builder. Default: ``"html"``.
		:param pages:   Further pages by name.
		:returns:       The Sphinx application after the build.
		"""
		return self._build({"page": f"{HEAD}{body}", **pages}, builder=builder)

	def _rendered(self) -> list[InterfaceSymbol]:
		"""
		Return the symbols the SVG renderer drew.

		:returns: The symbols, in drawing order.
		"""
		return [call.args[0] for call in self._svgRenderer.return_value.Render.call_args_list]


class Resolution(SymbolProject):
	def test_Entity(self) -> None:
		self._symbols(".. vhdl:symbol:: Counter\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(["Counter"], [symbol.Name for symbol in self._rendered()])

	def test_Entity_Library(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:symbol:: lib_A.Counter\n   :design: Demo\n"})

		self.assertEqual([], self._warningLines())
		self.assertEqual(["Counter"], [symbol.Name for symbol in self._rendered()])

	def test_PackageComponent(self) -> None:
		self._symbols(".. vhdl:symbol:: Components.Adder\n\n.. vhdl:symbol:: lib_A.Components.adder\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(["Adder", "Adder"], [symbol.Name for symbol in self._rendered()])

	def test_ArchitectureComponent(self) -> None:
		self._symbols(".. vhdl:symbol:: Counter.rtl.Sub\n\n.. vhdl:symbol:: lib_A.Counter.rtl.Sub\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(["Sub", "Sub"], [symbol.Name for symbol in self._rendered()])

	def test_Symbol(self) -> None:
		"""The symbol is converted from the entity's generics and ports."""
		self._symbols(".. vhdl:symbol:: Counter\n")

		symbol = self._rendered()[0]
		self.assertEqual(
			["MODULO", "BITS"], [parameter.Name for parameter in symbol.ParameterGroups[0].Parameters]
		)
		self.assertEqual(["Clock", "Reset_n", "Value"], [pin.Name for pin in symbol.PinGroups[0].Pins])

	def test_NoObject(self) -> None:
		"""A symbol describes no object of the domain."""
		app = self._symbols(".. vhdl:symbol:: Counter\n")

		self.assertEqual({}, app.env.get_domain("vhdl").Objects)


class Errors(SymbolProject):
	def test_NoLibrary(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:design:: Demo\n\n.. vhdl:symbol:: Counter\n"})

		self.assertEqual(
			[
				"/src/page.rst:6: WARNING: vhdl:symbol: No library: name it as '<library>.Counter' or place a 'vhdl:library' "
				"before it. [vhdl.library]"
			],
			self._warningLines()
		)

	def test_NoDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:symbol:: lib_A.Counter\n"})

		self.assertEqual(
			[
				"/src/page.rst:4: WARNING: vhdl:symbol: No design: give option ':design:' or place a 'vhdl:design' before it. "
				"[vhdl.design]"
			],
			self._warningLines()
		)

	def test_Unknown(self) -> None:
		self._symbols(".. vhdl:symbol:: Components.Counter\n\n.. vhdl:symbol:: lib_X.Counter\n")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:symbol: Entity or component 'Components.Counter' is not in design 'Demo'. "
				"[vhdl.symbol]",
				"/src/page.rst:12: WARNING: vhdl:symbol: Entity or component 'lib_X.Counter' is not in design 'Demo'. "
				"[vhdl.symbol]",
			],
			self._warningLines()
		)
		self.assertEqual([], self._rendered())

	def test_Ambiguous(self) -> None:
		"""``lib_B.Adder`` names a component of package ``lib_B`` in ``lib_A``, and entity ``Adder`` of ``lib_B``."""
		self._symbols(".. vhdl:symbol:: lib_B.Adder\n")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:symbol: 'lib_B.Adder' is ambiguous, candidates: component lib_A.lib_B.Adder, "
				"entity lib_B.Adder. [vhdl.symbol]"
			],
			self._warningLines()
		)
		self.assertEqual([], self._rendered())

	def test_Writer(self) -> None:
		"""What pyVHDLModel can't write yet is written as ``...``, and warned about."""
		self._symbols(".. vhdl:symbol:: Wide\n")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:symbol: pyVHDLModel can't write a 'FunctionCall' yet, written as '...'. "
				"[vhdl.writer]"
			],
			self._warningLines()
		)
		self.assertEqual("...", self._rendered()[0].ParameterGroups[0].Parameters[0].DefaultValue)


class Visitors(SymbolProject):
	def test_HTML(self) -> None:
		"""HTML writes the SVG, and not the node's text."""
		self._symbols(".. vhdl:symbol:: Counter\n")

		html = self._html("page")
		self.assertIn('<div class="vhdl vhdl-symbol" style="overflow-x: auto;">\n<svg>Counter</svg>\n</div>', html)
		self.assertNotIn("parameter MODULO", html)

	def test_LaTeX(self) -> None:
		"""LaTeX writes the TikZ picture, and loads package ``tikz`` and the renderer's TikZ libraries."""
		self._symbols(".. vhdl:symbol:: Counter\n", builder="latex")

		self.assertEqual([], self._warningLines())
		texFiles = list((self._path / "build" / "latex").glob("*.tex"))
		self.assertEqual(1, len(texFiles))
		tex = texFiles[0].read_text(encoding="utf-8")
		self.assertIn("\\usepackage{tikz}", tex)
		self.assertIn("\\usetikzlibrary{positioning,arrows.meta}", tex)
		self.assertIn(
			"\n\n\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{%\n"
			"\\begin{tikzpicture}Counter\\end{tikzpicture}%\n}\n\n",
			tex
		)
		self.assertNotIn("parameter MODULO", tex)

	def test_LaTeX_NoLibraries(self) -> None:
		self._tikzRenderer.TIKZ_LIBRARIES = ()
		self._symbols(".. vhdl:symbol:: Counter\n", builder="latex")

		tex = next((self._path / "build" / "latex").glob("*.tex")).read_text(encoding="utf-8")
		self.assertIn("\\usepackage{tikz}", tex)
		self.assertNotIn("\\usetikzlibrary", tex)

	def test_Text(self) -> None:
		"""Builders without visitors write the node's text: the name, a line per parameter and per pin."""
		self._symbols(".. vhdl:symbol:: Counter\n", builder="text")

		text = (self._path / "build" / "text" / "page.txt").read_text(encoding="utf-8")
		self.assertIn(
			"   Counter\n"
			"     parameter MODULO : positive\n"
			"     parameter BITS : natural := 8\n"
			"     left      Clock : std_logic\n"
			"     left      Reset_n : std_logic\n"
			"     right     Value : unsigned(7 downto 0)\n",
			text
		)
		self._svgRenderer.assert_not_called()

	def test_Parallel(self) -> None:
		"""The node's symbol travels between parallel readers and writers."""
		pages = {
			f"page{index}": f"Page {index}\n######\n\n.. vhdl:symbol:: lib_A.Counter\n   :design: Demo\n"
			for index in range(8)
		}
		self._build(pages, parallel=2)

		self.assertEqual([], self._warningLines())
		for index in range(8):
			with self.subTest(page=index):
				self.assertIn("<svg>Counter</svg>", self._html(f"page{index}"))
