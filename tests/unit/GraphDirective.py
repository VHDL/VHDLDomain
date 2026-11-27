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
Unit tests for the directives ``vhdl:dependencies``, ``vhdl:compile-order`` and ``vhdl:hierarchy``, and the visitors
of their node.

Most tests build the text output, which lists a picture's vertices and edges.
"""
from importlib.util                 import find_spec
from re                             import search
from textwrap                       import dedent
from typing                         import ClassVar
from unittest                       import skipUnless
from unittest.mock                  import patch

from pyTooling.Graph.Layout         import LayoutDirection
from pyTooling.Graph.Layout.Layered import LayeredLayout

from VHDLDomain.Graph.Directive     import GraphNode

from tests.unit.Domain              import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: A :file:`conf.py` adding design ``Demo`` of :func:`tests.unit.Graph.demo`.
CONF = dedent("""\
	from tests.unit.Graph import demo

	extensions = ["VHDLDomain"]


	def addDesigns(app):
		app.env.get_domain("vhdl").AddDesign("Demo", demo())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")

#: The beginning of a page: design ``Demo`` is current.
HEAD = "Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n"

#: Whether matplotlib is installed, which draws a PNG image.
matplotlibIsInstalled = find_spec("matplotlib") is not None


class GraphProject(Project):
	"""A project with design ``Demo``."""

	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	def _text(self, body: str) -> str:
		"""
		Build a page placing the body after ``vhdl:design`` as text, and return the text below the page's title.

		:param body: The page's body.
		:returns:    The page's text, without the title.
		"""
		self._build({"page": f"{HEAD}{body}"}, builder="text")
		return (self._path / "build" / "text" / "page.txt").read_text(encoding="utf-8").removeprefix("Page\n****\n\n")


class Hierarchy(GraphProject):
	def test_All(self) -> None:
		text = self._text(".. vhdl:hierarchy::\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			"   lib_A.Leaf\n"
			"     -> lib_A.Leaf(rtl)\n"
			"   lib_A.Leaf(rtl)\n"
			"   lib_B.Top\n"
			"     -> lib_B.Top(rtl)\n"
			"   lib_B.Top(rtl)\n"
			"     -> lib_A.Leaf\n",
			text
		)

	def test_Start(self) -> None:
		text = self._text(".. vhdl:hierarchy:: lib_B.Top\n   :depth: 1\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   lib_B.Top\n     -> lib_B.Top(rtl)\n   lib_B.Top(rtl)\n", text)

	def test_Start_Architecture(self) -> None:
		text = self._text(".. vhdl:hierarchy:: lib_A.Leaf(rtl)\n   :follow: inbound\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			"   lib_A.Leaf\n     -> lib_A.Leaf(rtl)\n   lib_A.Leaf(rtl)\n   lib_B.Top\n     -> lib_B.Top(rtl)\n"
			"   lib_B.Top(rtl)\n     -> lib_A.Leaf\n",
			text
		)

	def test_Start_CurrentLibrary(self) -> None:
		text = self._text(".. vhdl:library:: lib_A\n   :no-index:\n\n.. vhdl:hierarchy:: leaf\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   lib_A.Leaf\n     -> lib_A.Leaf(rtl)\n   lib_A.Leaf(rtl)\n", text)

	def test_Libraries(self) -> None:
		text = self._text(".. vhdl:hierarchy::\n   :libraries: lib_B\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   lib_B.Top\n     -> lib_B.Top(rtl)\n   lib_B.Top(rtl)\n", text)

	def test_Direction(self) -> None:
		with patch("VHDLDomain.Graph.Directive.LayeredLayout", wraps=LayeredLayout) as layout:
			self._text(".. vhdl:hierarchy::\n\n.. vhdl:hierarchy::\n   :direction: left-to-right\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			[LayoutDirection.TopToBottom, LayoutDirection.LeftToRight],
			[call.kwargs["direction"] for call in layout.call_args_list]
		)


class Dependencies(GraphProject):
	def test_DesignUnits(self) -> None:
		"""Without options, the design units are drawn: no libraries, no source files, nothing of ``std`` or ``ieee``."""
		text = self._text(".. vhdl:dependencies::\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			"   lib_A.Types\n"
			"   lib_A.Types(body)\n"
			"     -> lib_A.Types\n"
			"   lib_A.Leaf\n"
			"     -> lib_A.Types\n"
			"   lib_A.Leaf(rtl)\n"
			"     -> lib_A.Leaf\n"
			"   lib_B.Types\n"
			"   lib_B.Top\n"
			"   lib_B.Top(rtl)\n"
			"     -> lib_B.Top\n"
			"     -> lib_A.Leaf\n",
			text
		)

	def test_Kinds(self) -> None:
		text = self._text(".. vhdl:dependencies:: lib_B.Top\n   :kinds: library, entity\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   lib_A\n   lib_B\n   lib_B.Top\n     -> lib_B\n     -> lib_A\n", text)

	def test_Predefined(self) -> None:
		text = self._text(".. vhdl:dependencies:: lib_B.Top\n   :kinds: library entity package\n   :predefined:\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			"   Std\n   Std.Standard\n     -> Std\n   lib_A\n   lib_B\n   lib_B.Top\n     -> Std\n     -> lib_B\n"
			"     -> lib_A\n     -> Std.Standard\n",
			text
		)

	def test_Kinds_Unknown(self) -> None:
		self._text(".. vhdl:dependencies::\n   :kinds: entity, unit\n")

		self.assertEqual(
			[
				'/src/page.rst:7: ERROR: Error in "vhdl:dependencies" directive:',
				'invalid option value: (option: "kinds"; value: \'entity, unit\')',
				"'unit' is not a vertex kind..",
			],
			self._warningLines()[:3]
		)


