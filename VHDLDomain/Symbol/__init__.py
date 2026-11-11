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
A data model of an interface symbol, independent of the format drawing it.

An interface symbol shows a design unit's interface as a box: the parameters (VHDL generics) in a box on top, the pins
(VHDL ports) on the left and right edge. Parameters and pins are arranged in groups; a group is a horizontal section of
the box, which may carry a name. A renderer turns the description into a picture, e.g. SVG, TikZ or PNG.

The model knows nothing about VHDL: :mod:`VHDLDomain` fills it from an entity or a component.
"""
from __future__            import annotations

from enum                  import Enum
from typing                import ClassVar, Generic, Optional as Nullable, TypeVar

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType


@export
class PinSide(Enum):
	"""The edge of the symbol's box a pin is drawn on."""

	Left =  0  #: Left edge, e.g. for inputs.
	Right = 1  #: Right edge, e.g. for outputs.


@export
class PinKind(Enum):
	"""
	The role of a pin, which a renderer may mark.

	A renderer draws a clock input with a triangle, for example.
	"""

	Signal = 0  #: An ordinary pin.
	Clock =  1  #: A clock input.
	Reset =  2  #: A reset input.


ParentType = TypeVar("ParentType", bound="InterfaceSymbol | ParameterGroup | PinGroup")
"""The type of an element's parent: the symbol or a group."""


@export
class InterfaceSymbol(metaclass=ExtendedType, slots=True):
	"""
	An interface symbol: a named box with parameter groups on top and pin groups on its edges.

	Groups and their elements are created with this symbol as (grand)parent; they append themselves in creation order.
	"""
	_name:            str                  #: Name of the symbol, e.g. the entity's name.
	_parameterGroups: list[ParameterGroup] #: Parameter groups, in declaration order.
	_pinGroups:       list[PinGroup]       #: Pin groups, in declaration order.

	def __init__(self, name: str) -> None:
		"""
		Initializes an interface symbol without groups.

		:param name:        Name of the symbol.
		:raises ValueError: If parameter 'name' is None.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		self._name =            name
		self._parameterGroups = []
		self._pinGroups =       []

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the symbol's name (:attr:`_name`).

		:returns: Name of the symbol.
		"""
		return self._name

	@readonly
	def ParameterGroups(self) -> list[ParameterGroup]:
		"""
		Read-only property to access the parameter groups (:attr:`_parameterGroups`).

		:returns: List of parameter groups, in declaration order.
		"""
		return self._parameterGroups

	@readonly
	def PinGroups(self) -> list[PinGroup]:
		"""
		Read-only property to access the pin groups (:attr:`_pinGroups`).

		:returns: List of pin groups, in declaration order.
		"""
		return self._pinGroups


