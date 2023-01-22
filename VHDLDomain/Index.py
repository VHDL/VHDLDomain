from typing import Iterable, Optional as Nullable, List, Tuple

from pyGHDL.dom.NonStandard import Design
from pyTooling.Decorators import export
from pyVHDLModel import DesignUnitKind
from sphinx.domains import Index, IndexEntry


@export
class BaseIndex(Index):
	pass


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

		design: Design = DUMMY.VAR
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

		design: Design = DUMMY.VAR
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
