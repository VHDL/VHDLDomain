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

A :class:`SymbolLayout` places the symbol's name, its parameter box and its pin box, and returns the drawing as
primitives: rectangles, lines, circles, polygons and texts. A renderer only translates them into its format. The
primitives build on :mod:`pyTooling.Cartesian2D`: a point is a :class:`~pyTooling.Cartesian2D.Point2D`, a line a
:class:`~pyTooling.Cartesian2D.LineSegment2D` and a rectangle a :class:`~pyTooling.Cartesian2D.Shapes.Rectangle`, each
with a style.

Coordinates are points (1/72 inch), the origin is the top left corner and *y* grows downwards. The layout sets all text
in a monospace font of :data:`FONT_SIZE`, so the width of a text is its number of characters times
:data:`CHARACTER_WIDTH`. A text's position is a point on its baseline; its anchor says, whether the text starts, is
centered or ends there. A text carries its font size and font family, which the renderers apply, and its bounding box.

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
from __future__            import annotations

from enum                  import Enum
from typing                import Iterable

from pyTooling.Cartesian2D import LineSegment2D, Point2D, Shapes, Size2D
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType

from VHDLDomain.Symbol     import InterfaceSymbol, Pin, PinKind, PinSide


__all__ = [
	"FONT_SIZE", "CHARACTER_WIDTH", "BASELINE_OFFSET", "LINE_HEIGHT", "PIN_PITCH", "PADDING", "SECTION_PADDING",
	"MARGIN", "LINE_WIDTH", "BUS_LINE_WIDTH", "DASH_PATTERN", "STUB_LENGTH", "LABEL_RISE", "CLOCK_WIDTH",
	"CLOCK_HEIGHT", "INVERSION_RADIUS"
]

FONT_SIZE = 10.0
"""Font size of the layout's texts in points; the default of a :class:`Text`."""

