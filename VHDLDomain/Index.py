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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
The indices of the domain ``vhdl``: entities, packages, subprograms and types, as described by the directives.

An index lists the described objects - not every object of the designs -, grouped by the first letter of their name,
each linking to its description. An entry's extra information names where the object is: the library for a design
unit, the library and design unit for a declaration, preceded by the design if the documentation describes several.
A subprogram's entry shows its signature, so its overloads are told apart.

An index is a page of its own, referred to as ``:ref:`vhdl-<index name>```, e.g. ``:ref:`vhdl-entities```.
"""
from __future__           import annotations

from typing               import TYPE_CHECKING, ClassVar, Iterable, Optional as Nullable

from sphinx.domains       import Index, IndexEntry

from pyTooling.Decorators import export

if TYPE_CHECKING:  # pragma: no cover
	from VHDLDomain         import VHDLDomain


@export
class VHDLIndex(Index):
	"""
	Base-class of the indices of domain ``vhdl``: the described objects of some object types, grouped by first letter.

	A derived class names the index and the object types it lists.
	"""

	_OBJECT_TYPES: ClassVar[tuple[str, ...]]  #: The object types the index lists.

	def generate(self, docnames: Nullable[Iterable[str]] = None) -> tuple[list[tuple[str, list[IndexEntry]]], bool]:
		"""
		Create the index's entries.

		:param docnames: Optional, the documents whose objects are listed. Default: ``None``, all documents.
		:returns:        The entries grouped by first letter, sorted by name, and ``False``: the groups aren't collapsible.
		"""
		domain: VHDLDomain = self.domain  # type: ignore[assignment]
		documents = None if docnames is None else set(docnames)

		objects = []
		designs = set()
		for (objectType, _), (document, nodeID, qualifiedName) in domain.Objects.items():
			if objectType not in self._OBJECT_TYPES or (documents is not None and document not in documents):
				continue

			designName, library, name = qualifiedName.split(".", 2)
			unit, _, member = name.partition(".")
			objects.append((designName, library, unit, member, objectType, document, nodeID))
			designs.add(designName.lower())

		groups: dict[str, list[IndexEntry]] = {}
		for designName, library, unit, member, objectType, document, nodeID in objects:
			name = unit if member == "" else member
			location = library if member == "" else f"{library}.{unit}"
			if len(designs) > 1:
				location = f"{designName}.{location}"

			entry = IndexEntry(name, 0, document, nodeID, f"{objectType} in {location}", "", "")
			groups.setdefault(name[0].upper(), []).append(entry)

		content = [
			(letter, sorted(entries, key=lambda entry: (entry.name.lower(), entry.extra.lower())))
			for letter, entries in sorted(groups.items())
		]

		return content, False


@export
class EntityIndex(VHDLIndex):
	"""
	The index of the described entities: ``:ref:`vhdl-entities```.
	"""

	name =      "entities"      #: Name of the index, the label ``vhdl-entities``.
	localname = "Entity Index"  #: Title of the index.
	shortname = "Entities"      #: Short title of the index, as a link names it.

	_OBJECT_TYPES: ClassVar[tuple[str, ...]] = ("entity", )  #: The object types the index lists.


@export
class PackageIndex(VHDLIndex):
	"""
	The index of the described packages: ``:ref:`vhdl-packages```.
	"""

	name =      "packages"       #: Name of the index, the label ``vhdl-packages``.
	localname = "Package Index"  #: Title of the index.
	shortname = "Packages"       #: Short title of the index, as a link names it.

	_OBJECT_TYPES: ClassVar[tuple[str, ...]] = ("package", )  #: The object types the index lists.


@export
class SubprogramIndex(VHDLIndex):
	"""
	The index of the described functions and procedures: ``:ref:`vhdl-subprograms```.
	"""

	name =      "subprograms"       #: Name of the index, the label ``vhdl-subprograms``.
	localname = "Subprogram Index"  #: Title of the index.
	shortname = "Subprograms"       #: Short title of the index, as a link names it.

	_OBJECT_TYPES: ClassVar[tuple[str, ...]] = ("function", "procedure")  #: The object types the index lists.


@export
class TypeIndex(VHDLIndex):
	"""
	The index of the described types and subtypes: ``:ref:`vhdl-types```.
	"""

	name =      "types"       #: Name of the index, the label ``vhdl-types``.
	localname = "Type Index"  #: Title of the index.
	shortname = "Types"       #: Short title of the index, as a link names it.

	_OBJECT_TYPES: ClassVar[tuple[str, ...]] = ("type", "subtype")  #: The object types the index lists.
