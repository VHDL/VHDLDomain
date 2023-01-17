from typing import Iterable, Optional as Nullable, List, Tuple

from pyGHDL.dom.NonStandard import Design
from pyTooling.Decorators import export
from pyVHDLModel import DesignUnitKind
from sphinx.domains import Index, IndexEntry


class DUMMY:
	VAR = None


@export
class ComponentIndex(Index):
	"""
	An index for VHDL components.
	"""

	name =      "compindex"
	localname = "Component Index"
	shortname = "Components"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		entries = []

		design: Design = DUMMY.VAR
		for entity in design.IterateDesignUnits(DesignUnitKind.Entity):
			entryName = entity.Identifier
			entryKind = 0
			document = f"{entity.Library.Identifier}/{entity.Identifier}"
			link = f"{entity.Library.Identifier}-{entity.Identifier}"
			entries.append((entryName, entryKind, document, link, document, "", entity.Documentation))

		group = ("C", entries)

		result.append(group)

		return result, True


@export
class PackageIndex(Index):
	"""
	An index for VHDL packages.
	"""

	name =      "packindex"
	localname = "Package Index"
	shortname = "Packages"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		entry = ("Utilities", 0, "lib_Utilities/Utilities", "lib_Utilities-Utilities", "lib_Utilities/Utilities", "", "A collection of utilities.")
		group = ("U", [entry])

		result.append(group)

		return result, True


@export
class SubprogramIndex(Index):
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
class TypeIndex(Index):
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
