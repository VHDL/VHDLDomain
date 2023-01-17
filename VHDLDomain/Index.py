from typing import Iterable, Optional as Nullable, List, Tuple

from pyTooling.Decorators import export
from sphinx.domains import Index, IndexEntry


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

		entry = ("Counter", 0, "lib_Utilities/Counter", "lib_Utilities-Counter", "lib_Utilities/Counter", "", "A generic counter.")
		group = ("C", [entry])

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