CHARACTER_WIDTH = 6.0
"""
Width of a character in points at :data:`FONT_SIZE`.

It is 0.6 of the font size, the advance width of monospace fonts like DejaVu Sans Mono.
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
class TextAnchor(Enum):
	"""The horizontal position of a text relative to its position."""

	Start =  0  #: The text starts at its position.
	Middle = 1  #: The text is centered on its position.
	End =    2  #: The text ends at its position.


@export
class TextStyle(Enum):
	"""The style of a text."""

	Regular = 0  #: Regular text.
	Bold =    1  #: Bold text, e.g. the symbol's name.
	Italic =  2  #: Italic text, e.g. a group's header.


@export
class FontFamily(Enum):
	"""
	The generic font family of a text.

	Each renderer maps it to its format's equivalent, e.g. ``monospace`` in SVG or ``\\ttfamily`` in TikZ.
	"""

	Monospace = 0  #: A font, whose characters have the same width.
	SansSerif = 1  #: A proportional font without serifs.
	Serif =     2  #: A proportional font with serifs.


@export
class LineStyle(Enum):
	"""The style of a line or an outline."""

	Normal = 0  #: A solid line of :data:`LINE_WIDTH`.
	Thick =  1  #: A solid line of :data:`BUS_LINE_WIDTH`, e.g. a bus pin's stub.
	Dashed = 2  #: A dashed line of :data:`LINE_WIDTH` with :data:`DASH_PATTERN`.


@export
class Text(metaclass=ExtendedType, slots=True):
	"""
	A single line of text with its font size and font family.

	Its bounding box follows from the monospace metrics :data:`CHARACTER_WIDTH` and :data:`LINE_HEIGHT`, scaled to the
	text's font size.
	"""

	_position:   Point2D[float]  #: Point on the baseline, where the text starts, is centered or ends.
	_content:    str             #: The text.
	_anchor:     TextAnchor      #: The text's horizontal position relative to :attr:`_position`.
	_style:      TextStyle       #: The text's style.
	_fontSize:   float           #: Font size in points.
	_fontFamily: FontFamily      #: Generic font family.

	def __init__(
		self,
		position:   Point2D[float],
		content:    str,
		anchor:     TextAnchor,
		style:      TextStyle,
		fontSize:   float = FONT_SIZE,
		fontFamily: FontFamily = FontFamily.Monospace
	) -> None:
		"""
		Initializes a text.

		:param position:   Point on the baseline, where the text starts, is centered or ends.
		:param content:    The text.
		:param anchor:     The text's horizontal position relative to ``position``.
		:param style:      The text's style.
		:param fontSize:   Optional, font size in points. Default: :data:`FONT_SIZE`.
		:param fontFamily: Optional, generic font family. Default: :attr:`FontFamily.Monospace`.
		"""
		self._position =   position
		self._content =    content
		self._anchor =     anchor
		self._style =      style
		self._fontSize =   fontSize
		self._fontFamily = fontFamily

	@readonly
	def Position(self) -> Point2D[float]:
		"""
		Read-only property to access the text's position on its baseline (:attr:`_position`).

		:returns: Point on the baseline.
		"""
		return self._position

	@readonly
	def Content(self) -> str:
		"""
		Read-only property to access the text (:attr:`_content`).

		:returns: The text.
		"""
		return self._content

	@readonly
	def Anchor(self) -> TextAnchor:
		"""
		Read-only property to access the text's horizontal position relative to its position (:attr:`_anchor`).

		:returns: The text's anchor.
		"""
		return self._anchor

	@readonly
	def Style(self) -> TextStyle:
		"""
		Read-only property to access the text's style (:attr:`_style`).

		:returns: The text's style.
		"""
		return self._style

	@readonly
	def FontSize(self) -> float:
		"""
		Read-only property to access the font size (:attr:`_fontSize`).

		:returns: Font size in points.
		"""
		return self._fontSize

	@readonly
	def FontFamily(self) -> FontFamily:
		"""
		Read-only property to access the generic font family (:attr:`_fontFamily`).

		:returns: The text's font family.
		"""
		return self._fontFamily

	@readonly
	def BoundingBox(self) -> Size2D[float]:
		"""
		Read-only property to return the size of the text's bounding box.

		The width is the number of characters times :data:`CHARACTER_WIDTH`, the height is :data:`LINE_HEIGHT`, both
		scaled from :data:`FONT_SIZE` to the text's font size (:attr:`_fontSize`). It's exact for a monospace font with
		the advance width of :data:`CHARACTER_WIDTH`, an estimate for other fonts.

		:returns: Width and height in points.
		"""
		scale = self._fontSize / FONT_SIZE
		return Size2D(len(self._content) * CHARACTER_WIDTH * scale, LINE_HEIGHT * scale)


@export
class Line(LineSegment2D[float]):
	"""A straight line with a style: a line segment from :attr:`start` to :attr:`end`."""

	_style: LineStyle  #: The line's style.

	def __init__(self, start: Point2D[float], end: Point2D[float], style: LineStyle) -> None:
		"""
		Initializes a line.

		:param start:      Start point.
		:param end:        End point.
		:param style:      The line's style.
		:raises TypeError: If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError: If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		"""
		super().__init__(start, end)

		self._style = style

	@readonly
	def Style(self) -> LineStyle:
		"""
		Read-only property to access the line's style (:attr:`_style`).

		:returns: The line's style.
		"""
		return self._style


@export
class Rectangle(Shapes.Rectangle[float], metaclass=ExtendedType):
	"""
	The outline of an axis-parallel box with a style.

	The corners in :attr:`points` are the top left, top right, bottom right and bottom left corner.
	"""

	_style: LineStyle  #: The outline's style.

	def __init__(self, position: Point2D[float], size: Size2D[float], style: LineStyle) -> None:
		"""
		Initializes a rectangle.

		:param position:    Top left corner.
		:param size:        Width and height in points.
		:param style:       The outline's style.
		:raises ValueError: If the width or height is 0.
		"""
		right =  position.x + size.width
		bottom = position.y + size.height
		super().__init__(position, Point2D(right, position.y), Point2D(right, bottom), Point2D(position.x, bottom))

		self._style = style

	@readonly
	def Position(self) -> Point2D[float]:
		"""
		Read-only property to return the top left corner (the first point of :attr:`points`).

		:returns: Top left corner.
		"""
		return self.points[0]

	@readonly
	def Size(self) -> Size2D[float]:
		"""
		Read-only property to return the width and height, computed from the top left and bottom right corner.

		:returns: Width and height in points.
		"""
		topLeft =     self.points[0]
		bottomRight = self.points[2]
		return Size2D(bottomRight.x - topLeft.x, bottomRight.y - topLeft.y)

	@readonly
	def Style(self) -> LineStyle:
		"""
		Read-only property to access the outline's style (:attr:`_style`).

		:returns: The outline's style.
		"""
		return self._style


@export
class Circle(Shapes.Shape[float], metaclass=ExtendedType):
	"""
	The outline of a circle.

	An inverted pin is marked with a circle. The fields follow the planned ``pyTooling.Cartesian2D.Shapes.Circle``, which
	becomes the base-class once a pyTooling release has it.
	"""

	center: Point2D[float]  #: Center.
	radius: float           #: Radius in points.

	def __init__(self, center: Point2D[float], radius: float) -> None:
		"""
		Initializes a circle.

		:param center:      Center; the circle keeps a copy.
		:param radius:      Radius in points.
		:raises ValueError: If parameter 'center' is None.
		:raises TypeError:  If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'radius' is None.
		:raises TypeError:  If parameter 'radius' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'radius' isn't positive.
		"""
		if center is None:
			raise ValueError("Parameter 'center' is None.")
		elif not isinstance(center, Point2D):
			ex = TypeError("Parameter 'center' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(center)}'.")
			raise ex

		if radius is None:
			raise ValueError("Parameter 'radius' is None.")
		elif not isinstance(radius, (float, int)):
			ex = TypeError("Parameter 'radius' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(radius)}'.")
			raise ex
		elif radius <= 0:
			ex = ValueError("Parameter 'radius' isn't positive.")
			ex.add_note(f"Got value '{radius}'.")
			raise ex

		self.center = center.Copy()
		self.radius = radius


@export
class Polygon(Shapes.Shape[float], metaclass=ExtendedType):
	"""
	The closed outline through a sequence of points.

	A clock pin is marked with a triangle. The fields follow the planned ``pyTooling.Cartesian2D.Shapes.Polygon``,
	which becomes the base-class once a pyTooling release has it.
	"""

	points: tuple[Point2D[float], ...]  #: Corners, in drawing order.

	def __init__(self, points: Iterable[Point2D[float]]) -> None:
		"""
		Initializes a polygon.

		:param points:      Corners, in drawing order; the polygon keeps copies.
		:raises ValueError: If parameter 'points' is None.
		:raises TypeError:  If parameter 'points' is not iterable.
		:raises TypeError:  If an element of parameter 'points' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'points' has fewer than 3 points.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		corners = []
		for point in points:
			if not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			corners.append(point.Copy())

		if len(corners) < 3:
			ex = ValueError("Parameter 'points' has fewer than 3 points.")
			ex.add_note(f"Got {len(corners)} points.")
			raise ex

		self.points = tuple(corners)


