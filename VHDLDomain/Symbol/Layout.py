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
The geometry of an interface symbol, shared by the renderers.

A :class:`SymbolLayout` places the symbol's name, its parameter box and its pin box on a
:class:`~pyTooling.Cartesian2D.Groups.Canvas2D` of drawable elements from :mod:`pyTooling.Cartesian2D.Drawing`:
rectangles, line segments, circles, polygons and texts, each with its stroke or font. A renderer only translates them
into its format.

Coordinates are points (1/72 inch), the origin is the top left corner and *y* grows downwards. The layout sets all text
in a monospace font of :data:`FONT_SIZE`, so the width of a text is its number of characters times
:data:`CHARACTER_WIDTH`. A text's position is a point on its baseline; its alignment says, whether the text starts, is
centered or ends there. Lines and texts are drawn in the :class:`CurrentColor`.

.. rubric:: Drawing

* The symbol's name is the title above the boxes.
* The parameter box (dashed) sits on top of the pin box: one line ``NAME : type := default`` per parameter, the three
  parts aligned in columns.
* A group is a horizontal section of its box: a named group starts with its name as a header line, a line separates
  two groups.
* A pin's name is inside the pin box at the edge of its side, its type label is outside, above its stub and next to
  the box. The pins of a side end in one column. A bus pin's stub is thick, a clock pin has a triangle at the inner box
  edge, an inverted pin a circle between box edge and stub.
"""
from __future__                    import annotations

from pyTooling.Cartesian2D         import Point2D, Size2D
from pyTooling.Cartesian2D.Drawing import Circle, Color, Fill, Font, FontStyle, LineSegment2D, LineStyle, Polygon, \
                                          Rectangle, RGBAColor, Stroke, Text, TextAlignment
from pyTooling.Cartesian2D.Groups  import Canvas2D, YAxisDirection
from pyTooling.Common              import getFullyQualifiedName
from pyTooling.Decorators          import export, readonly
from pyTooling.MetaClasses         import ExtendedType

from VHDLDomain.Symbol             import InterfaceSymbol, Pin, PinKind, PinSide


__all__ = [
	"FONT_SIZE", "CHARACTER_WIDTH", "BASELINE_OFFSET", "LINE_HEIGHT", "PIN_PITCH", "PADDING", "SECTION_PADDING",
	"MARGIN", "LINE_WIDTH", "BUS_LINE_WIDTH", "DASH_PATTERN", "STUB_LENGTH", "LABEL_RISE", "CLOCK_WIDTH",
	"CLOCK_HEIGHT", "INVERSION_RADIUS"
]

FONT_SIZE = 10.0
"""Font size of the layout's texts in points."""

CHARACTER_WIDTH = 6.0
"""
Width of a character in points at :data:`FONT_SIZE`.

It is 0.6 of the font size, the advance width of monospace fonts like DejaVu Sans Mono and the default
:attr:`~pyTooling.Cartesian2D.Drawing.Font.CharacterWidth` of a font.
"""

BASELINE_OFFSET = 3.5
"""Distance in points from a text line's vertical center down to its baseline."""

LINE_HEIGHT = 14.0
"""Height of a text line in points at :data:`FONT_SIZE`: the title, a group header or a parameter."""

PIN_PITCH = 20.0
"""Height of a pin row in points; it holds the pin's name and, above its stub, the pin's type label."""

PADDING = 6.0
"""Horizontal distance in points between a box edge or a stub end and a text."""

SECTION_PADDING = 4.0
"""Vertical space in points above and below the content of a group."""

MARGIN = 4.0
"""Space in points around the drawing."""

LINE_WIDTH = 1.0
"""Width of a line in points."""

BUS_LINE_WIDTH = 3.0
"""Width of a bus pin's stub in points."""

DASH_PATTERN = (4.0, 2.0)
"""Dash and gap length in points of a dashed line."""

STUB_LENGTH = 24.0
"""Minimum length of a stub in points, from the box edge to the pin's end."""

LABEL_RISE = 5.0
"""Distance in points from a stub up to the baseline of the type label above it."""

CLOCK_WIDTH = 6.0
"""Depth in points of a clock pin's triangle, from the box edge into the box."""

CLOCK_HEIGHT = 8.0
"""Height in points of a clock pin's triangle at the box edge."""

INVERSION_RADIUS = 3.0
"""Radius in points of an inverted pin's circle."""


@export
class CurrentColor(Color, singleton=True):
	"""
	The foreground color of the medium a drawing is rendered to, like ``currentColor`` in CSS and SVG.

	A renderer draws it in its medium's foreground color: ``currentColor`` in SVG, the current color in TikZ, black in
	matplotlib. There is only one current color: every instantiation returns the same object.
	"""

	def ToRGBA(self) -> RGBAColor:
		"""
		Convert the color to red, green and blue components and an opacity.

		:returns: Opaque black, the foreground color of a medium without a color of its own.
		"""
		return RGBAColor(0, 0, 0)


