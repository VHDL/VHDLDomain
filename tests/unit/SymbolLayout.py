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
"""Unit tests for the geometry of an interface symbol."""
from typing                        import TypeVar

from pyTooling.Cartesian2D.Drawing import Circle, FontStyle, LineSegment2D, LineStyle, Polygon, Rectangle, RGBAColor, \
                                          Text, TextAlignment
from pyTooling.Cartesian2D.Groups  import YAxisDirection
from pyTooling.Testing             import Testcase

from VHDLDomain.Symbol             import InterfaceSymbol, Parameter, ParameterGroup, Pin, PinGroup, PinKind, PinSide
from VHDLDomain.Symbol.Layout      import BUS_LINE_WIDTH, CHARACTER_WIDTH, FONT_SIZE, LINE_HEIGHT, LINE_WIDTH, MARGIN, \
                                          PADDING, CurrentColor, SymbolLayout


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


Element = TypeVar("Element")
"""Type of a canvas' element, as selected by :func:`ElementsOf`."""


def Inverter() -> InterfaceSymbol:
	"""
	Build a small symbol: one parameter without default, a left pin and an inverted right pin.

	:returns: The symbol ``inv``.
	"""
	symbol = InterfaceSymbol("inv")
	Parameter("WIDTH", "positive", parent=ParameterGroup(parent=symbol))
	group =  PinGroup(parent=symbol)
	Pin("a", "bit", PinSide.Left, parent=group)
	Pin("y_n", "bit", PinSide.Right, isInverted=True, parent=group)

	return symbol


def Fifo() -> InterfaceSymbol:
	"""
	Build a larger symbol: named and unnamed groups, a clock, two buses and an inverted pin.

	:returns: The symbol ``fifo``.
	"""
	symbol =     InterfaceSymbol("fifo")
	parameters = ParameterGroup(parent=symbol)
	Parameter("DEPTH", "positive", "16", parent=parameters)
	Parameter("DATA_BITS", "positive", "8", parent=parameters)

	group = PinGroup(parent=symbol)
	Pin("clock", "std_logic", PinSide.Left, PinKind.Clock, parent=group)
	Pin("reset", "std_logic", PinSide.Left, PinKind.Reset, parent=group)
	group = PinGroup("In", parent=symbol)
	Pin("In_Valid", "std_logic", PinSide.Left, parent=group)
	Pin("In_Data", "std_logic_vector(DATA_BITS - 1 downto 0)", PinSide.Left, isBus=True, parent=group)
	Pin("In_Ack", "std_logic", PinSide.Right, parent=group)
	group = PinGroup(parent=symbol)
	Pin("error_n", "std_logic", PinSide.Right, isInverted=True, parent=group)
	group = PinGroup("Out", parent=symbol)
	Pin("Out_Valid", "std_logic", PinSide.Right, parent=group)
	Pin("Out_Data", "std_logic_vector(DATA_BITS - 1 downto 0)", PinSide.Right, isBus=True, parent=group)
	Pin("Out_Ack", "std_logic", PinSide.Left, parent=group)

	return symbol


def ElementsOf(layout: SymbolLayout, kind: type[Element]) -> list[Element]:
	"""
	Select the elements of one kind from a layout's canvas.

	:param layout: The layout.
	:param kind:   The class of the elements.
	:returns:      The elements of that class, in drawing order.
	"""
	return [element for element in layout.Canvas.Children if isinstance(element, kind)]


