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
"""
Interface symbols of three entities of the StopWatch example, built with the data model of :mod:`VHDLDomain.Symbol`.

The documentation's :file:`conf.py` renders them as SVG, PNG and TikZ.
"""
from VHDLDomain.Symbol import InterfaceSymbol, Parameter, ParameterGroup, Pin, PinGroup, PinKind, PinSide


def Counter() -> InterfaceSymbol:
	"""
	Build the symbol of entity ``Counter``: two generics, a clock and a reset input, a bus output.

	:returns: The symbol ``Counter``.
	"""
	symbol =     InterfaceSymbol("Counter")
	parameters = ParameterGroup(parent=symbol)
	Parameter("MODULO", "positive", parent=parameters)
	Parameter("BITS", "natural", "log2(MODULO)", parent=parameters)

	pins = PinGroup(parent=symbol)
	Pin("Clock", "std_logic", PinSide.Left, PinKind.Clock, parent=pins)
	Pin("Reset", "std_logic", PinSide.Left, PinKind.Reset, parent=pins)
	Pin("Enable", "std_logic", PinSide.Left, parent=pins)
	Pin("Value", "unsigned(BITS - 1 downto 0)", PinSide.Right, isBus=True, parent=pins)
	Pin("WrapAround", "std_logic", PinSide.Right, parent=pins)

	return symbol


def Seg7Display() -> InterfaceSymbol:
	"""
	Build the symbol of entity ``seg7_Display``: three generics, a clock input, bus inputs and bus outputs.

	:returns: The symbol ``seg7_Display``.
	"""
	symbol =     InterfaceSymbol("seg7_Display")
	parameters = ParameterGroup(parent=symbol)
	Parameter("CLOCK_PERIOD", "time", "10 ns", parent=parameters)
	Parameter("REFRESH_RATE", "time", "200 us", parent=parameters)
	Parameter("DIGITS", "positive", parent=parameters)

	pins = PinGroup(parent=symbol)
	Pin("Clock", "std_logic", PinSide.Left, PinKind.Clock, parent=pins)
	Pin("DigitValues", "T_BCD_Vector(DIGITS - 1 downto 0)", PinSide.Left, isBus=True, parent=pins)
	Pin("DotValues", "std_logic_vector(DIGITS - 1 downto 0)", PinSide.Left, isBus=True, parent=pins)
	Pin("Seg7_Segments", "std_logic_vector(7 downto 0)", PinSide.Right, isBus=True, parent=pins)
	Pin("Seg7_Selects", "std_logic_vector(DIGITS - 1 downto 0)", PinSide.Right, isBus=True, parent=pins)

	return symbol


def TopLevel() -> InterfaceSymbol:
	"""
	Build the symbol of entity ``toplevel``: one generic, a low-active input and low-active bus outputs.

	:returns: The symbol ``toplevel``.
	"""
	symbol =     InterfaceSymbol("toplevel")
	parameters = ParameterGroup(parent=symbol)
	Parameter("CLOCK_PERIOD", "time", "10 ns", parent=parameters)

	pins = PinGroup(parent=symbol)
	Pin("NexysA7_SystemClock", "std_logic", PinSide.Left, parent=pins)
	Pin("NexysA7_GPIO_Button_Reset_n", "std_logic", PinSide.Left, isInverted=True, parent=pins)
	Pin("NexysA7_GPIO_Button", "std_logic_vector(0 downto 0)", PinSide.Left, isBus=True, parent=pins)
	Pin(
		"NexysA7_GPIO_Seg7_Cathode_n", "std_logic_vector(7 downto 0)", PinSide.Right, isBus=True, isInverted=True,
		parent=pins
	)
	Pin(
		"NexysA7_GPIO_Seg7_Anode_n", "std_logic_vector(7 downto 0)", PinSide.Right, isBus=True, isInverted=True,
		parent=pins
	)

	return symbol
