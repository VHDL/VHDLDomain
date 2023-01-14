from typing import Iterable, Optional as Nullable, List, Tuple

from sphinx.domains import Index, IndexEntry


class ComponentIndex(Index):
	name =      "componentindex"
	localname = "Component Index"
	shortname = "Components"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		return result, True

class PackageIndex(Index):
	name =      "packageindex"
	localname = "Package Index"
	shortname = "Packages"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		return result, True


class SubprogramIndex(Index):
	name =      "subprogramindex"
	localname = "Subprogram Index"
	shortname = "Subprograms"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		return result, True


class TypeIndex(Index):
	name =      "typeindex"
	localname = "Type Index"
	shortname = "Types"

	def generate(self, docnames: Iterable[str] = None) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
		result: List[Tuple[str, List[IndexEntry]]] = []

		return result, True