class Construction(Testcase):
	def test_Symbol(self) -> None:
		symbol = Inverter()
		layout = SymbolLayout(symbol)

		self.assertIs(symbol, layout.Symbol)

	def test_Symbol_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			SymbolLayout(None)

		self.assertEqual("Parameter 'symbol' is None.", str(context.exception))

	def test_Symbol_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			SymbolLayout("inv")

		self.assertEqual("Parameter 'symbol' is not of type 'InterfaceSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class Canvas(Testcase):
	def test_Canvas(self) -> None:
		"""The canvas' y-axis points down, its size is the drawing's size."""
		canvas = SymbolLayout(Inverter()).Canvas

		self.assertIs(YAxisDirection.Down, canvas.Direction)
		self.assertEqual((182.0, 72.0), canvas.Size.ToTuple())

	def test_DrawingOrder(self) -> None:
		"""The children are grouped by kind: rectangles, line segments, circles, polygons, then texts."""
		kinds =   [Rectangle, LineSegment2D, Circle, Polygon, Text]
		indices = [kinds.index(type(element)) for element in SymbolLayout(Fifo()).Canvas.Children]

		self.assertEqual(43, len(indices))
		self.assertEqual(sorted(indices), indices)

	def test_Rectangles(self) -> None:
		layout = SymbolLayout(Fifo())

		self.assertEqual(2, len(ElementsOf(layout, Rectangle)))

	def test_LineSegments(self) -> None:
		layout = SymbolLayout(Fifo())

		self.assertEqual(12, len(ElementsOf(layout, LineSegment2D)))

	def test_Circles(self) -> None:
		layout = SymbolLayout(Fifo())

		self.assertEqual(1, len(ElementsOf(layout, Circle)))

	def test_Polygons(self) -> None:
		layout = SymbolLayout(Fifo())

		self.assertEqual(1, len(ElementsOf(layout, Polygon)))

	def test_Texts(self) -> None:
		layout = SymbolLayout(Fifo())

		self.assertEqual(27, len(ElementsOf(layout, Text)))


class Geometry(Testcase):
	def test_Inverter(self) -> None:
		layout =     SymbolLayout(Inverter())
		rectangles = ElementsOf(layout, Rectangle)

		self.assertEqual(2, len(rectangles))
		self.assertIs(LineStyle.Dashed, rectangles[0].Stroke.LineStyle)
		self.assertIs(LineStyle.Solid, rectangles[1].Stroke.LineStyle)
		self.assertEqual((34.0, 18.0, 142.0, 40.0), rectangles[0].BoundingBox.ToTuple())
		self.assertEqual((34.0, 40.0, 142.0, 68.0), rectangles[1].BoundingBox.ToTuple())

	def test_Title(self) -> None:
		layout = SymbolLayout(Inverter())
		title =  ElementsOf(layout, Text)[0]

		self.assertEqual("inv", title.Content)
		self.assertIs(TextAlignment.Center, title.Alignment)
		self.assertTrue(title.Font.Bold)
		self.assertEqual(88.0, title.Position.X)

	def test_ParameterColumns(self) -> None:
		"""Name, type and default value of all parameters start in one column each."""
		layout =   SymbolLayout(Fifo())
		contents = {text.Content: text.Position.X for text in ElementsOf(layout, Text)}

		self.assertEqual(contents["DEPTH"], contents["DATA_BITS"])
		self.assertEqual(contents["DEPTH"] + 10 * CHARACTER_WIDTH, contents[": positive"])
		self.assertEqual(contents[": positive"] + 11 * CHARACTER_WIDTH, contents[":= 16"])
		self.assertEqual(contents[":= 16"], contents[":= 8"])

	def test_PinEnds(self) -> None:
		"""The stubs of a side end in one column, far enough out for the longest type label."""
		layout =    SymbolLayout(Fifo())
		pinBox =    ElementsOf(layout, Rectangle)[1].BoundingBox
		lines =     ElementsOf(layout, LineSegment2D)
		leftEnds =  {line.Start.X for line in lines if line.Start.X < pinBox.MinX}
		rightEnds = {line.Start.X for line in lines if line.Start.X > pinBox.MaxX}

		self.assertEqual({MARGIN}, leftEnds)
		self.assertEqual({layout.Canvas.Size.Width - MARGIN}, rightEnds)
		self.assertEqual(40 * CHARACTER_WIDTH + 2 * PADDING, pinBox.MinX - MARGIN)

	def test_GroupSeparators(self) -> None:
		"""A line separates two groups; the first group of a box has none."""
		layout = SymbolLayout(Fifo())
		pinBox = ElementsOf(layout, Rectangle)[1].BoundingBox
		separators = [
			line for line in ElementsOf(layout, LineSegment2D) if line.Start.X == pinBox.MinX and line.Start.Y == line.End.Y
		]

		self.assertEqual(3, len(separators))
		for separator in separators:
			self.assertEqual(pinBox.MaxX, separator.End.X)

	def test_GroupHeaders(self) -> None:
		layout =  SymbolLayout(Fifo())
		headers = [text.Content for text in ElementsOf(layout, Text) if text.Font.FontStyle is FontStyle.Italic]

		self.assertEqual(["In", "Out"], headers)

	def test_Rows(self) -> None:
		"""Left and right pins of a group fill rows from the top, independently."""
		layout = SymbolLayout(Fifo())
		names =  {text.Content: text for text in ElementsOf(layout, Text)}

		self.assertEqual(names["In_Valid"].Position.Y, names["In_Ack"].Position.Y)
		self.assertEqual(names["Out_Ack"].Position.Y, names["Out_Valid"].Position.Y)
		self.assertIs(TextAlignment.Left, names["In_Valid"].Alignment)
		self.assertIs(TextAlignment.Right, names["In_Ack"].Alignment)

	def test_WithoutParameters(self) -> None:
		symbol =     InterfaceSymbol("buf")
		Pin("a", "bit", PinSide.Left, parent=PinGroup(parent=symbol))
		rectangles = ElementsOf(SymbolLayout(symbol), Rectangle)

		self.assertEqual(1, len(rectangles))
		self.assertIs(LineStyle.Solid, rectangles[0].Stroke.LineStyle)

	def test_WithoutPins(self) -> None:
		symbol =     InterfaceSymbol("constants")
		Parameter("WIDTH", "positive", "8", parent=ParameterGroup("Sizes", parent=symbol))
		layout =     SymbolLayout(symbol)
		rectangles = ElementsOf(layout, Rectangle)

		self.assertEqual(1, len(rectangles))
		self.assertIs(LineStyle.Dashed, rectangles[0].Stroke.LineStyle)
		self.assertEqual(0, len(ElementsOf(layout, LineSegment2D)))


class Glyphs(Testcase):
	def test_Bus(self) -> None:
		layout = SymbolLayout(Fifo())
		buses =  [line for line in ElementsOf(layout, LineSegment2D) if line.Stroke.Width == BUS_LINE_WIDTH]

		self.assertEqual(2, len(buses))

	def test_Clock(self) -> None:
		"""A clock pin has a triangle pointing into the box, at the box edge."""
		layout =   SymbolLayout(Fifo())
		boxLeft =  ElementsOf(layout, Rectangle)[1].BoundingBox.MinX
		polygons = ElementsOf(layout, Polygon)

		self.assertEqual(1, len(polygons))
		points = polygons[0].Points
		self.assertEqual(3, len(points))
		self.assertEqual(boxLeft, points[0].X)
		self.assertLess(boxLeft, points[1].X)
		self.assertEqual(boxLeft, points[2].X)

	def test_Reset(self) -> None:
		"""A reset pin has no glyph."""
		symbol = InterfaceSymbol("reg")
		Pin("reset", "std_logic", PinSide.Left, PinKind.Reset, parent=PinGroup(parent=symbol))
		layout = SymbolLayout(symbol)

		self.assertEqual(0, len(ElementsOf(layout, Polygon)))
		self.assertEqual(0, len(ElementsOf(layout, Circle)))

	def test_Inverted(self) -> None:
		"""An inverted pin has a circle between box edge and stub."""
		layout =   SymbolLayout(Inverter())
		boxRight = ElementsOf(layout, Rectangle)[1].BoundingBox.MaxX
		circles =  ElementsOf(layout, Circle)
		stub =     ElementsOf(layout, LineSegment2D)[1]

		self.assertEqual(1, len(circles))
		self.assertEqual(boxRight + circles[0].Radius, circles[0].Center.X)
		self.assertEqual(boxRight + 2 * circles[0].Radius, stub.End.X)
		self.assertEqual(circles[0].Center.Y, stub.End.Y)


class Styles(Testcase):
	def test_CurrentColor(self) -> None:
		"""There is one current color; it converts to opaque black."""
		self.assertIs(CurrentColor(), CurrentColor())
		self.assertEqual(RGBAColor(0, 0, 0), CurrentColor().ToRGBA())

	def test_Rectangles(self) -> None:
		layout = SymbolLayout(Fifo())

		for rectangle in ElementsOf(layout, Rectangle):
			self.assertEqual(LINE_WIDTH, rectangle.Stroke.Width)
			self.assertIs(CurrentColor(), rectangle.Stroke.Color)
			self.assertIsNone(rectangle.Fill)

	def test_LineSegments(self) -> None:
		layout = SymbolLayout(Fifo())

		for line in ElementsOf(layout, LineSegment2D):
			self.assertIs(LineStyle.Solid, line.Stroke.LineStyle)
			self.assertIs(CurrentColor(), line.Stroke.Color)

	def test_Circles(self) -> None:
		layout = SymbolLayout(Fifo())

		for circle in ElementsOf(layout, Circle):
			self.assertEqual(LINE_WIDTH, circle.Stroke.Width)
			self.assertIs(CurrentColor(), circle.Stroke.Color)
			self.assertIsNone(circle.Fill)

	def test_Polygons(self) -> None:
		layout = SymbolLayout(Fifo())

		for polygon in ElementsOf(layout, Polygon):
			self.assertEqual(LINE_WIDTH, polygon.Stroke.Width)
			self.assertIs(CurrentColor(), polygon.Stroke.Color)
			self.assertIsNone(polygon.Fill)

	def test_Texts(self) -> None:
		"""The layout sets all texts in the monospace font of the layout's font size, a line being LINE_HEIGHT high."""
		layout = SymbolLayout(Fifo())

		for text in ElementsOf(layout, Text):
			self.assertEqual("monospace", text.Font.Family)
			self.assertEqual(FONT_SIZE, text.Font.Size)
			self.assertAlmostEqual(LINE_HEIGHT, text.LineHeight * text.Font.Size)
			self.assertIs(CurrentColor(), text.Fill.Color)
			self.assertIsNone(text.Stroke)

	def test_TextWidth(self) -> None:
		"""The estimated width of a text is the layout's width: its number of characters times CHARACTER_WIDTH."""
		layout = SymbolLayout(Fifo())

		for text in ElementsOf(layout, Text):
			self.assertEqual(len(text.Content) * CHARACTER_WIDTH, text.BoundingBox.Width)
