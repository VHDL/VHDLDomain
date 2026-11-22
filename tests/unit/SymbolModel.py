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
"""Unit tests for the data model of an interface symbol."""
from pyTooling.Testing import Testcase

from VHDLDomain.Symbol import InterfaceSymbol, Parameter, ParameterGroup, Pin, PinGroup, PinKind, PinSide


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Symbol(Testcase):
	def test_Name(self) -> None:
		symbol = InterfaceSymbol("fifo")

		self.assertEqual("fifo", symbol.Name)
		self.assertEqual([], symbol.ParameterGroups)
		self.assertEqual([], symbol.PinGroups)

	def test_Name_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceSymbol(None)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

	def test_Name_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			InterfaceSymbol(5)

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Name_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceSymbol("")

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_GroupOrder(self) -> None:
		"""Groups append themselves to their symbol in creation order."""
		symbol = InterfaceSymbol("fifo")
		first =  PinGroup(parent=symbol)
		second = PinGroup("In", parent=symbol)
		third =  ParameterGroup("Sizes", parent=symbol)
		fourth = ParameterGroup(parent=symbol)

		self.assertEqual([first, second], symbol.PinGroups)
		self.assertEqual([third, fourth], symbol.ParameterGroups)


class ParameterGroups(Testcase):
	def test_Unnamed(self) -> None:
		symbol = InterfaceSymbol("fifo")
		group =  ParameterGroup(parent=symbol)

		self.assertIsNone(group.Name)
		self.assertIs(symbol, group.Parent)
		self.assertEqual([], group.Parameters)

	def test_Named(self) -> None:
		group = ParameterGroup("Sizes", parent=InterfaceSymbol("fifo"))

		self.assertEqual("Sizes", group.Name)

	def test_Name_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			ParameterGroup(5, parent=InterfaceSymbol("fifo"))

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Parent_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ParameterGroup(parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_Parent_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			ParameterGroup(parent=PinGroup(parent=InterfaceSymbol("fifo")))

		self.assertEqual("Parameter 'parent' is not of type 'InterfaceSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'VHDLDomain.Symbol.PinGroup'."], context.exception.__notes__)

	def test_ParameterOrder(self) -> None:
		"""Parameters append themselves to their group in creation order."""
		group =  ParameterGroup(parent=InterfaceSymbol("fifo"))
		first =  Parameter("DEPTH", "positive", "16", parent=group)
		second = Parameter("DATA_BITS", "positive", parent=group)

		self.assertEqual([first, second], group.Parameters)