@export
class SymbolLayout(metaclass=ExtendedType, slots=True):
	"""
	The geometry of an interface symbol: a canvas holding the elements drawing it.

	The canvas' y-axis points down and its size is the size of the drawing. Its children are in drawing order, grouped
	by kind: the rectangles of the parameter box and the pin box, the line segments, the circles, the polygons, then the
	texts.
	"""

	_symbol: InterfaceSymbol  #: The symbol laid out.
	_canvas: Canvas2D[float]  #: The drawing: boxes, group separators, pin stubs, pin glyphs and texts.

	def __init__(self, symbol: InterfaceSymbol) -> None:
		"""
		Initializes the layout of an interface symbol.

		:param symbol:      The symbol to lay out.
		:raises ValueError: If parameter 'symbol' is None.
		:raises TypeError:  If parameter 'symbol' is not of type :class:`~VHDLDomain.Symbol.InterfaceSymbol`.
		"""
		if symbol is None:
			raise ValueError("Parameter 'symbol' is None.")
		elif not isinstance(symbol, InterfaceSymbol):
			ex = TypeError("Parameter 'symbol' is not of type 'InterfaceSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(symbol)}'.")
			raise ex

		self._symbol = symbol
		rectangles =   []
		lines =        []
		circles =      []
		polygons =     []
		texts =        []

		color =        CurrentColor()
		stroke =       Stroke(LINE_WIDTH, color)
		busStroke =    Stroke(BUS_LINE_WIDTH, color)
		dashedStroke = Stroke(LINE_WIDTH, color, LineStyle.Dashed)
		textFill =     Fill(color)
		font =         Font("monospace", FONT_SIZE)
		titleFont =    Font("monospace", FONT_SIZE, bold=True)
		headerFont =   Font("monospace", FONT_SIZE, fontStyle=FontStyle.Italic)

		def addText(position: Point2D[float], content: str, alignment: TextAlignment, textFont: Font) -> None:
			"""
			Nested function adding a single line of text in the current color, its baseline at the position.

			:param position:  Point on the baseline, where the text starts, is centered or ends.
			:param content:   The text.
			:param alignment: The text's horizontal alignment at ``position``.
			:param textFont:  The text's font.
			"""
			texts.append(Text(
				position, content, font=textFont, alignment=alignment, lineHeight=LINE_HEIGHT / FONT_SIZE, fill=textFill
			))

		pins =       [pin for group in symbol.PinGroups for pin in group.Pins]
		leftPins =   [pin for pin in pins if pin.Side is PinSide.Left]
		rightPins =  [pin for pin in pins if pin.Side is PinSide.Right]
		parameters = [parameter for group in symbol.ParameterGroups for parameter in group.Parameters]
		headers =    [group.Name for group in (*symbol.ParameterGroups, *symbol.PinGroups) if group.Name is not None]

		# Parameter columns in characters: 'NAME', ': type' and ':= default', separated by a space.
		nameColumn = max((len(parameter.Name) for parameter in parameters), default=0)
		typeColumn = max((len(parameter.TypeLabel) + 2 for parameter in parameters), default=0)
		defaultColumn = max(
			(len(parameter.DefaultValue) + 3 for parameter in parameters if parameter.DefaultValue is not None),
			default=0
		)
		parameterWidth = (nameColumn + 1 + typeColumn + (1 + defaultColumn if defaultColumn > 0 else 0)) * CHARACTER_WIDTH

		pinNameInset =   PADDING + CLOCK_WIDTH
		leftNameWidth =  max((len(pin.Name) for pin in leftPins), default=0) * CHARACTER_WIDTH
		rightNameWidth = max((len(pin.Name) for pin in rightPins), default=0) * CHARACTER_WIDTH
		headerWidth =    max(len(text) for text in (symbol.Name, *headers)) * CHARACTER_WIDTH

		boxWidth = max(
			2 * pinNameInset + leftNameWidth + 2 * PADDING + rightNameWidth,
			2 * PADDING + parameterWidth,
			2 * PADDING + headerWidth
		)
		leftExtent =  self._PinExtent(leftPins)
		rightExtent = self._PinExtent(rightPins)
		boxLeft =     MARGIN + leftExtent
		boxRight =    boxLeft + boxWidth
		boxCenter =   boxLeft + boxWidth / 2

		y = MARGIN
		addText(Point2D(boxCenter, y + LINE_HEIGHT / 2 + BASELINE_OFFSET), symbol.Name, TextAlignment.Center, titleFont)
		y += LINE_HEIGHT

		if len(symbol.ParameterGroups) > 0:
			nameX =    boxLeft + PADDING
			typeX =    nameX + (nameColumn + 1) * CHARACTER_WIDTH
			defaultX = typeX + (typeColumn + 1) * CHARACTER_WIDTH
			top =      y
			for index, parameterGroup in enumerate(symbol.ParameterGroups):
				if index > 0:
					lines.append(LineSegment2D(Point2D(boxLeft, y), Point2D(boxRight, y), stroke=stroke))

				y += SECTION_PADDING
				if parameterGroup.Name is not None:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					addText(Point2D(boxCenter, baseline), parameterGroup.Name, TextAlignment.Center, headerFont)
					y += LINE_HEIGHT

				for parameter in parameterGroup.Parameters:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					addText(Point2D(nameX, baseline), parameter.Name, TextAlignment.Left, font)
					addText(Point2D(typeX, baseline), f": {parameter.TypeLabel}", TextAlignment.Left, font)
					if parameter.DefaultValue is not None:
						addText(Point2D(defaultX, baseline), f":= {parameter.DefaultValue}", TextAlignment.Left, font)

					y += LINE_HEIGHT

				y += SECTION_PADDING

			rectangles.append(Rectangle(
				Point2D(boxLeft, top), Point2D(boxRight, top), Point2D(boxRight, y), Point2D(boxLeft, y), stroke=dashedStroke
			))

		if len(symbol.PinGroups) > 0:
			top = y
			for index, pinGroup in enumerate(symbol.PinGroups):
				if index > 0:
					lines.append(LineSegment2D(Point2D(boxLeft, y), Point2D(boxRight, y), stroke=stroke))

				y += SECTION_PADDING
				if pinGroup.Name is not None:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					addText(Point2D(boxCenter, baseline), pinGroup.Name, TextAlignment.Center, headerFont)
					y += LINE_HEIGHT

				rowCount = 0
				for side, edge, outwards, extent, nameAlignment, labelAlignment in (
					(PinSide.Left,  boxLeft,  -1.0, leftExtent,  TextAlignment.Left,  TextAlignment.Right),
					(PinSide.Right, boxRight,  1.0, rightExtent, TextAlignment.Right, TextAlignment.Left)
				):
					sidePins = [pin for pin in pinGroup.Pins if pin.Side is side]
					rowCount = max(rowCount, len(sidePins))
					for row, pin in enumerate(sidePins):
						stubY =     y + (row + 0.5) * PIN_PITCH
						end =       edge + outwards * extent
						stubStart = edge + outwards * 2 * INVERSION_RADIUS if pin.IsInverted else edge

						lines.append(
							LineSegment2D(Point2D(end, stubY), Point2D(stubStart, stubY), stroke=busStroke if pin.IsBus else stroke)
						)
						if pin.IsInverted:
							center = Point2D(edge + outwards * INVERSION_RADIUS, stubY)
							circles.append(Circle(center, INVERSION_RADIUS, stroke=stroke))

						if pin.Kind is PinKind.Clock:
							polygons.append(Polygon(
								(
									Point2D(edge, stubY - CLOCK_HEIGHT / 2),
									Point2D(edge - outwards * CLOCK_WIDTH, stubY),
									Point2D(edge, stubY + CLOCK_HEIGHT / 2)
								),
								stroke=stroke
							))

						namePosition =  Point2D(edge - outwards * pinNameInset, stubY + BASELINE_OFFSET)
						labelPosition = Point2D(stubStart + outwards * PADDING, stubY - LABEL_RISE)
						addText(namePosition, pin.Name, nameAlignment, font)
						addText(labelPosition, pin.TypeLabel, labelAlignment, font)

				y += rowCount * PIN_PITCH + SECTION_PADDING

			rectangles.append(Rectangle(
				Point2D(boxLeft, top), Point2D(boxRight, top), Point2D(boxRight, y), Point2D(boxLeft, y), stroke=stroke
			))

		self._canvas = Canvas2D(
			YAxisDirection.Down,
			Size2D(boxRight + rightExtent + MARGIN, y + MARGIN),
			(*rectangles, *lines, *circles, *polygons, *texts)
		)

	@staticmethod
	def _PinExtent(pins: list[Pin]) -> float:
		"""
		Compute how far the pins of one side reach out of the box.

		The pins of a side end in one column. The stub is long enough for the longest type label with :data:`PADDING`
		on both ends, plus an inversion circle.

		:param pins: The pins of one side.
		:returns:    Distance in points from the box edge to the pins' ends, or ``0.0`` if the side has no pins.
		"""
		if len(pins) == 0:
			return 0.0

		labelExtent = max(
			len(pin.TypeLabel) * CHARACTER_WIDTH + 2 * PADDING + (2 * INVERSION_RADIUS if pin.IsInverted else 0.0)
			for pin in pins
		)
		return max(STUB_LENGTH, labelExtent)

	@readonly
	def Symbol(self) -> InterfaceSymbol:
		"""
		Read-only property to access the symbol laid out (:attr:`_symbol`).

		:returns: The interface symbol.
		"""
		return self._symbol

	@readonly
	def Canvas(self) -> Canvas2D[float]:
		"""
		Read-only property to access the drawing (:attr:`_canvas`).

		:returns: The canvas: y-axis pointing down, sized to the drawing, children in drawing order.
		"""
		return self._canvas
