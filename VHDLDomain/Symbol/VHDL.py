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
Conversion of a VHDL entity or component, as modelled by pyVHDLModel, into an interface symbol.

The generics become the symbol's parameters, the ports its pins: a port of mode ``in`` on the left edge, of mode
``out``, ``inout``, ``buffer`` or ``linkage`` and a port with a mode view on the right edge.
"""
from __future__                  import annotations

from typing                      import Callable, ClassVar, Optional as Nullable

from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Decorators        import export
from pyTooling.MetaClasses       import ExtendedType

from pyVHDLModel.Base            import Mode
from pyVHDLModel.DesignUnit      import Component, Entity
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Interface       import GenericFunctionInterfaceItem, GenericInterfaceItemMixin, \
                                        GenericPackageInterfaceItem, GenericTypeInterfaceItem, \
                                        SingleGenericConstantDeclaration, SingleGenericDeclarationMixin, \
                                        SinglePortDeclarationMixin, SinglePortSimpleSignalDeclaration
from pyVHDLModel.Symbol          import ConstrainedCompositeSubtypeSymbol, SimpleSubtypeSymbol, Symbol

from VHDLDomain.Symbol           import InterfaceSymbol, Parameter, ParameterGroup, Pin, PinGroup, PinKind, PinSide


@export
class VHDLConverter(metaclass=ExtendedType, slots=True):
	"""
	Converts a VHDL entity or component into an interface symbol.

	Each identifier of a generic or port declaration becomes a parameter or pin of its own: ``a, b : in bit`` gives two
	pins. A generic constant's parameter shows the subtype and the default value; a generic type, package, function or
	procedure shows its VHDL keyword as type. A port's pin shows the subtype, or ``view`` and the mode view's name.

	A pin's properties follow from the port:

	* Side: mode ``in`` (or no mode) on the left edge, all others on the right edge.
	* Kind: :attr:`~VHDLDomain.Symbol.PinKind.Clock` for the name ``clk`` or ``clock``,
	  :attr:`~VHDLDomain.Symbol.PinKind.Reset` for ``rst``, ``reset`` or ``reset_n`` (case-insensitive).
	* Inverted: a name ending in ``_n`` (case-insensitive).
	* Bus: a constrained array or record subtype - as ``unsigned(7 downto 0)`` -, a type mark of
	  :attr:`_ARRAY_TYPES`, or a port with a mode view.
	"""

	#: The array types of the predefined libraries ``std`` and ``ieee``, by normalized name: a port of such a type mark
	#: is a bus.
	_ARRAY_TYPES: ClassVar[frozenset[str]] = frozenset({
		"bit_vector", "boolean_vector", "integer_vector", "real_vector", "time_vector", "string",
		"std_logic_vector", "std_ulogic_vector",
		"signed", "unsigned", "unresolved_signed", "unresolved_unsigned", "u_signed", "u_unsigned",
		"sfixed", "ufixed", "unresolved_sfixed", "unresolved_ufixed", "u_sfixed", "u_ufixed",
		"float", "float32", "float64", "float128", "unresolved_float", "unresolved_float32", "unresolved_float64",
		"unresolved_float128", "u_float", "u_float32", "u_float64", "u_float128",
	})

	_formatter: Callable[[object], str]  #: Writes a model element - a subtype, an expression - as VHDL source text.

	def __init__(self, formatter: Nullable[Callable[[object], str]] = None) -> None:
		"""
		Initializes a converter writing subtypes and default values by a formatter.

		:param formatter:  Optional, a function writing a model element as VHDL source text. Default: the
		                   :meth:`~pyVHDLModel.Formatting.VHDL.VHDLWriter.Format` method of a
		                   :class:`~pyVHDLModel.Formatting.VHDL.VHDLWriter`.
		:raises TypeError: If parameter 'formatter' is not callable.
		"""
		if formatter is not None and not callable(formatter):
			ex = TypeError("Parameter 'formatter' is not callable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(formatter)}'.")
			raise ex

		self._formatter = VHDLWriter().Format if formatter is None else formatter  # type: ignore[assignment]

	def Convert(self, unit: Entity | Component) -> InterfaceSymbol:
		"""
		Convert an entity or a component into an interface symbol.

		The symbol has one unnamed parameter group of all generics and one unnamed pin group of all ports, in declaration
		order; a unit without generics or ports has no parameter group or pin group.

		:param unit:        The entity or component.
		:returns:           The interface symbol, named as the unit.
		:raises ValueError: If parameter 'unit' is None.
		:raises TypeError:  If parameter 'unit' is not of type :class:`~pyVHDLModel.DesignUnit.Entity` or
		                    :class:`~pyVHDLModel.DesignUnit.Component`.
		"""
		if unit is None:
			raise ValueError("Parameter 'unit' is None.")
		elif not isinstance(unit, (Entity, Component)):
			ex = TypeError("Parameter 'unit' is not of type 'Entity' or 'Component'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(unit)}'.")
			raise ex

		symbol = InterfaceSymbol(unit.Identifier)

		# TODO: one parameter group per generic group, once pyVHDLModel attaches generic groups to entities and components.
		if len(unit.GenericItems) > 0:
			parameterGroup = ParameterGroup(parent=symbol)
			for generic in unit.IterateSingleGenericDeclarations():
				self._Parameter(generic, parameterGroup)

		# TODO: one pin group per port group, once pyVHDLModel attaches port groups to entities and components.
		if len(unit.PortItems) > 0:
			pinGroup = PinGroup(parent=symbol)
			for port in unit.IterateSinglePortDeclarations():
				self._Pin(port, pinGroup)

		return symbol

	def _Parameter(
		self,
		generic: SingleGenericDeclarationMixin | GenericInterfaceItemMixin,
		group:   ParameterGroup
	) -> None:
		"""
		Convert a generic into a parameter of a group.

		:param generic: A generic constant's single declaration, or a generic type, package or subprogram.
		:param group:   The parameter group.
		"""
		defaultValue: Nullable[str] = None
		if isinstance(generic, SingleGenericConstantDeclaration):
			typeLabel = self._formatter(generic.Subtype)
			if generic.DefaultExpression is not None:
				defaultValue = self._formatter(generic.DefaultExpression)
		elif isinstance(generic, GenericTypeInterfaceItem):
			typeLabel = "type"
		elif isinstance(generic, GenericPackageInterfaceItem):
			typeLabel = "package"
		elif isinstance(generic, GenericFunctionInterfaceItem):
			typeLabel = "function"
		else:
			typeLabel = "procedure"

		Parameter(generic.Identifier, typeLabel, defaultValue, parent=group)

	def _Pin(self, port: SinglePortDeclarationMixin, group: PinGroup) -> None:
		"""
		Convert a port into a pin of a group.

		:param port:  A port's single declaration.
		:param group: The pin group.
		"""
		if isinstance(port, SinglePortSimpleSignalDeclaration):
			typeLabel = self._formatter(port.Subtype)
			side =      PinSide.Left if port.Mode in (Mode.Default, Mode.In) else PinSide.Right
			isBus =     self._IsBus(port.Subtype)
		else:
			typeLabel = f"view {self._formatter(port.ModeViewIndication)}"  # type: ignore[attr-defined]
			side =      PinSide.Right
			isBus =     True

		name = port.NormalizedIdentifier
		if name in ("clk", "clock"):
			kind = PinKind.Clock
		elif name in ("rst", "reset", "reset_n"):
			kind = PinKind.Reset
		else:
			kind = PinKind.Signal

		Pin(port.Identifier, typeLabel, side, kind, isBus, name.endswith("_n"), parent=group)

	@classmethod
	def _IsBus(cls, subtype: Symbol) -> bool:
		"""
		Check if a port's subtype carries several bits.

		:param subtype: The port's subtype indication.
		:returns:       ``True``, if the subtype is a constrained array or record subtype, or a type mark of
		                :attr:`_ARRAY_TYPES`.
		"""
		if isinstance(subtype, ConstrainedCompositeSubtypeSymbol):
			return True
		elif isinstance(subtype, SimpleSubtypeSymbol):
			return subtype.Name.NormalizedIdentifier in cls._ARRAY_TYPES

		return False