@export
class SymbolLayout(metaclass=ExtendedType, slots=True):
	"""
	The geometry of an interface symbol: its size and the primitives drawing it.

	The primitives are listed per kind in drawing order: boxes first, the parameter box before the pin box.
	"""

	_symbol:     InterfaceSymbol  #: The symbol laid out.
	_width:      float            #: Width of the drawing in points.
	_height:     float            #: Height of the drawing in points.
	_rectangles: list[Rectangle]  #: Outlines of the parameter box and the pin box.
	_lines:      list[Line]       #: Group separators and pin stubs.
	_circles:    list[Circle]     #: Circles of inverted pins.
	_polygons:   list[Polygon]    #: Triangles of clock pins.
	_texts:      list[Text]       #: Title, group headers, parameters, pin names and type labels.

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

		self._symbol =     symbol
		self._rectangles = rectangles = []
		self._lines =      lines =      []
		self._circles =    circles =    []
		self._polygons =   polygons =   []
		self._texts =      texts =      []

		pins =       [pin for group in symbol.PinGroups for pin in group.Pins]
		leftPins =   [pin for pin in pins if pin.Side is PinSide.Left]
		rightPins =  [pin for pin in pins if pin.Side is PinSide.Right]
		parameters = [parameter for group in symbol.ParameterGroups for parameter in group.Parameters]
		headers =    [group.Name for group in (*symbol.ParameterGroups, *symbol.PinGroups) if group.Name is not None]

		# Parameter columns in characters: 'NAME', ': type' and ':= default', separated by a space.
		nameColumn =    max((len(parameter.Name) for parameter in parameters), default=0)
		typeColumn =    max((len(parameter.TypeLabel) + 2 for parameter in parameters), default=0)
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
		texts.append(
			Text(Point2D(boxCenter, y + LINE_HEIGHT / 2 + BASELINE_OFFSET), symbol.Name, TextAnchor.Middle, TextStyle.Bold)
		)
		y += LINE_HEIGHT

		if len(symbol.ParameterGroups) > 0:
			nameX =    boxLeft + PADDING
			typeX =    nameX + (nameColumn + 1) * CHARACTER_WIDTH
			defaultX = typeX + (typeColumn + 1) * CHARACTER_WIDTH
			top =      y
			for index, parameterGroup in enumerate(symbol.ParameterGroups):
				if index > 0:
					lines.append(Line(Point2D(boxLeft, y), Point2D(boxRight, y), LineStyle.Normal))

				y += SECTION_PADDING
				if parameterGroup.Name is not None:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					texts.append(Text(Point2D(boxCenter, baseline), parameterGroup.Name, TextAnchor.Middle, TextStyle.Italic))
					y += LINE_HEIGHT

				for parameter in parameterGroup.Parameters:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					texts.append(Text(Point2D(nameX, baseline), parameter.Name, TextAnchor.Start, TextStyle.Regular))
					texts.append(Text(Point2D(typeX, baseline), f": {parameter.TypeLabel}", TextAnchor.Start, TextStyle.Regular))
					if parameter.DefaultValue is not None:
						defaultValue = f":= {parameter.DefaultValue}"
						texts.append(Text(Point2D(defaultX, baseline), defaultValue, TextAnchor.Start, TextStyle.Regular))

					y += LINE_HEIGHT

				y += SECTION_PADDING

			rectangles.append(Rectangle(Point2D(boxLeft, top), Size2D(boxWidth, y - top), LineStyle.Dashed))

		if len(symbol.PinGroups) > 0:
			top = y
			for index, pinGroup in enumerate(symbol.PinGroups):
				if index > 0:
					lines.append(Line(Point2D(boxLeft, y), Point2D(boxRight, y), LineStyle.Normal))

				y += SECTION_PADDING
				if pinGroup.Name is not None:
					baseline = y + LINE_HEIGHT / 2 + BASELINE_OFFSET
					texts.append(Text(Point2D(boxCenter, baseline), pinGroup.Name, TextAnchor.Middle, TextStyle.Italic))
					y += LINE_HEIGHT

				rowCount = 0
				for side, edge, outwards, extent, nameAnchor, labelAnchor in (
					(PinSide.Left,  boxLeft,  -1.0, leftExtent,  TextAnchor.Start, TextAnchor.End),
					(PinSide.Right, boxRight,  1.0, rightExtent, TextAnchor.End,   TextAnchor.Start)
				):
					sidePins = [pin for pin in pinGroup.Pins if pin.Side is side]
					rowCount = max(rowCount, len(sidePins))
					for row, pin in enumerate(sidePins):
						stubY =     y + (row + 0.5) * PIN_PITCH
						end =       edge + outwards * extent
						stubStart = edge + outwards * 2 * INVERSION_RADIUS if pin.IsInverted else edge
						lineStyle = LineStyle.Thick if pin.IsBus else LineStyle.Normal

						lines.append(Line(Point2D(end, stubY), Point2D(stubStart, stubY), lineStyle))
						if pin.IsInverted:
							circles.append(Circle(Point2D(edge + outwards * INVERSION_RADIUS, stubY), INVERSION_RADIUS))

						if pin.Kind is PinKind.Clock:
							polygons.append(Polygon((
								Point2D(edge, stubY - CLOCK_HEIGHT / 2),
								Point2D(edge - outwards * CLOCK_WIDTH, stubY),
								Point2D(edge, stubY + CLOCK_HEIGHT / 2)
							)))

						namePosition =  Point2D(edge - outwards * pinNameInset, stubY + BASELINE_OFFSET)
						labelPosition = Point2D(stubStart + outwards * PADDING, stubY - LABEL_RISE)
						texts.append(Text(namePosition, pin.Name, nameAnchor, TextStyle.Regular))
						texts.append(Text(labelPosition, pin.TypeLabel, labelAnchor, TextStyle.Regular))

				y += rowCount * PIN_PITCH + SECTION_PADDING

			rectangles.append(Rectangle(Point2D(boxLeft, top), Size2D(boxWidth, y - top), LineStyle.Normal))

		self._width =  boxRight + rightExtent + MARGIN
		self._height = y + MARGIN

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
	def Width(self) -> float:
		"""
		Read-only property to access the width of the drawing (:attr:`_width`).

		:returns: Width in points.
		"""
		return self._width

	@readonly
	def Height(self) -> float:
		"""
		Read-only property to access the height of the drawing (:attr:`_height`).

		:returns: Height in points.
		"""
		return self._height

	@readonly
	def Rectangles(self) -> list[Rectangle]:
		"""
		Read-only property to access the outlines of the parameter box and the pin box (:attr:`_rectangles`).

		:returns: List of rectangles, in drawing order.
		"""
		return self._rectangles

	@readonly
	def Lines(self) -> list[Line]:
		"""
		Read-only property to access the group separators and pin stubs (:attr:`_lines`).

		:returns: List of lines, in drawing order.
		"""
		return self._lines

	@readonly
	def Circles(self) -> list[Circle]:
		"""
		Read-only property to access the circles of inverted pins (:attr:`_circles`).

		:returns: List of circles, in drawing order.
		"""
		return self._circles

	@readonly
	def Polygons(self) -> list[Polygon]:
		"""
		Read-only property to access the triangles of clock pins (:attr:`_polygons`).

		:returns: List of polygons, in drawing order.
		"""
		return self._polygons

	@readonly
	def Texts(self) -> list[Text]:
		"""
		Read-only property to access the title, group headers, parameters, pin names and type labels (:attr:`_texts`).

		:returns: List of texts, in drawing order.
		"""
		return self._texts
