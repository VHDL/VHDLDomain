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
The generated pages of a design: a page per library and per design unit, without a source file.

A design declared with ``pages`` - a document name, e.g. ``"StopWatch"`` - gets them below that document name:
``StopWatch/lib_Utilities`` describes the library by ``vhdl:library`` and lists its units' pages, and
``StopWatch/lib_Utilities/Counter`` describes the entity by ``vhdl:entity``. A page is written as reStructuredText, so
it's described by the directives - the same objects, targets and index entries as a hand-written description; a
directive describing the same object again is warned about as a duplicate. The predefined libraries (``std``,
``ieee``) get no pages.

The pages are listed below the document of the design's ``vhdl:design``, which has a hidden table of contents of the
library pages.
"""
from __future__              import annotations

from pathlib                 import Path
from typing                  import Any, ClassVar, Iterable

from docutils                import nodes
from sphinx.application      import Sphinx
from sphinx.environment      import BuildEnvironment

from pyTooling.Decorators    import export, notimplemented
from pyTooling.Sphinx.Pages  import GeneratedPages

from pyVHDLModel             import Design, Library
from pyVHDLModel.Predefined  import PredefinedLibrary


#: The design units with a page: per kind, the collection of :class:`~pyVHDLModel.Library`, the role and the directive.
UNIT_KINDS: tuple[tuple[str, str, str], ...] = (
	("Contexts",       "ctx",    "context"),
	("Entities",       "ent",    "entity"),
	("Packages",       "pack",   "package"),
	("Configurations", "config", "configuration"),
)

__all__ = ["UNIT_KINDS"]


@export
class DesignPages(GeneratedPages):
	"""
	The generated pages of one design: a page per library, and per context, entity, package and configuration.
	"""

	_DOMAIN: ClassVar[str] = "vhdl"                    #: The pages' objects belong to domain ``vhdl``.
	_pages:  ClassVar[dict[str, GeneratedPages]] = {}  #: The pages of every design with pages, by design name.

	#: The directive describing a design unit, by role.
	_DIRECTIVES: ClassVar[dict[str, str]] = {roleName: directive for _, roleName, directive in UNIT_KINDS}

	_designName: str  #: Name of the design, as directives and roles name it.

	def __init__(self, designName: str, design: Design, prefix: str, source: Path) -> None:
		"""
		Compute the document names of a design's libraries and design units.

		:param designName: Name of the design, as directives and roles name it.
		:param design:     The design.
		:param prefix:     Document name the pages are generated below.
		:param source:     The file or directory Sphinx regards as the pages' source, e.g. the design's directory.
		"""
		topLevel = [
			("lib", library) for library in design.Libraries.values() if not isinstance(library, PredefinedLibrary)
		]
		super().__init__(designName, prefix, source, topLevel)

		self._designName = designName

	@classmethod
	def Reset(cls, sphinxApplication: Sphinx) -> None:
		"""
		Call-back for Sphinx' ``builder-inited`` event: forget the pages of the previous build, before the designs are read
		again.

		:param sphinxApplication: Sphinx application instance.
		"""
		cls._pages = {}

	@classmethod
	def AddPages(cls, env: BuildEnvironment, designName: str, design: Design, prefix: str, source: Path) -> DesignPages:
		"""
		Create and register the pages of a design.

		:param env:        The build environment.
		:param designName: Name of the design.
		:param design:     The design.
		:param prefix:     Document name the pages are generated below.
		:param source:     The file or directory Sphinx regards as the pages' source.
		:returns:          The design's pages.
		"""
		pages = cls(designName, design, prefix, source)
		cls._pages[designName.lower()] = pages
		pages.Register(env)

		return pages

	def _Name(self, entity: Any) -> str:
		"""
		Return a library's or design unit's name.

		:param entity: The library or design unit.
		:returns:      The identifier.
		"""
		return entity.Identifier  # type: ignore[no-any-return]

	def _Source(self, entity: Any) -> Path:
		"""
		Return the file Sphinx regards as the source of a page: a design unit's VHDL file, else the pages' source.

		A warning of a design unit's page names that file.

		:param entity: The library or design unit.
		:returns:      The page's source.
		"""
		document = getattr(entity, "Document", None)
		if document is not None and (path := getattr(document, "Path", None)) is not None and path.is_file():
			return path

		return self._source

	def _Children(self, roleName: str, entity: Any) -> Iterable[tuple[str, Any]]:
		"""
		Return a library's design units - contexts, entities, packages, configurations, each sorted by name -; a design
		unit has none.

		:param roleName: The role referring to the object: ``lib`` or a design unit's.
		:param entity:   The library or design unit.
		:returns:        The children as ``(role name, object)`` pairs.
		"""
		if roleName != "lib":
			return []

		library: Library = entity
		children: list[tuple[str, Any]] = []
		for collectionName, unitRole, _ in UNIT_KINDS:
			units = getattr(library, collectionName).values()
			children.extend((unitRole, unit) for unit in sorted(units, key=lambda unit: unit.NormalizedIdentifier))

		return children

	@notimplemented("DesignPages writes its pages as reStructuredText, see _Fill.")
	def _Page(self, docName: str, roleName: str, entity: Any) -> nodes.section:
		"""
		Not used: the pages are written as reStructuredText by :meth:`_Fill`.

		:param docName:  Name of the page's document.
		:param roleName: The role referring to the object.
		:param entity:   The library or design unit.
		:returns:        Nothing.
		"""

	def _Fill(
		self,
		sphinxApplication: Sphinx,
		document:          nodes.document,
		docName:           str,
		roleName:          str,
		entity:            Any
	) -> None:
		"""
		Write a library's or design unit's page as reStructuredText: a title, and the directive describing it.

		A library's page lists its units' pages in a hidden table of contents.

		:param sphinxApplication: Sphinx application instance.
		:param document:          The page's document.
		:param docName:           Name of the page's document.
		:param roleName:          The role referring to the object.
		:param entity:            The library or design unit.
		"""
		name = entity.Identifier
		if roleName == "lib":
			title = name
			directive = f".. vhdl:library:: {name}\n   :design: {self._designName}\n"
		else:
			library = entity.Library.Identifier
			title = f"{name} ({library})"
			directive = f".. vhdl:{self._DIRECTIVES[roleName]}:: {library}.{name}\n   :design: {self._designName}\n"

		self._ParseReST(sphinxApplication, document, f"{title}\n{'#' * len(title)}\n\n{directive}")

		if roleName == "lib":
			children: list[str] = []
			for _, child in self._Children(roleName, entity):
				if (childDocName := self.DocName(child)) is not None:
					children.append(childDocName)

			if len(children) > 0:
				section: nodes.Element = document.children[-1]  # type: ignore[assignment]
				section += self._TableOfContents(docName, children)