@export
class Element(Generic[ParentType], metaclass=ExtendedType, slots=True):
	"""
	Base-class of every element below the symbol: a reference to the symbol or group containing it.

	A derived class names the accepted parent types in :attr:`_PARENT_TYPE` and appends itself to the parent's
	collection, after setting its fields.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]]  #: The types a parent may have; assigned by each derived class.

	_parent: ParentType  #: The symbol or group containing this element.

	def __init__(self, *, parent: ParentType) -> None:
		"""
		Initializes an element with its parent.

		:param parent:      The symbol or group containing this element.
		:raises ValueError: If parameter 'parent' is None.
		:raises TypeError:  If parameter 'parent' is not of a type this class declares in :attr:`_PARENT_TYPE`.
		"""
		if parent is None:
			raise ValueError("Parameter 'parent' is None.")
		elif not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex =        TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@readonly
	def Parent(self) -> ParentType:
		"""
		Read-only property to access the symbol or group containing this element (:attr:`_parent`).

		:returns: The parent.
		"""
		return self._parent


@export
class ParameterGroup(Element[InterfaceSymbol]):
	"""
	A section of the parameter box, optionally named.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]] = (InterfaceSymbol, )  #: A parameter group is in a symbol.

	_name:       Nullable[str]     #: Name of the group, or ``None`` for an unnamed group.
	_parameters: list[Parameter]   #: Parameters, in declaration order.

	def __init__(self, name: Nullable[str] = None, *, parent: InterfaceSymbol) -> None:
		"""
		Initializes a parameter group without parameters and appends it to its symbol.

		:param name:        Optional, name of the group. Default: ``None`` (unnamed).
		:param parent:      The symbol the group belongs to.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'parent' is None.
		:raises TypeError:  If parameter 'parent' is not of type :class:`InterfaceSymbol`.
		"""
		super().__init__(parent=parent)

		if name is not None and not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name =       name
		self._parameters = []
		parent._parameterGroups.append(self)

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property to access the group's name (:attr:`_name`).

		:returns: Name of the group, or ``None`` if unnamed.
		"""
		return self._name

	@readonly
	def Parameters(self) -> list[Parameter]:
		"""
		Read-only property to access the parameters (:attr:`_parameters`).

		:returns: List of parameters, in declaration order.
		"""
		return self._parameters


@export
class Parameter(Element[ParameterGroup]):
	"""
	A parameter of the symbol: a name, a type label and an optional default value.

	A VHDL generic becomes a parameter.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]] = (ParameterGroup, )  #: A parameter is in a parameter group.

	_name:         str             #: Name of the parameter.
	_typeLabel:    str             #: Type as written, e.g. ``positive``.
	_defaultValue: Nullable[str]   #: Default value as written, or ``None``.

	def __init__(self, name: str, typeLabel: str, defaultValue: Nullable[str] = None, *, parent: ParameterGroup) -> None:
		"""
		Initializes a parameter and appends it to its group.

		:param name:         Name of the parameter.
		:param typeLabel:    Type as written.
		:param defaultValue: Optional, default value as written. Default: ``None``.
		:param parent:       The group the parameter belongs to.
		:raises ValueError:  If parameter 'name' is None.
		:raises TypeError:   If parameter 'name' is not of type :class:`str`.
		:raises ValueError:  If parameter 'name' is empty.
		:raises ValueError:  If parameter 'typeLabel' is None.
		:raises TypeError:   If parameter 'typeLabel' is not of type :class:`str`.
		:raises TypeError:   If parameter 'defaultValue' is not of type :class:`str`.
		:raises ValueError:  If parameter 'parent' is None.
		:raises TypeError:   If parameter 'parent' is not of type :class:`ParameterGroup`.
		"""
		super().__init__(parent=parent)

		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if typeLabel is None:
			raise ValueError("Parameter 'typeLabel' is None.")
		elif not isinstance(typeLabel, str):
			ex = TypeError("Parameter 'typeLabel' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(typeLabel)}'.")
			raise ex

		if defaultValue is not None and not isinstance(defaultValue, str):
			ex = TypeError("Parameter 'defaultValue' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(defaultValue)}'.")
			raise ex

		self._name =         name
		self._typeLabel =    typeLabel
		self._defaultValue = defaultValue
		parent._parameters.append(self)

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the parameter's name (:attr:`_name`).

		:returns: Name of the parameter.
		"""
		return self._name

	@readonly
	def TypeLabel(self) -> str:
		"""
		Read-only property to access the parameter's type as written (:attr:`_typeLabel`).

		:returns: Type label.
		"""
		return self._typeLabel

	@readonly
	def DefaultValue(self) -> Nullable[str]:
		"""
		Read-only property to access the parameter's default value as written (:attr:`_defaultValue`).

		:returns: Default value, or ``None`` if the parameter has none.
		"""
		return self._defaultValue


@export
class PinGroup(Element[InterfaceSymbol]):
	"""
	A horizontal section of the symbol's box, optionally named; its pins sit on the left and right edge.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]] = (InterfaceSymbol, )  #: A pin group is in a symbol.

	_name: Nullable[str]  #: Name of the group, or ``None`` for an unnamed group.
	_pins: list[Pin]      #: Pins, in declaration order.

	def __init__(self, name: Nullable[str] = None, *, parent: InterfaceSymbol) -> None:
		"""
		Initializes a pin group without pins and appends it to its symbol.

		:param name:        Optional, name of the group. Default: ``None`` (unnamed).
		:param parent:      The symbol the group belongs to.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'parent' is None.
		:raises TypeError:  If parameter 'parent' is not of type :class:`InterfaceSymbol`.
		"""
		super().__init__(parent=parent)

		if name is not None and not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name = name
		self._pins = []
		parent._pinGroups.append(self)

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property to access the group's name (:attr:`_name`).

		:returns: Name of the group, or ``None`` if unnamed.
		"""
		return self._name

	@readonly
	def Pins(self) -> list[Pin]:
		"""
		Read-only property to access the pins (:attr:`_pins`).

		:returns: List of pins, in declaration order.
		"""
		return self._pins


@export
class Pin(Element[PinGroup]):
	"""
	A pin of the symbol: a name and a type label on one edge of the box.

	A VHDL port becomes a pin.
	A bus pin (:attr:`IsBus`) is drawn as a thick line; an inverted pin (:attr:`IsInverted`, low-active) with an inversion
	circle at the box edge.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]] = (PinGroup, )  #: A pin is in a pin group.

	_name:       str       #: Name of the pin.
	_typeLabel:  str       #: Type as written, e.g. ``std_logic_vector(7 downto 0)``.
	_side:       PinSide   #: The edge of the box the pin is drawn on.
	_kind:       PinKind   #: The pin's role.
	_isBus:      bool      #: ``True``, if the pin carries several bits.
	_isInverted: bool      #: ``True``, if the pin is low-active.

	def __init__(
		self,
		name:       str,
		typeLabel:  str,
		side:       PinSide,
		kind:       PinKind = PinKind.Signal,
		isBus:      bool = False,
		isInverted: bool = False,
		*,
		parent:     PinGroup
	) -> None:
		"""
		Initializes a pin and appends it to its group.

		:param name:        Name of the pin.
		:param typeLabel:   Type as written.
		:param side:        The edge of the box the pin is drawn on.
		:param kind:        Optional, the pin's role. Default: :attr:`PinKind.Signal`.
		:param isBus:       Optional, ``True`` if the pin carries several bits. Default: ``False``.
		:param isInverted:  Optional, ``True`` if the pin is low-active. Default: ``False``.
		:param parent:      The group the pin belongs to.
		:raises ValueError: If parameter 'name' is None.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises ValueError: If parameter 'typeLabel' is None.
		:raises TypeError:  If parameter 'typeLabel' is not of type :class:`str`.
		:raises ValueError: If parameter 'side' is None.
		:raises TypeError:  If parameter 'side' is not of type :class:`PinSide`.
		:raises ValueError: If parameter 'kind' is None.
		:raises TypeError:  If parameter 'kind' is not of type :class:`PinKind`.
		:raises ValueError: If parameter 'isBus' is None.
		:raises TypeError:  If parameter 'isBus' is not of type :class:`bool`.
		:raises ValueError: If parameter 'isInverted' is None.
		:raises TypeError:  If parameter 'isInverted' is not of type :class:`bool`.
		:raises ValueError: If parameter 'parent' is None.
		:raises TypeError:  If parameter 'parent' is not of type :class:`PinGroup`.
		"""
		super().__init__(parent=parent)

		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if typeLabel is None:
			raise ValueError("Parameter 'typeLabel' is None.")
		elif not isinstance(typeLabel, str):
			ex = TypeError("Parameter 'typeLabel' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(typeLabel)}'.")
			raise ex

		if side is None:
			raise ValueError("Parameter 'side' is None.")
		elif not isinstance(side, PinSide):
			ex = TypeError("Parameter 'side' is not of type 'PinSide'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(side)}'.")
			raise ex

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, PinKind):
			ex = TypeError("Parameter 'kind' is not of type 'PinKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex

		for flagName, flag in (
			("isBus",      isBus),
			("isInverted", isInverted)
		):
			if flag is None:
				raise ValueError(f"Parameter '{flagName}' is None.")
			elif not isinstance(flag, bool):
				ex = TypeError(f"Parameter '{flagName}' is not of type 'bool'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(flag)}'.")
				raise ex

		self._name =       name
		self._typeLabel =  typeLabel
		self._side =       side
		self._kind =       kind
		self._isBus =      isBus
		self._isInverted = isInverted
		parent._pins.append(self)

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the pin's name (:attr:`_name`).

		:returns: Name of the pin.
		"""
		return self._name

	@readonly
	def TypeLabel(self) -> str:
		"""
		Read-only property to access the pin's type as written (:attr:`_typeLabel`).

		:returns: Type label.
		"""
		return self._typeLabel

	@readonly
	def Side(self) -> PinSide:
		"""
		Read-only property to access the edge the pin is drawn on (:attr:`_side`).

		:returns: The pin's side.
		"""
		return self._side

	@readonly
	def Kind(self) -> PinKind:
		"""
		Read-only property to access the pin's role (:attr:`_kind`).

		:returns: The pin's kind.
		"""
		return self._kind

	@readonly
	def IsBus(self) -> bool:
		"""
		Check if the pin carries several bits (:attr:`_isBus`).

		:returns: ``True``, if the pin is a bus.
		"""
		return self._isBus

	@readonly
	def IsInverted(self) -> bool:
		"""
		Check if the pin is low-active (:attr:`_isInverted`).

		:returns: ``True``, if the pin is drawn with an inversion circle.
		"""
		return self._isInverted
