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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
**A Sphinx domain providing VHDL language support.**

This module contains all the indices of the VHDL domain.
"""
from typing import Iterable, Optional as Nullable, List, Tuple, Dict

from pyGHDL.dom.NonStandard import Design
from pyTooling.Decorators import export
from pyVHDLModel import DesignUnitKind
from sphinx.domains import Index, IndexEntry


@export
class BaseIndex(Index):
	pass


@export
class LibraryIndex(BaseIndex):
	"""
	An index for VHDL libraries.
	"""

	name =      "libindex"
	localname = "Library Index"
	shortname = "Libraries"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		designs: Dict[str, Design] = self.domain.data["designs"]
		design = designs["StopWatch"]
		for library in design.Libraries.values():
			entries = []
			for entity in library.Entities.values():
				entryName = entity.Identifier
				entryKind = 0 if len(entity.Architectures) == 1 else 1
				document = f"{entity.Library.Identifier}/{entity.Identifier}"
				link = f"{entity.Library.Identifier}-{entity.Identifier}"
				entries.append((entryName, entryKind, document, link, document, "", entity.Documentation))
				if entryKind == 1:
					for architecture in entity.Architectures.values():
						architectureName = architecture.Identifier
						architectureKind = 2
						doc = f"{entity.Library.Identifier}/{entity.Identifier}-{architecture.Identifier}"
						lnk = f"{entity.Library.Identifier}-{entity.Identifier}-{architecture.Identifier}"
						entries.append((architectureName, architectureKind, doc, lnk, doc, "", architecture.Documentation))

			group = (library.Identifier, entries)
			result.append(group)

		return result, True


@export
class DocumentIndex(BaseIndex):
	"""
	An index for VHDL documents.
	"""

	name =      "fileindex"
	localname = "Document Index"
	shortname = "Documents"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		designs: Dict[str, Design] = self.domain.data["designs"]
		design = designs["StopWatch"]
		for library in design.Libraries.values():
			entries = []
			for entity in library.Entities.values():
				entryName = entity.Identifier
				entryKind = 0 if len(entity.Architectures) == 1 else 1
				document = f"{entity.Library.Identifier}/{entity.Identifier}"
				link = f"{entity.Library.Identifier}-{entity.Identifier}"
				entries.append((entryName, entryKind, document, link, document, "", entity.Documentation))
				if entryKind == 1:
					for architecture in entity.Architectures.values():
						architectureName = architecture.Identifier
						architectureKind = 2
						doc = f"{entity.Library.Identifier}/{entity.Identifier}-{architecture.Identifier}"
						lnk = f"{entity.Library.Identifier}-{entity.Identifier}-{architecture.Identifier}"
						entries.append((architectureName, architectureKind, doc, lnk, doc, "", architecture.Documentation))

			group = (library.Identifier, entries)
			result.append(group)

		return result, True


@export
class ComponentIndex(BaseIndex):
	"""
	An index for VHDL components.
	"""

	name =      "compindex"
	localname = "Component Index"
	shortname = "Components"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		designs: Dict[str, Design] = self.domain.data["designs"]
		design = designs["StopWatch"]
		for library in design.Libraries.values():
			entries = []
			for entity in library.Entities.values():
				entryName = entity.Identifier
				entryKind = 0 if len(entity.Architectures) == 1 else 1
				document = f"{entity.Library.Identifier}/{entity.Identifier}"
				link = f"{entity.Library.Identifier}-{entity.Identifier}"
				entries.append((entryName, entryKind, document, link, document, "", entity.Documentation))
				if entryKind == 1:
					for architecture in entity.Architectures.values():
						architectureName = architecture.Identifier
						architectureKind = 2
						doc = f"{entity.Library.Identifier}/{entity.Identifier}-{architecture.Identifier}"
						lnk = f"{entity.Library.Identifier}-{entity.Identifier}-{architecture.Identifier}"
						entries.append((architectureName, architectureKind, doc, lnk, doc, "", architecture.Documentation))

			group = (library.Identifier, entries)
			result.append(group)

		return result, True


@export
class PackageIndex(BaseIndex):
	"""
	An index for VHDL packages.
	"""

	name =      "packindex"
	localname = "Package Index"
	shortname = "Packages"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		designs: Dict[str, Design] = self.domain.data["designs"]
		design = designs["StopWatch"]
		for library in design.Libraries.values():
			entries = []
			for package in library.Packages.values():
				entryName = package.Identifier
				entryKind = 0
				document = f"{package.Library.Identifier}/{package.Identifier}"
				link = f"{package.Library.Identifier}-{package.Identifier}"
				entries.append((entryName, entryKind, document, link, document, "", package.Documentation))

			group = (library.Identifier, entries)
			result.append(group)

		return result, True


@export
class SubprogramIndex(BaseIndex):
	"""
	An index for VHDL functions or procedures.
	"""

	name =      "subindex"
	localname = "Subprogram Index"
	shortname = "Subprograms"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		entry = ("binary2onehot", 0, "lib_Utilities/binary2onehot", "lib_Utilities-binary2onehot", "lib_Utilities/binary2onehot", "", "Conversion from binary to onehot code.")
		group = ("B", [entry])

		result.append(group)

		return result, True


@export
class TypeIndex(BaseIndex):
	"""
	An index for types and subtypes in VHDL.
	"""

	name =      "typeindex"
	localname = "Type Index"
	shortname = "Types"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		entry = ("BCD", 0, "lib_Utilities/BCD", "lib_Utilities-BCD", "lib_Utilities/BCD", "", "Binary coded decimal.")
		group = ("B", [entry])

		result.append(group)

		return result, True
