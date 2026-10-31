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
in ``\\ttfamily`` at the layout's font size, special characters of LaTeX are escaped.

.. code-block:: python

   from VHDLDomain.Symbol.TikZ import TikZRenderer

   tikz = TikZRenderer().Render(symbol)
"""
from __future__               import annotations

from typing                   import ClassVar

from pyTooling.Common         import getFullyQualifiedName
from pyTooling.Decorators     import export
from pyTooling.MetaClasses    import ExtendedType

from VHDLDomain.Symbol        import InterfaceSymbol
from VHDLDomain.Symbol.Layout import BUS_LINE_WIDTH, DASH_PATTERN, FONT_SIZE, LINE_HEIGHT, LINE_WIDTH, LineStyle, \
                                     SymbolLayout, TextAnchor, TextStyle


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

		layout =     SymbolLayout(symbol)
		height =     layout.Height
		lineStyles = {
			LineStyle.Normal: "",
			LineStyle.Thick:  f"[line width={BUS_LINE_WIDTH:g}pt]",
			LineStyle.Dashed: f"[dash pattern=on {DASH_PATTERN[0]:g}pt off {DASH_PATTERN[1]:g}pt]"
		}
		anchors = {
			TextAnchor.Start:  "base west",
			TextAnchor.Middle: "base",
			TextAnchor.End:    "base east"
		}
		textStyles = {
			TextStyle.Regular: "",
			TextStyle.Bold:    r"\bfseries ",
			TextStyle.Italic:  r"\itshape "
		}

		output = [
			f"\\begin{{tikzpicture}}[x=1pt, y=1pt, line width={LINE_WIDTH:g}pt, "
			f"font=\\fontsize{{{FONT_SIZE:g}}}{{{LINE_HEIGHT:g}}}\\selectfont\\ttfamily]",
			f"\\useasboundingbox (0,0) rectangle ({layout.Width:g},{height:g});"
		]
		for rectangle in layout.Rectangles:
			position = rectangle.Position
			size =     rectangle.Size
			output.append(
				f"\\draw{lineStyles[rectangle.Style]} ({position.x:g},{height - position.y:g}) "
				f"rectangle ({position.x + size.width:g},{height - position.y - size.height:g});"
			)

		for line in layout.Lines:
			start = line.start
			end =   line.end
			output.append(
				f"\\draw{lineStyles[line.Style]} ({start.x:g},{height - start.y:g}) -- ({end.x:g},{height - end.y:g});"
			)

		for circle in layout.Circles:
			center = circle.center
			output.append(f"\\draw ({center.x:g},{height - center.y:g}) circle[radius={circle.radius:g}];")

		for polygon in layout.Polygons:
			points = " -- ".join(f"({point.x:g},{height - point.y:g})" for point in polygon.points)
			output.append(f"\\draw {points} -- cycle;")

		for text in layout.Texts:
			position = text.Position
			content =  text.Content.translate(self._SPECIAL_CHARACTERS)
			output.append(
				f"\\node[anchor={anchors[text.Anchor]}, inner sep=0pt] at ({position.x:g},{height - position.y:g}) "
				f"{{{textStyles[text.Style]}{content}}};"
			)

		output.append("\\end{tikzpicture}")

		return "\n".join(output) + "\n"
