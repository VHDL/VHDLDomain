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
"""Unit tests for the renderers of an interface symbol: SVG and TikZ."""
from textwrap                import dedent
from xml.etree.ElementTree   import fromstring

from pyTooling.Testing       import Testcase

from VHDLDomain.Symbol       import InterfaceSymbol, Pin, PinGroup, PinSide
from VHDLDomain.Symbol.SVG   import SVGRenderer
from VHDLDomain.Symbol.TikZ  import TikZRenderer

from tests.unit.SymbolLayout import Fifo, Inverter


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"
"""Namespace of SVG elements, as :mod:`xml.etree.ElementTree` writes it in a tag."""


def Escaping() -> InterfaceSymbol:
	"""
	Build a symbol, whose name and type label contain special characters of XML and LaTeX.

	:returns: The symbol ``a<b&c>_x``.
	"""
	symbol = InterfaceSymbol("a<b&c>_x")
	Pin("d", "\\{}_#%&$~^", PinSide.Left, parent=PinGroup(parent=symbol))

	return symbol


class SVG(Testcase):
	def test_Inverter(self) -> None:
		expected = (
			"<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"182pt\" height=\"72pt\" "
			"viewBox=\"0 0 182 72\" font-family=\"monospace\" font-size=\"10\">\n"
		) + dedent("""\
			<title>inv</title>
			<g fill="none" stroke="currentColor" stroke-width="1">
			<rect x="34" y="18" width="108" height="22" stroke-dasharray="4 2"/>
			<rect x="34" y="40" width="108" height="28"/>
			<line x1="4" y1="54" x2="34" y2="54"/>
			<line x1="178" y1="54" x2="148" y2="54"/>
			<circle cx="145" cy="54" r="3"/>
			</g>
			<g fill="currentColor" xml:space="preserve">
			<text x="88" y="14.5" text-anchor="middle" font-weight="bold">inv</text>
			<text x="40" y="32.5" text-anchor="start">WIDTH</text>
			<text x="76" y="32.5" text-anchor="start">: positive</text>
			<text x="46" y="57.5" text-anchor="start">a</text>
			<text x="28" y="49" text-anchor="end">bit</text>
			<text x="130" y="57.5" text-anchor="end">y_n</text>
			<text x="154" y="49" text-anchor="start">bit</text>
			</g>
			</svg>
			""")

		self.assertEqual(expected, SVGRenderer().Render(Inverter()))

	def test_Fifo(self) -> None:
		"""The larger symbol is well-formed SVG with an element per primitive and no external resources."""
		svg =  SVGRenderer().Render(Fifo())
		root = fromstring(svg)

		self.assertEqual(f"{SVG_NAMESPACE}svg", root.tag)
		self.assertEqual("0 0 680 258", root.get("viewBox"))
		self.assertEqual(2, len(root.findall(f".//{SVG_NAMESPACE}rect")))
		self.assertEqual(12, len(root.findall(f".//{SVG_NAMESPACE}line")))
		self.assertEqual(1, len(root.findall(f".//{SVG_NAMESPACE}circle")))
		self.assertEqual(1, len(root.findall(f".//{SVG_NAMESPACE}polygon")))
		self.assertEqual(27, len(root.findall(f".//{SVG_NAMESPACE}text")))
		self.assertNotIn("href", svg)
		self.assertNotIn("<style", svg)
		self.assertEqual(svg, SVGRenderer().Render(Fifo()))

	def test_Bus(self) -> None:
		svg = SVGRenderer().Render(Fifo())

		self.assertEqual(2, svg.count(" stroke-width=\"3\"/>"))

	def test_Clock(self) -> None:
		svg = SVGRenderer().Render(Fifo())

		self.assertIn("<polygon points=\"256,64 262,68 256,72\"/>", svg)

	def test_Inverted(self) -> None:
		svg = SVGRenderer().Render(Fifo())

		self.assertIn("<circle cx=\"427\" cy=\"178\" r=\"3\"/>", svg)

	def test_Escaping(self) -> None:
		svg = SVGRenderer().Render(Escaping())

		self.assertIn("<title>a&lt;b&amp;c&gt;_x</title>", svg)
		self.assertIn(">a&lt;b&amp;c&gt;_x</text>", svg)
		self.assertIn(">\\{}_#%&amp;$~^</text>", svg)

	def test_Symbol_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			SVGRenderer().Render(None)

		self.assertEqual("Parameter 'symbol' is None.", str(context.exception))

	def test_Symbol_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			SVGRenderer().Render("inv")

		self.assertEqual("Parameter 'symbol' is not of type 'InterfaceSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class TikZ(Testcase):
	def test_Inverter(self) -> None:
		expected = dedent("""\
			\\begin{tikzpicture}[x=1pt, y=1pt, line width=1pt, font=\\fontsize{10}{14}\\selectfont\\ttfamily]
			\\useasboundingbox (0,0) rectangle (182,72);
			\\draw[dash pattern=on 4pt off 2pt] (34,54) rectangle (142,32);
			\\draw (34,32) rectangle (142,4);
			\\draw (4,18) -- (34,18);
			\\draw (178,18) -- (148,18);
			\\draw (145,18) circle[radius=3];
			\\node[anchor=base, inner sep=0pt] at (88,57.5) {\\bfseries inv};
			\\node[anchor=base west, inner sep=0pt] at (40,39.5) {WIDTH};
			\\node[anchor=base west, inner sep=0pt] at (76,39.5) {: positive};
			\\node[anchor=base west, inner sep=0pt] at (46,14.5) {a};
			\\node[anchor=base east, inner sep=0pt] at (28,23) {bit};
			\\node[anchor=base east, inner sep=0pt] at (130,14.5) {y\\_n};
			\\node[anchor=base west, inner sep=0pt] at (154,23) {bit};
			\\end{tikzpicture}
			""")

		self.assertEqual(expected, TikZRenderer().Render(Inverter()))

	def test_Fifo(self) -> None:
		"""The larger symbol is one environment with a command per primitive and balanced braces."""
		tikz =  TikZRenderer().Render(Fifo())
		lines = tikz.splitlines()

		self.assertTrue(lines[0].startswith("\\begin{tikzpicture}["))
		self.assertEqual("\\useasboundingbox (0,0) rectangle (680,258);", lines[1])
		self.assertEqual("\\end{tikzpicture}", lines[-1])
		self.assertEqual(2, len([line for line in lines if line.startswith("\\draw") and " rectangle " in line]))
		self.assertEqual(27, tikz.count("\\node["))
		self.assertEqual(tikz.count("{"), tikz.count("}"))
		self.assertEqual((), TikZRenderer.TIKZ_LIBRARIES)

	def test_Bus(self) -> None:
		tikz = TikZRenderer().Render(Fifo())

		self.assertEqual(2, tikz.count("\\draw[line width=3pt] "))

	def test_Clock(self) -> None:
		tikz = TikZRenderer().Render(Fifo())

		self.assertIn("\\draw (256,194) -- (262,190) -- (256,186) -- cycle;", tikz)

	def test_Inverted(self) -> None:
		tikz = TikZRenderer().Render(Fifo())

		self.assertIn("\\draw (427,80) circle[radius=3];", tikz)

	def test_Escaping(self) -> None:
		tikz = TikZRenderer().Render(Escaping())

		self.assertIn("{\\bfseries a<b\\&c>\\_x};", tikz)
		self.assertIn(
			"{\\textbackslash{}\\{\\}\\_\\#\\%\\&\\$\\textasciitilde{}\\textasciicircum{}};",
			tikz
		)

	def test_Symbol_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			TikZRenderer().Render(None)

		self.assertEqual("Parameter 'symbol' is None.", str(context.exception))

	def test_Symbol_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			TikZRenderer().Render("inv")

		self.assertEqual("Parameter 'symbol' is not of type 'InterfaceSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

