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
"""
Render an interface symbol as a TikZ picture.

The output is a complete ``tikzpicture`` environment; a LaTeX document needs only ``\\usepackage{tikz}``. Texts are set
in their font size and the LaTeX equivalent of their font family, e.g. ``\\ttfamily``; special characters of LaTeX are
escaped.

.. code-block:: python

   from VHDLDomain.Symbol.TikZ import TikZRenderer

   tikz = TikZRenderer().Render(symbol)
"""
from __future__                    import annotations

from typing                        import ClassVar

from pyTooling.Cartesian2D.Drawing import Circle, FontStyle, LineSegment2D, LineStyle, Polygon, Rectangle, Stroke, \
                                          Text, TextAlignment
from pyTooling.Common              import getFullyQualifiedName
from pyTooling.Decorators          import export
from pyTooling.MetaClasses         import ExtendedType

from VHDLDomain.Symbol             import InterfaceSymbol
from VHDLDomain.Symbol.Layout      import DASH_PATTERN, LINE_WIDTH, SymbolLayout


@export
class TikZRenderer(metaclass=ExtendedType, slots=True):
	"""
	Renders an interface symbol as a TikZ picture.

	One TikZ unit is one point of the layout; the origin is the bottom left corner of the drawing, so *y* is flipped.
	A text node is anchored on its baseline, so a font narrower than the layout's monospace metrics still starts or
	ends at its position.
	"""

	TIKZ_LIBRARIES: ClassVar[tuple[str, ...]] = ()  #: TikZ libraries the picture needs (``\usetikzlibrary``).

	_SPECIAL_CHARACTERS: ClassVar[dict[int, str]] = str.maketrans({
		"\\": r"\textbackslash{}",
		"{":  r"\{",
		"}":  r"\}",
		"_":  r"\_",
		"#":  r"\#",
		"%":  r"\%",
		"&":  r"\&",
		"$":  r"\$",
		"~":  r"\textasciitilde{}",
		"^":  r"\textasciicircum{}"
	})  #: Translation table escaping the special characters of LaTeX.

	def Render(self, symbol: InterfaceSymbol) -> str:
		"""
		Render an interface symbol as a TikZ picture.

		:param symbol:      The symbol to render.
		:returns:           The ``tikzpicture`` environment as text.
		:raises ValueError: If parameter 'symbol' is None.
		:raises TypeError:  If parameter 'symbol' is not of type :class:`~VHDLDomain.Symbol.InterfaceSymbol`.
		"""
		if symbol is None:
			raise ValueError("Parameter 'symbol' is None.")
		elif not isinstance(symbol, InterfaceSymbol):
			ex = TypeError("Parameter 'symbol' is not of type 'InterfaceSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(symbol)}'.")
			raise ex

		canvas = SymbolLayout(symbol).Canvas
		height = canvas.Size.Height
		lineStyles = {
			LineStyle.Dashed: f"dash pattern=on {DASH_PATTERN[0]:g}pt off {DASH_PATTERN[1]:g}pt"
		}
		anchors = {
			TextAlignment.Left:   "base west",
			TextAlignment.Center: "base",
			TextAlignment.Right:  "base east"
		}
		fontStyles = {
			FontStyle.Upright: "",
			FontStyle.Italic:  r"\itshape ",
			FontStyle.Slanted: r"\slshape "
		}
		fontFamilies = {
			"monospace":  r"\ttfamily",
			"sans-serif": r"\sffamily",
			"serif":      r"\rmfamily"
		}

		def strokeOptions(stroke: Stroke) -> str:
			"""
			Nested function writing the options of a stroke: its width, if it differs from the picture's, and its dashes.

			:param stroke: The stroke of an outline or a line.
			:returns:      The options in brackets, or an empty string if there are none.
			"""
			options = []
			if stroke.Width != LINE_WIDTH:
				options.append(f"line width={stroke.Width:g}pt")

			if stroke.LineStyle is not LineStyle.Solid:
				options.append(lineStyles[stroke.LineStyle])

			return f"[{', '.join(options)}]" if len(options) > 0 else ""

		output = [
			f"\\begin{{tikzpicture}}[x=1pt, y=1pt, line width={LINE_WIDTH:g}pt]",
			f"\\useasboundingbox (0,0) rectangle ({canvas.Size.Width:g},{height:g});"
		]
		for element in canvas.Children:
			if isinstance(element, Rectangle):
				box = element.BoundingBox
				output.append(
					f"\\draw{strokeOptions(element.Stroke)} ({box.MinX:g},{height - box.MinY:g}) "
					f"rectangle ({box.MaxX:g},{height - box.MaxY:g});"
				)
			elif isinstance(element, LineSegment2D):
				start = element.Start
				end =   element.End
				output.append(
					f"\\draw{strokeOptions(element.Stroke)} ({start.X:g},{height - start.Y:g}) -- ({end.X:g},{height - end.Y:g});"
				)
			elif isinstance(element, Circle):
				center = element.Center
				output.append(
					f"\\draw{strokeOptions(element.Stroke)} ({center.X:g},{height - center.Y:g}) "
					f"circle[radius={element.Radius:g}];"
				)
			elif isinstance(element, Polygon):
				points = " -- ".join(f"({point.X:g},{height - point.Y:g})" for point in element.Points)
				output.append(f"\\draw{strokeOptions(element.Stroke)} {points} -- cycle;")
			elif isinstance(element, Text):
				position = element.Position
				font =     element.Font
				content =  element.Content.translate(self._SPECIAL_CHARACTERS)
				fontSize = f"\\fontsize{{{font.Size:g}}}{{{font.Size * element.LineHeight:g}}}"
				series =   r"\bfseries " if font.Bold else ""
				shape =    r"\scshape " if font.SmallCaps else ""
				output.append(
					f"\\node[anchor={anchors[element.Alignment]}, inner sep=0pt, "
					f"font={fontSize}\\selectfont{fontFamilies[font.Family]}] at ({position.X:g},{height - position.Y:g}) "
					f"{{{series}{fontStyles[font.FontStyle]}{shape}{content}}};"
				)

		output.append("\\end{tikzpicture}")

		return "\n".join(output) + "\n"
