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
"""Unit tests for the conversion of a VHDL entity or component into an interface symbol."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, Mode, SimpleRange
from pyVHDLModel.DesignUnit import Component, Entity, Package
from pyVHDLModel.Expression import FunctionCall, IntegerLiteral
from pyVHDLModel.Interface  import GenericConstantInterfaceItem, GenericFunctionInterfaceItem, \
                                   GenericPackageInterfaceItem, GenericProcedureInterfaceItem, \
                                   GenericTypeInterfaceItem, PortSimpleSignalInterfaceItem, \
                                   PortViewSignalInterfaceItem
from pyVHDLModel.Name       import SelectedName, SimpleName
from pyVHDLModel.Symbol     import ConstrainedArraySubtypeSymbol, ConstrainedScalarSubtypeSymbol, ModeViewSymbol, \
                                   SimpleSubtypeSymbol

from VHDLDomain.Symbol      import InterfaceSymbol, Pin, PinKind, PinSide
from VHDLDomain.Symbol.VHDL import VHDLConverter


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def subtype(name: str) -> SimpleSubtypeSymbol:
	"""
	Create a subtype indication by a simple type mark.

	:param name: The type mark.
	:returns:    The subtype symbol.
	"""
	return SimpleSubtypeSymbol(SimpleName(name))


def vector(name: str, high: int) -> ConstrainedArraySubtypeSymbol:
	"""
	Create a constrained array subtype indication ``<name>(<high> downto 0)``.

	:param name: The type mark.
	:param high: The left bound.
	:returns:    The subtype symbol.
	"""
	return ConstrainedArraySubtypeSymbol(
		SimpleName(name), [SimpleRange(IntegerLiteral(high), IntegerLiteral(0), Direction.DownTo)]
	)


def pins(*ports: PortSimpleSignalInterfaceItem | PortViewSignalInterfaceItem) -> dict[str, Pin]:
	"""
	Convert an entity of the given ports, and return its pins.

	:param ports: The entity's ports.
	:returns:     The pins, by name.
	"""
	symbol = VHDLConverter().Convert(Entity("E", portItems=ports))

	return {pin.Name: pin for pin in symbol.PinGroups[0].Pins}


class Symbol(Testcase):
	def test_Entity(self) -> None:
		symbol = VHDLConverter().Convert(Entity(
			"Counter",
			genericItems=[GenericConstantInterfaceItem(("BITS", ), Mode.In, subtype("positive"))],
			portItems=[PortSimpleSignalInterfaceItem(("Clock", ), Mode.In, subtype("std_logic"))]
		))

		self.assertIsInstance(symbol, InterfaceSymbol)
		self.assertEqual("Counter", symbol.Name)
		self.assertEqual(1, len(symbol.ParameterGroups))
		self.assertIsNone(symbol.ParameterGroups[0].Name)
		self.assertEqual(["BITS"], [parameter.Name for parameter in symbol.ParameterGroups[0].Parameters])
		self.assertEqual(1, len(symbol.PinGroups))
		self.assertIsNone(symbol.PinGroups[0].Name)
		self.assertEqual(["Clock"], [pin.Name for pin in symbol.PinGroups[0].Pins])

	def test_Component(self) -> None:
		symbol = VHDLConverter().Convert(Component(
			"Counter", portItems=[PortSimpleSignalInterfaceItem(("Value", ), Mode.Out, subtype("bit"))]
		))

		self.assertEqual("Counter", symbol.Name)
		self.assertEqual([], symbol.ParameterGroups)
		self.assertEqual(["Value"], [pin.Name for pin in symbol.PinGroups[0].Pins])

	def test_Empty(self) -> None:
		"""A unit without generics and ports has no groups."""
		symbol = VHDLConverter().Convert(Entity("Empty"))

		self.assertEqual([], symbol.ParameterGroups)
		self.assertEqual([], symbol.PinGroups)

	def test_IdentifierList(self) -> None:
		"""Each identifier of a declaration is a pin or parameter of its own, in declaration order."""
		symbol = VHDLConverter().Convert(Entity(
			"E",
			genericItems=[GenericConstantInterfaceItem(("A", "B"), Mode.In, subtype("natural"), IntegerLiteral(2))],
			portItems=[
				PortSimpleSignalInterfaceItem(("x", "y"), Mode.In, subtype("bit")),
				PortSimpleSignalInterfaceItem(("z", ), Mode.Out, subtype("bit")),
			]
		))

		parameters = symbol.ParameterGroups[0].Parameters
		self.assertEqual(["A", "B"], [parameter.Name for parameter in parameters])
		for parameter in parameters:
			with self.subTest(parameter=parameter.Name):
				self.assertEqual("natural", parameter.TypeLabel)
				self.assertEqual("2", parameter.DefaultValue)

		self.assertEqual(["x", "y", "z"], [pin.Name for pin in symbol.PinGroups[0].Pins])

	def test_Unit_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLConverter().Convert(None)

		self.assertEqual("Parameter 'unit' is None.", str(context.exception))

	def test_Unit_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLConverter().Convert(Package("Utilities"))

		self.assertEqual("Parameter 'unit' is not of type 'Entity' or 'Component'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.DesignUnit.Package'."], context.exception.__notes__)


class Formatter(Testcase):
	def test_Formatter(self) -> None:
		"""The formatter writes the subtypes and default values."""
		symbol = VHDLConverter(lambda element: f"<{type(element).__name__}>").Convert(Entity(
			"E",
			genericItems=[GenericConstantInterfaceItem(("N", ), Mode.In, subtype("natural"), FunctionCall())],
			portItems=[PortSimpleSignalInterfaceItem(("x", ), Mode.In, subtype("bit"))]
		))

		parameter = symbol.ParameterGroups[0].Parameters[0]
		self.assertEqual("<SimpleSubtypeSymbol>", parameter.TypeLabel)
		self.assertEqual("<FunctionCall>", parameter.DefaultValue)
		self.assertEqual("<SimpleSubtypeSymbol>", symbol.PinGroups[0].Pins[0].TypeLabel)

	def test_Formatter_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLConverter("Format")

		self.assertEqual("Parameter 'formatter' is not callable.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class Generics(Testcase):
	def test_Constant(self) -> None:
		symbol = VHDLConverter().Convert(Entity(
			"E",
			genericItems=[
				GenericConstantInterfaceItem(("MODULO", ), Mode.In, subtype("positive")),
				GenericConstantInterfaceItem(("BITS", ), Mode.In, subtype("natural"), IntegerLiteral(8)),
			]
		))

		modulo, bits = symbol.ParameterGroups[0].Parameters
		self.assertEqual("positive", modulo.TypeLabel)
		self.assertIsNone(modulo.DefaultValue)
		self.assertEqual("natural", bits.TypeLabel)
		self.assertEqual("8", bits.DefaultValue)

	def test_OtherKinds(self) -> None:
		"""A generic type, package, function or procedure shows its keyword as type, and no default value."""
		symbol = VHDLConverter().Convert(Entity(
			"E",
			genericItems=[
				GenericTypeInterfaceItem("T_DATA"),
				GenericPackageInterfaceItem("P"),
				GenericFunctionInterfaceItem("f", subtype("bit")),
				GenericProcedureInterfaceItem("p"),
			]
		))

		parameters = symbol.ParameterGroups[0].Parameters
		self.assertEqual(["T_DATA", "P", "f", "p"], [parameter.Name for parameter in parameters])
		self.assertEqual(["type", "package", "function", "procedure"], [parameter.TypeLabel for parameter in parameters])
		for parameter in parameters:
			with self.subTest(parameter=parameter.Name):
				self.assertIsNone(parameter.DefaultValue)


class Sides(Testcase):
	def test_Left(self) -> None:
		"""Mode ``in`` and no mode - which is ``in`` - are on the left edge."""
		converted = pins(
			PortSimpleSignalInterfaceItem(("a", ), Mode.In, subtype("bit")),
			PortSimpleSignalInterfaceItem(("b", ), Mode.Default, subtype("bit")),
		)

		for name in ("a", "b"):
			with self.subTest(port=name):
				self.assertIs(PinSide.Left, converted[name].Side)

	def test_Right(self) -> None:
		"""Mode ``out``, ``inout``, ``buffer`` and ``linkage`` are on the right edge."""
		converted = pins(
			PortSimpleSignalInterfaceItem(("a", ), Mode.Out, subtype("bit")),
			PortSimpleSignalInterfaceItem(("b", ), Mode.InOut, subtype("bit")),
			PortSimpleSignalInterfaceItem(("c", ), Mode.Buffer, subtype("bit")),
			PortSimpleSignalInterfaceItem(("d", ), Mode.Linkage, subtype("bit")),
		)

		for name in ("a", "b", "c", "d"):
			with self.subTest(port=name):
				self.assertIs(PinSide.Right, converted[name].Side)

	def test_View(self) -> None:
		"""A port with a mode view is a bus on the right edge, typed ``view <name>``."""
		pin = pins(PortViewSignalInterfaceItem(("Stream", ), ModeViewSymbol(SimpleName("Source"))))["Stream"]

		self.assertIs(PinSide.Right, pin.Side)
		self.assertEqual("view Source", pin.TypeLabel)
		self.assertTrue(pin.IsBus)


class Kinds(Testcase):
	def test_Clock(self) -> None:
		converted = pins(PortSimpleSignalInterfaceItem(("clk", "Clock"), Mode.In, subtype("std_logic")))

		for name in ("clk", "Clock"):
			with self.subTest(port=name):
				self.assertIs(PinKind.Clock, converted[name].Kind)

	def test_Reset(self) -> None:
		converted = pins(PortSimpleSignalInterfaceItem(("rst", "Reset", "RESET_N"), Mode.In, subtype("std_logic")))

		for name in ("rst", "Reset", "RESET_N"):
			with self.subTest(port=name):
				self.assertIs(PinKind.Reset, converted[name].Kind)

	def test_Signal(self) -> None:
		"""Names only containing a clock's or reset's name are ordinary pins."""
		converted = pins(PortSimpleSignalInterfaceItem(("Clock_n", "SysClock", "rst_sync"), Mode.In, subtype("std_logic")))

		for name in ("Clock_n", "SysClock", "rst_sync"):
			with self.subTest(port=name):
				self.assertIs(PinKind.Signal, converted[name].Kind)


class Inverted(Testcase):
	def test_Inverted(self) -> None:
		converted = pins(PortSimpleSignalInterfaceItem(("reset_n", "CS_N", "WE_n"), Mode.In, subtype("std_logic")))

		for name in ("reset_n", "CS_N", "WE_n"):
			with self.subTest(port=name):
				self.assertTrue(converted[name].IsInverted)

	def test_NotInverted(self) -> None:
		converted = pins(PortSimpleSignalInterfaceItem(("Enable", "nReset", "n"), Mode.In, subtype("std_logic")))

		for name in ("Enable", "nReset", "n"):
			with self.subTest(port=name):
				self.assertFalse(converted[name].IsInverted)


class Bus(Testcase):
	def test_ConstrainedArray(self) -> None:
		pin = pins(PortSimpleSignalInterfaceItem(("Value", ), Mode.Out, vector("unsigned", 7)))["Value"]

		self.assertTrue(pin.IsBus)
		self.assertEqual("unsigned(7 downto 0)", pin.TypeLabel)

	def test_ArrayTypeMark(self) -> None:
		"""A type mark of an array type of ``std`` or ``ieee`` is a bus, also as selected name."""
		converted = pins(
			PortSimpleSignalInterfaceItem(("a", ), Mode.In, subtype("std_logic_vector")),
			PortSimpleSignalInterfaceItem(("b", ), Mode.In, subtype("BIT_VECTOR")),
			PortSimpleSignalInterfaceItem(
				("c", ), Mode.In, SimpleSubtypeSymbol(SelectedName("signed", SelectedName("numeric_std", SimpleName("ieee"))))
			),
		)

		for name in ("a", "b", "c"):
			with self.subTest(port=name):
				self.assertTrue(converted[name].IsBus)

	def test_Scalar(self) -> None:
		"""A scalar type mark, a constrained scalar subtype and an unknown type mark aren't buses."""
		converted = pins(
			PortSimpleSignalInterfaceItem(("a", ), Mode.In, subtype("std_logic")),
			PortSimpleSignalInterfaceItem(
				("b", ), Mode.In,
				ConstrainedScalarSubtypeSymbol(
					SimpleName("integer"), SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
				)
			),
			PortSimpleSignalInterfaceItem(("c", ), Mode.In, subtype("T_WORD")),
		)

		for name in ("a", "b", "c"):
			with self.subTest(port=name):
				self.assertFalse(converted[name].IsBus)
