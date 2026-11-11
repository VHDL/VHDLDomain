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

The image is SVG 1.1 text without external resources. Texts stay text (selectable and searchable) in their font size and
generic font family, e.g. ``monospace``. Lines and texts are drawn in ``currentColor``, so the image takes the text
color of the page it is embedded in and works on light and dark pages. The output is deterministic: the same symbol
gives the same text.

.. code-block:: python

   from VHDLDomain.Symbol.SVG import SVGRenderer

   svg = SVGRenderer().Render(symbol)
"""
from __future__                    import annotations

from pyTooling.Cartesian2D.Drawing import Circle, FontStyle, LineSegment2D, LineStyle, Polygon, Rectangle, Stroke, \
                                          Text, TextAlignment
from pyTooling.Common              import getFullyQualifiedName
from pyTooling.Decorators          import export
from pyTooling.MetaClasses         import ExtendedType

from VHDLDomain.Symbol             import InterfaceSymbol
from VHDLDomain.Symbol.Layout      import DASH_PATTERN, LINE_WIDTH, SymbolLayout


@export
class SVGRenderer(metaclass=ExtendedType, slots=True):
	"""
	Renders an interface symbol as SVG 1.1 text.

	The layout's points are the image's user units; ``width`` and ``height`` state the size in points, a ``viewBox``
	lets the image scale. Outlines and texts are drawn in ``currentColor``, a font's family is written as is.
	"""

	def Render(self, symbol: InterfaceSymbol) -> str:
		"""
		Render an interface symbol as an SVG image.

		:param symbol:      The symbol to render.
		:returns:           The SVG document as text, without XML declaration.
		:raises ValueError: If parameter 'symbol' is None.
		:raises TypeError:  If parameter 'symbol' is not of type :class:`~VHDLDomain.Symbol.InterfaceSymbol`.
		:raises TypeError:  If the layout's canvas holds an element of a kind the renderer can't draw.
		"""
		if symbol is None:
			raise ValueError("Parameter 'symbol' is None.")
		elif not isinstance(symbol, InterfaceSymbol):
			ex = TypeError("Parameter 'symbol' is not of type 'InterfaceSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(symbol)}'.")
			raise ex

		canvas = SymbolLayout(symbol).Canvas
		lineStyles = {
			LineStyle.Solid:  "",
			LineStyle.Dashed: f" stroke-dasharray=\"{DASH_PATTERN[0]:g} {DASH_PATTERN[1]:g}\""
		}
		anchors = {
			TextAlignment.Left:   "start",
			TextAlignment.Center: "middle",
			TextAlignment.Right:  "end"
		}
		fontStyles = {
			FontStyle.Upright: "",
			FontStyle.Italic:  " font-style=\"italic\"",
			FontStyle.Slanted: " font-style=\"oblique\""
		}

		def strokeAttributes(stroke: Stroke) -> str:
			"""
			Nested function writing the attributes of a stroke: its width, if it differs from the group's, and its dashes.

			:param stroke: The stroke of an outline or a line.
			:returns:      The attributes, each with a leading space.
			"""
			width = "" if stroke.Width == LINE_WIDTH else f" stroke-width=\"{stroke.Width:g}\""
			return f"{width}{lineStyles[stroke.LineStyle]}"

		width =  f"{canvas.Size.Width:g}"
		height = f"{canvas.Size.Height:g}"
		output = [
			f"<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"{width}pt\" height=\"{height}pt\" "
			f"viewBox=\"0 0 {width} {height}\">",
			f"<title>{self._Escape(symbol.Name)}</title>",
			f"<g fill=\"none\" stroke=\"currentColor\" stroke-width=\"{LINE_WIDTH:g}\">"
		]
		texts = []
		for element in canvas.Children:
			if isinstance(element, Rectangle):
				box = element.BoundingBox
				output.append(
					f"<rect x=\"{box.MinX:g}\" y=\"{box.MinY:g}\" width=\"{box.Width:g}\" height=\"{box.Height:g}\""
					f"{strokeAttributes(element.Stroke)}/>"
				)
			elif isinstance(element, LineSegment2D):
				start = element.Start
				end =   element.End
				output.append(
					f"<line x1=\"{start.X:g}\" y1=\"{start.Y:g}\" x2=\"{end.X:g}\" y2=\"{end.Y:g}\""
					f"{strokeAttributes(element.Stroke)}/>"
				)
			elif isinstance(element, Circle):
				center = element.Center
				output.append(
					f"<circle cx=\"{center.X:g}\" cy=\"{center.Y:g}\" r=\"{element.Radius:g}\""
					f"{strokeAttributes(element.Stroke)}/>"
				)
			elif isinstance(element, Polygon):
				points = " ".join(f"{point.X:g},{point.Y:g}" for point in element.Points)
				output.append(f"<polygon points=\"{points}\"{strokeAttributes(element.Stroke)}/>")
			elif isinstance(element, Text):
				position = element.Position
				font =     element.Font
				weight =   " font-weight=\"bold\"" if font.Bold else ""
				variant =  " font-variant=\"small-caps\"" if font.SmallCaps else ""
				texts.append(
					f"<text x=\"{position.X:g}\" y=\"{position.Y:g}\" text-anchor=\"{anchors[element.Alignment]}\" "
					f"font-family=\"{font.Family}\" font-size=\"{font.Size:g}\"{weight}{fontStyles[font.FontStyle]}{variant}>"
					f"{self._Escape(element.Content)}</text>"
				)
			else:
				ex = TypeError("Canvas element is not supported by 'SVGRenderer'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
				raise ex

		output.append("</g>")
		output.append("<g fill=\"currentColor\" xml:space=\"preserve\">")
		output.extend(texts)
		output.append("</g>")
		output.append("</svg>")

		return "\n".join(output) + "\n"

	@staticmethod
	def _Escape(text: str) -> str:
		"""
		Escape a text for the content of an XML element.

		The renderer escapes the symbol's name in ``<title>`` and each text in ``<text>``; attribute values are numbers or
		fixed keywords.

		:param text: The text.
		:returns:    The text with ``&``, ``<`` and ``>`` escaped.
		"""
		return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
