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
Render an interface symbol as an SVG image.

The image is SVG 1.1 text without external resources. Texts stay text (selectable and searchable) in a ``monospace``
font, lines and texts are drawn in ``currentColor``, so the image takes the text color of the page it is embedded in
and works on light and dark pages. The output is deterministic: the same symbol gives the same text.

.. code-block:: python

   from VHDLDomain.Symbol.SVG import SVGRenderer

   svg = SVGRenderer().Render(symbol)
"""
from __future__               import annotations

from xml.sax.saxutils         import escape

from pyTooling.Common         import getFullyQualifiedName
from pyTooling.Decorators     import export
from pyTooling.MetaClasses    import ExtendedType

from VHDLDomain.Symbol        import InterfaceSymbol
from VHDLDomain.Symbol.Layout import BUS_LINE_WIDTH, DASH_PATTERN, FONT_SIZE, LINE_WIDTH, LineStyle, SymbolLayout, \
                                     TextAnchor, TextStyle


@export
class SVGRenderer(metaclass=ExtendedType, slots=True):
	"""
	Renders an interface symbol as SVG 1.1 text.

	The layout's points are the image's user units; ``width`` and ``height`` state the size in points, a ``viewBox``
	lets the image scale.
	"""

	def Render(self, symbol: InterfaceSymbol) -> str:
		"""
		Render an interface symbol as an SVG image.

		:param symbol:      The symbol to render.
		:returns:           The SVG document as text, without XML declaration.
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
		lineStyles = {
			LineStyle.Normal: "",
			LineStyle.Thick:  f" stroke-width=\"{BUS_LINE_WIDTH:g}\"",
			LineStyle.Dashed: f" stroke-dasharray=\"{DASH_PATTERN[0]:g} {DASH_PATTERN[1]:g}\""
		}
		anchors = {
			TextAnchor.Start:  "start",
			TextAnchor.Middle: "middle",
			TextAnchor.End:    "end"
		}
		textStyles = {
			TextStyle.Regular: "",
			TextStyle.Bold:    " font-weight=\"bold\"",
			TextStyle.Italic:  " font-style=\"italic\""
		}

		width =  f"{layout.Width:g}"
		height = f"{layout.Height:g}"
		output = [
			f"<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"{width}pt\" height=\"{height}pt\" "
			f"viewBox=\"0 0 {width} {height}\" font-family=\"monospace\" font-size=\"{FONT_SIZE:g}\">",
			f"<title>{escape(symbol.Name)}</title>",
			f"<g fill=\"none\" stroke=\"currentColor\" stroke-width=\"{LINE_WIDTH:g}\">"
		]
		for rectangle in layout.Rectangles:
			position = rectangle.Position
			output.append(
				f"<rect x=\"{position.X:g}\" y=\"{position.Y:g}\" width=\"{rectangle.Width:g}\" "
				f"height=\"{rectangle.Height:g}\"{lineStyles[rectangle.Style]}/>"
			)

		for line in layout.Lines:
			start = line.Start
			end =   line.End
			output.append(
				f"<line x1=\"{start.X:g}\" y1=\"{start.Y:g}\" x2=\"{end.X:g}\" y2=\"{end.Y:g}\"{lineStyles[line.Style]}/>"
			)

		for circle in layout.Circles:
			center = circle.Center
			output.append(f"<circle cx=\"{center.X:g}\" cy=\"{center.Y:g}\" r=\"{circle.Radius:g}\"/>")

		for polygon in layout.Polygons:
			points = " ".join(f"{point.X:g},{point.Y:g}" for point in polygon.Points)
			output.append(f"<polygon points=\"{points}\"/>")

		output.append("</g>")
		output.append("<g fill=\"currentColor\" xml:space=\"preserve\">")
		for text in layout.Texts:
			position = text.Position
			output.append(
				f"<text x=\"{position.X:g}\" y=\"{position.Y:g}\" text-anchor=\"{anchors[text.Anchor]}\""
				f"{textStyles[text.Style]}>{escape(text.Content)}</text>"
			)

		output.append("</g>")
		output.append("</svg>")

		return "\n".join(output) + "\n"
