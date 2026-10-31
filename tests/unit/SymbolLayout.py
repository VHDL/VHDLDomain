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
from pyTooling.Testing        import Testcase

from VHDLDomain.Symbol        import InterfaceSymbol, Parameter, ParameterGroup, Pin, PinGroup, PinKind, PinSide
from VHDLDomain.Symbol.Layout import CHARACTER_WIDTH, MARGIN, PADDING, LineStyle, SymbolLayout, TextAnchor, TextStyle


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


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


class Geometry(Testcase):
	def test_Inverter(self) -> None:
		layout = SymbolLayout(Inverter())

		self.assertEqual(182.0, layout.Width)
		self.assertEqual(72.0, layout.Height)

		parameterBox = layout.Rectangles[0]
		pinBox =       layout.Rectangles[1]
		self.assertEqual(2, len(layout.Rectangles))
		self.assertIs(LineStyle.Dashed, parameterBox.Style)
		self.assertIs(LineStyle.Normal, pinBox.Style)
		self.assertEqual(34.0, parameterBox.Position.X)
		self.assertEqual(18.0, parameterBox.Position.Y)
		self.assertEqual(108.0, parameterBox.Width)
		self.assertEqual(22.0, parameterBox.Height)
		self.assertEqual(34.0, pinBox.Position.X)
		self.assertEqual(40.0, pinBox.Position.Y)
		self.assertEqual(108.0, pinBox.Width)
		self.assertEqual(28.0, pinBox.Height)

	def test_Title(self) -> None:
		layout = SymbolLayout(Inverter())
		title =  layout.Texts[0]

		self.assertEqual("inv", title.Content)
		self.assertIs(TextAnchor.Middle, title.Anchor)
		self.assertIs(TextStyle.Bold, title.Style)
		self.assertEqual(88.0, title.Position.X)

	def test_ParameterColumns(self) -> None:
		"""Name, type and default value of all parameters start in one column each."""
		layout =   SymbolLayout(Fifo())
		contents = {text.Content: text.Position.X for text in layout.Texts}

		self.assertEqual(contents["DEPTH"], contents["DATA_BITS"])
		self.assertEqual(contents["DEPTH"] + 10 * CHARACTER_WIDTH, contents[": positive"])
		self.assertEqual(contents[": positive"] + 11 * CHARACTER_WIDTH, contents[":= 16"])
		self.assertEqual(contents[":= 16"], contents[":= 8"])

	def test_PinEnds(self) -> None:
		"""The stubs of a side end in one column, far enough out for the longest type label."""
		layout =    SymbolLayout(Fifo())
		pinBox =    layout.Rectangles[1]
		boxLeft =   pinBox.Position.X
		boxRight =  boxLeft + pinBox.Width
		leftEnds =  {line.Start.X for line in layout.Lines if line.Start.X < boxLeft}
		rightEnds = {line.Start.X for line in layout.Lines if line.Start.X > boxRight}

		self.assertEqual({MARGIN}, leftEnds)
		self.assertEqual({layout.Width - MARGIN}, rightEnds)
		self.assertEqual(40 * CHARACTER_WIDTH + 2 * PADDING, boxLeft - MARGIN)

	def test_GroupSeparators(self) -> None:
		"""A line separates two groups; the first group of a box has none."""
		layout =     SymbolLayout(Fifo())
		pinBox =     layout.Rectangles[1]
		separators = [line for line in layout.Lines if line.Start.X == pinBox.Position.X and line.Start.Y == line.End.Y]

		self.assertEqual(3, len(separators))
		for separator in separators:
			self.assertEqual(pinBox.Position.X + pinBox.Width, separator.End.X)

	def test_GroupHeaders(self) -> None:
		layout =  SymbolLayout(Fifo())
		headers = [text.Content for text in layout.Texts if text.Style is TextStyle.Italic]

		self.assertEqual(["In", "Out"], headers)

	def test_Rows(self) -> None:
		"""Left and right pins of a group fill rows from the top, independently."""
		layout = SymbolLayout(Fifo())
		names =  {text.Content: text for text in layout.Texts}

		self.assertEqual(names["In_Valid"].Position.Y, names["In_Ack"].Position.Y)
		self.assertEqual(names["Out_Ack"].Position.Y, names["Out_Valid"].Position.Y)
		self.assertIs(TextAnchor.Start, names["In_Valid"].Anchor)
		self.assertIs(TextAnchor.End, names["In_Ack"].Anchor)

	def test_WithoutParameters(self) -> None:
		symbol = InterfaceSymbol("buf")
		Pin("a", "bit", PinSide.Left, parent=PinGroup(parent=symbol))
		layout = SymbolLayout(symbol)

		self.assertEqual(1, len(layout.Rectangles))
		self.assertIs(LineStyle.Normal, layout.Rectangles[0].Style)

	def test_WithoutPins(self) -> None:
		symbol = InterfaceSymbol("constants")
		Parameter("WIDTH", "positive", "8", parent=ParameterGroup("Sizes", parent=symbol))
		layout = SymbolLayout(symbol)

		self.assertEqual(1, len(layout.Rectangles))
		self.assertIs(LineStyle.Dashed, layout.Rectangles[0].Style)
		self.assertEqual(0, len(layout.Lines))


class Glyphs(Testcase):
	def test_Bus(self) -> None:
		layout = SymbolLayout(Fifo())
		buses =  [line for line in layout.Lines if line.Style is LineStyle.Thick]

		self.assertEqual(2, len(buses))

	def test_Clock(self) -> None:
		"""A clock pin has a triangle pointing into the box, at the box edge."""
		layout =  SymbolLayout(Fifo())
		boxLeft = layout.Rectangles[1].Position.X

		self.assertEqual(1, len(layout.Polygons))
		points = layout.Polygons[0].Points
		self.assertEqual(3, len(points))
		self.assertEqual(boxLeft, points[0].X)
		self.assertLess(boxLeft, points[1].X)
		self.assertEqual(boxLeft, points[2].X)

	def test_Reset(self) -> None:
		"""A reset pin has no glyph."""
		symbol = InterfaceSymbol("reg")
		Pin("reset", "std_logic", PinSide.Left, PinKind.Reset, parent=PinGroup(parent=symbol))
		layout = SymbolLayout(symbol)

		self.assertEqual(0, len(layout.Polygons))
		self.assertEqual(0, len(layout.Circles))

	def test_Inverted(self) -> None:
		"""An inverted pin has a circle between box edge and stub."""
		layout =   SymbolLayout(Inverter())
		boxRight = layout.Rectangles[1].Position.X + layout.Rectangles[1].Width
		circle =   layout.Circles[0]
		stub =     layout.Lines[1]

		self.assertEqual(1, len(layout.Circles))
		self.assertEqual(boxRight + circle.Radius, circle.Center.X)
		self.assertEqual(boxRight + 2 * circle.Radius, stub.End.X)
		self.assertEqual(circle.Center.Y, stub.End.Y)