class Parameters(Testcase):
	_group: ParameterGroup

	def setUp(self) -> None:
		self._group = ParameterGroup(parent=InterfaceSymbol("fifo"))

	def test_Parameter(self) -> None:
		parameter = Parameter("DEPTH", "positive", "16", parent=self._group)

		self.assertEqual("DEPTH", parameter.Name)
		self.assertEqual("positive", parameter.TypeLabel)
		self.assertEqual("16", parameter.DefaultValue)
		self.assertIs(self._group, parameter.Parent)

	def test_WithoutDefault(self) -> None:
		parameter = Parameter("DEPTH", "positive", parent=self._group)

		self.assertIsNone(parameter.DefaultValue)

	def test_Name_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Parameter(None, "positive", parent=self._group)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

	def test_Name_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Parameter(5, "positive", parent=self._group)

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Name_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			Parameter("", "positive", parent=self._group)

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_TypeLabel_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Parameter("DEPTH", None, parent=self._group)

		self.assertEqual("Parameter 'typeLabel' is None.", str(context.exception))

	def test_TypeLabel_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Parameter("DEPTH", 5, parent=self._group)

		self.assertEqual("Parameter 'typeLabel' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_DefaultValue_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Parameter("DEPTH", "positive", 16, parent=self._group)

		self.assertEqual("Parameter 'defaultValue' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Parent_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Parameter("DEPTH", "positive", parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_Parent_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Parameter("DEPTH", "positive", parent=self._group.Parent)

		self.assertEqual("Parameter 'parent' is not of type 'ParameterGroup'.", str(context.exception))
		self.assertEqual(["Got type 'VHDLDomain.Symbol.InterfaceSymbol'."], context.exception.__notes__)


class PinGroups(Testcase):
	def test_Unnamed(self) -> None:
		symbol = InterfaceSymbol("fifo")
		group =  PinGroup(parent=symbol)

		self.assertIsNone(group.Name)
		self.assertIs(symbol, group.Parent)
		self.assertEqual([], group.Pins)

	def test_Named(self) -> None:
		group = PinGroup("In", parent=InterfaceSymbol("fifo"))

		self.assertEqual("In", group.Name)

	def test_Name_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			PinGroup(5, parent=InterfaceSymbol("fifo"))

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Parent_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			PinGroup(parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_Parent_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			PinGroup(parent=ParameterGroup(parent=InterfaceSymbol("fifo")))

		self.assertEqual("Parameter 'parent' is not of type 'InterfaceSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'VHDLDomain.Symbol.ParameterGroup'."], context.exception.__notes__)

	def test_PinOrder(self) -> None:
		"""Pins append themselves to their group in creation order, whatever their side."""
		group =  PinGroup(parent=InterfaceSymbol("fifo"))
		first =  Pin("In_Valid", "std_logic", PinSide.Left, parent=group)
		second = Pin("In_Ack", "std_logic", PinSide.Right, parent=group)
		third =  Pin("In_Data", "std_logic_vector", PinSide.Left, parent=group)

		self.assertEqual([first, second, third], group.Pins)


class Pins(Testcase):
	_group: PinGroup

	def setUp(self) -> None:
		self._group = PinGroup(parent=InterfaceSymbol("fifo"))

	def test_Defaults(self) -> None:
		pin = Pin("In_Valid", "std_logic", PinSide.Left, parent=self._group)

		self.assertEqual("In_Valid", pin.Name)
		self.assertEqual("std_logic", pin.TypeLabel)
		self.assertIs(PinSide.Left, pin.Side)
		self.assertIs(PinKind.Signal, pin.Kind)
		self.assertFalse(pin.IsBus)
		self.assertFalse(pin.IsInverted)
		self.assertIs(self._group, pin.Parent)

	def test_Flags(self) -> None:
		pin = Pin("Data_n", "std_logic_vector", PinSide.Right, PinKind.Reset, True, True, parent=self._group)

		self.assertIs(PinSide.Right, pin.Side)
		self.assertIs(PinKind.Reset, pin.Kind)
		self.assertTrue(pin.IsBus)
		self.assertTrue(pin.IsInverted)

	def test_Name_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin(None, "std_logic", PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

	def test_Name_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin(5, "std_logic", PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Name_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("", "std_logic", PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_TypeLabel_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", None, PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'typeLabel' is None.", str(context.exception))

	def test_TypeLabel_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", 5, PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'typeLabel' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Side_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", "std_logic", None, parent=self._group)

		self.assertEqual("Parameter 'side' is None.", str(context.exception))

	def test_Side_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", "std_logic", "Left", parent=self._group)

		self.assertEqual("Parameter 'side' is not of type 'PinSide'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Kind_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", "std_logic", PinSide.Left, None, parent=self._group)

		self.assertEqual("Parameter 'kind' is None.", str(context.exception))

	def test_Kind_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", "std_logic", PinSide.Left, PinSide.Left, parent=self._group)

		self.assertEqual("Parameter 'kind' is not of type 'PinKind'.", str(context.exception))
		self.assertEqual(["Got type 'VHDLDomain.Symbol.PinSide'."], context.exception.__notes__)

	def test_IsBus_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", "std_logic", PinSide.Left, isBus=None, parent=self._group)

		self.assertEqual("Parameter 'isBus' is None.", str(context.exception))

	def test_IsBus_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", "std_logic", PinSide.Left, isBus=1, parent=self._group)

		self.assertEqual("Parameter 'isBus' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_IsInverted_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", "std_logic", PinSide.Left, isInverted=None, parent=self._group)

		self.assertEqual("Parameter 'isInverted' is None.", str(context.exception))

	def test_IsInverted_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", "std_logic", PinSide.Left, isInverted=1, parent=self._group)

		self.assertEqual("Parameter 'isInverted' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Parent_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Pin("clock", "std_logic", PinSide.Left, parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_Parent_WrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			Pin("clock", "std_logic", PinSide.Left, parent=self._group.Parent)

		self.assertEqual("Parameter 'parent' is not of type 'PinGroup'.", str(context.exception))
		self.assertEqual(["Got type 'VHDLDomain.Symbol.InterfaceSymbol'."], context.exception.__notes__)