class CompileOrder(GraphProject):
	def test_All(self) -> None:
		with patch("VHDLDomain.Graph.Directive.LayeredLayout", wraps=LayeredLayout) as layout:
			text = self._text(".. vhdl:compile-order::\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			"   pkg.vhdl\n   leaf.vhdl\n     -> pkg.vhdl\n   top.vhdl\n     -> leaf.vhdl\n   pkg.vhdl\n", text
		)
		self.assertIs(LayoutDirection.BottomToTop, layout.call_args.kwargs["direction"])

	def test_Start(self) -> None:
		text = self._text(".. vhdl:compile-order:: lib_B/pkg.vhdl\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   pkg.vhdl\n", text)

	def test_Start_Inbound(self) -> None:
		text = self._text(".. vhdl:compile-order:: leaf.vhdl\n   :follow: inbound\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual("   leaf.vhdl\n   top.vhdl\n     -> leaf.vhdl\n", text)

	def test_Start_Ambiguous(self) -> None:
		self._text(".. vhdl:compile-order:: pkg.vhdl\n")

		self.assertEqual(
			[
				"/src/page.rst:7: WARNING: vhdl:compile-order: 'pkg.vhdl' is ambiguous, candidates: pkg.vhdl, pkg.vhdl. "
				"[vhdl.graph]"
			],
			self._warningLines()
		)


class Errors(GraphProject):
	def test_NoDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:hierarchy::\n"})

		self.assertEqual(
			[
				"/src/page.rst:4: WARNING: vhdl:hierarchy: No design: give option ':design:' or place a 'vhdl:design' "
				"before it. [vhdl.design]"
			],
			self._warningLines()
		)

	def test_Unknown(self) -> None:
		self._text(".. vhdl:hierarchy:: lib_A.Types\n")

		self.assertEqual(
			["/src/page.rst:7: WARNING: vhdl:hierarchy: 'lib_A.Types' is not in the hierarchy. [vhdl.graph]"],
			self._warningLines()
		)

	def test_LeftOut(self) -> None:
		"""A library is no design unit, which is drawn by default."""
		self._text(".. vhdl:dependencies:: lib_A\n")

		self.assertEqual(
			["/src/page.rst:7: WARNING: vhdl:dependencies: 'lib_A' is left out by the options. [vhdl.graph]"],
			self._warningLines()
		)

	def test_UnknownLibrary(self) -> None:
		self._text(".. vhdl:hierarchy::\n   :libraries: lib_A, lib_X\n")

		self.assertEqual(
			["/src/page.rst:7: WARNING: vhdl:hierarchy: Library 'lib_X' is not in the design. [vhdl.library]"],
			self._warningLines()
		)

	def test_NothingToDraw(self) -> None:
		self._text(".. vhdl:dependencies::\n   :libraries: lib_B\n   :kinds: configuration\n")

		self.assertEqual(
			["/src/page.rst:7: WARNING: vhdl:dependencies: Nothing to draw. [vhdl.graph]"],
			self._warningLines()
		)

	def test_DepthWithoutStart(self) -> None:
		text = self._text(".. vhdl:hierarchy::\n   :depth: 1\n   :follow: both\n")

		self.assertEqual(
			[
				"/src/page.rst:7: WARNING: vhdl:hierarchy: Option ':depth:' without a start vertex is ignored. [vhdl.graph]",
				"/src/page.rst:7: WARNING: vhdl:hierarchy: Option ':follow:' without a start vertex is ignored. [vhdl.graph]",
			],
			self._warningLines()
		)
		self.assertIn("   lib_B.Top(rtl)\n", text)

	def test_Direction_Unknown(self) -> None:
		self._text(".. vhdl:hierarchy::\n   :direction: sideways\n")

		self.assertEqual(
			[
				'/src/page.rst:7: ERROR: Error in "vhdl:hierarchy" directive:',
				'invalid option value: (option: "direction"; value: \'sideways\')',
				"'sideways' is not a layout direction..",
			],
			self._warningLines()[:3]
		)


class Visitors(GraphProject):
	def test_HTML(self) -> None:
		"""HTML writes the SVG image with its alternative text as title, and not the node's text."""
		self._build({"page": f"{HEAD}.. vhdl:hierarchy:: lib_B.Top\n"})

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIn('<div class="vhdl vhdl-graph" style="overflow-x: auto;">\n<svg xmlns=', html)
		self.assertIn("<title>Hierarchy of design Demo, from lib_B.Top</title>", html)
		self.assertIn(">lib_A.Leaf(rtl)</text>", html)
		self.assertIn('stroke="currentColor"', html)
		self.assertNotIn("-&gt; lib_B.Top(rtl)", html)

	def test_HTML_Alt(self) -> None:
		self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n   :alt: The hierarchy.\n"})

		self.assertIn("<title>The hierarchy.</title>", self._html("page"))

	def test_HTML_Caption(self) -> None:
		self._build({
			"page": f"{HEAD}.. vhdl:hierarchy::\n   :caption: The *hierarchy*.\n   :name: fig-hierarchy\n\n"
			"See :ref:`fig-hierarchy`.\n"
		})

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIsNotNone(
			search(r'<figure class="align-default" id="fig-hierarchy">\s*<div class="vhdl vhdl-graph"', html)
		)
		self.assertIn("The <em>hierarchy</em>.", html)
		self.assertIn('href="#fig-hierarchy"', html)

	def test_HTML_Name(self) -> None:
		self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n   :name: hierarchy\n"})

		self.assertIn('<div class="vhdl vhdl-graph" id="hierarchy" style="overflow-x: auto;">', self._html("page"))

	@skipUnless(matplotlibIsInstalled, "matplotlib isn't installed.")
	def test_HTML_PNG(self) -> None:
		self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n   :format: png\n"})

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIsNotNone(
			match := search(
				r'<img src="_images/(vhdl-graph-[0-9a-f]{40}\.png)" alt="Hierarchy of design Demo" '
				r'style="width: [0-9.]+pt;" />',
				html
			)
		)
		self.assertNotIn("<svg", html)
		png = (self._path / "build" / "html" / "_images" / match[1]).read_bytes()
		self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))

	def test_PNG_MissingDependency(self) -> None:
		"""Without matplotlib, the picture is drawn as vector picture."""
		with patch.dict("sys.modules", {"matplotlib": None}):
			self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n   :format: png\n"})

		self.assertEqual(
			[
				"/src/page.rst:7: WARNING: vhdl:hierarchy: Drawn as vector picture, as matplotlib isn't installed: install "
				"the extra 'VHDLDomain[diagram]'. [vhdl.graph]"
			],
			self._warningLines()
		)
		self.assertIn("<svg", self._html("page"))

	def test_LaTeX(self) -> None:
		"""LaTeX writes the TikZ picture, scaled down to the line width."""
		self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n"}, builder="latex")

		self.assertEqual([], self._warningLines())
		tex = next((self._path / "build" / "latex").glob("*.tex")).read_text(encoding="utf-8")
		self.assertIn(
			"\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{%\n\\begin{tikzpicture}[x=1pt, y=1pt]",
			tex
		)
		self.assertIn("lib\\_A.Leaf(rtl)", tex)
		self.assertNotIn("-> lib_B.Top(rtl)", tex)

	@skipUnless(matplotlibIsInstalled, "matplotlib isn't installed.")
	def test_LaTeX_PNG(self) -> None:
		self._build({"page": f"{HEAD}.. vhdl:hierarchy::\n   :format: png\n"}, builder="latex")

		self.assertEqual([], self._warningLines())
		tex = next((self._path / "build" / "latex").glob("*.tex")).read_text(encoding="utf-8")
		self.assertIsNotNone(match := search(r"\\sphinxincludegraphics\{(vhdl-graph-[0-9a-f]{40}\.png)\}", tex))
		self.assertTrue((self._path / "build" / "latex" / match[1]).exists())
		self.assertNotIn("tikzpicture", tex)

	def test_Parallel(self) -> None:
		"""The node's pictures travel between parallel readers and writers."""
		pages = {
			f"page{index}": f"Page {index}\n######\n\n.. vhdl:hierarchy:: lib_B.Top\n   :design: Demo\n" for index in range(8)
		}
		self._build(pages, parallel=2)

		self.assertEqual([], self._warningLines())
		for index in range(8):
			with self.subTest(page=index):
				self.assertIn(">lib_A.Leaf(rtl)</text>", self._html(f"page{index}"))


class WriteImage(Project):
	def test_Written(self) -> None:
		node = GraphNode("", "", png=b"\x89PNG")

		name = node.WriteImage(self._path / "images")

		self.assertEqual("vhdl-graph-", name[:11])
		self.assertEqual(b"\x89PNG", (self._path / "images" / name).read_bytes())

	def test_Unchanged(self) -> None:
		"""A file named by the same content isn't written again."""
		node = GraphNode("", "", png=b"\x89PNG")
		name = node.WriteImage(self._path)
		(self._path / name).write_bytes(b"marker")

		self.assertEqual(name, node.WriteImage(self._path))
		self.assertEqual(b"marker", (self._path / name).read_bytes())
