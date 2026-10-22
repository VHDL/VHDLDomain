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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
The directives of the domain ``vhdl``: each describes an object of a design read into the domain.

``vhdl:design`` and ``vhdl:library`` set the design and library the following directives and references of the
document are in, until the next one.
"""
from __future__           import annotations

from typing               import TYPE_CHECKING, ClassVar, Optional as Nullable

from docutils             import nodes
from docutils.nodes       import Node
from docutils.parsers.rst import directives
from sphinx               import addnodes
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging  import getLogger
from sphinx.util.nodes    import make_id

from pyTooling.Decorators import export

from pyVHDLModel          import Design, Library

if TYPE_CHECKING:  # pragma: no cover
	from VHDLDomain       import VHDLDomain


_logger = getLogger(__name__)


@export
class VHDLDirective(SphinxDirective):
	"""
	Base-class of the directives of domain ``vhdl``: access to the domain, the current design and library, and the
	registration of a described object.
	"""

	_WARNING_TYPE: ClassVar[str] = "vhdl"  #: Type of the warnings the directives emit, the domain's name.

	directiveName: ClassVar[str]  #: Name the directive is invoked by, used in every warning.

	def _Domain(self) -> VHDLDomain:
		"""
		Return the domain ``vhdl``.

		:returns: The domain.
		"""
		return self.env.get_domain("vhdl")  # type: ignore[return-value]

	def _CurrentDesign(self) -> tuple[Nullable[str], Nullable[Design]]:
		"""
		Return the design the directive is in: the one of option ``:design:``, else the current one.

		A missing design is warned about.

		:returns: The design's name and the design, or ``None`` and ``None`` if no design is current, or the name and
		          ``None`` if the design wasn't read.
		"""
		if (name := self.options.get("design", self.env.ref_context.get("vhdl:design", None))) is None:
			_logger.warning(
				f"{self.directiveName}: No design: give option ':design:' or place a 'vhdl:design' before it.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="design"
			)
			return None, None

		if (design := self._Domain().GetDesign(name)) is None:
			_logger.warning(
				f"{self.directiveName}: Design '{name}' was not read.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="design"
			)

		return name, design

	def _Target(self, objectType: str, qualifiedName: str, indexText: str) -> list[Node]:
		"""
		Create the target and the index entry of a described object, and register it in the domain.

		:param objectType:    The object type, as ``entity``.
		:param qualifiedName: The object's qualified name, as ``StopWatch.lib_StopWatch.Counter``.
		:param indexText:     The text of the object's entry in the general index.
		:returns:             The index node and the target node.
		"""
		nodeID = make_id(self.env, self.state.document, f"vhdl-{objectType}", qualifiedName.lower())
		target = nodes.target("", "", ids=[nodeID])
		self.set_source_info(target)
		self.state.document.note_explicit_target(target)
		self._Domain().NoteObject(objectType, qualifiedName, nodeID, target)

		return [addnodes.index(entries=[("single", indexText, nodeID, "", None)]), target]


@export
class DesignDirective(VHDLDirective):
	"""
	The directive ``vhdl:design``: a design's target and index entry, and the current design of the document.

	.. code-block:: rst

	   .. vhdl:design:: StopWatch

	The argument is the design's name, a key of ``vhdl_designs``. Every directive and reference following it in the
	document is in this design. The directive writes no visible output except its content; placed above a page's title,
	its target is the title, as a label is. With ``:no-index:``, it only makes the design the current one - for the
	other pages of a design.
	"""

	directiveName: ClassVar[str] = "vhdl:design"  #: Name the directive is invoked by.

	has_content =        True                            #: The content describes the design.
	required_arguments = 1                               #: The design's name.
	option_spec =        {"no-index": directives.flag}   #: Make the design current, without a target and index entry.

	def run(self) -> list[Node]:
		"""
		Register the design, make it the current one, and parse the content.

		:returns: An index node, the design's target and the content's nodes.
		"""
		name = self.arguments[0].strip()
		self.env.ref_context["vhdl:design"] = name
		self.env.ref_context.pop("vhdl:library", None)

		if self._Domain().GetDesign(name) is None:
			_logger.warning(
				f"{self.directiveName}: Design '{name}' was not read.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="design"
			)

		result = [] if "no-index" in self.options else self._Target("design", name, f"{name} (VHDL design)")
		result.extend(self.parse_content_to_nodes())

		return result


@export
class LibraryDirective(VHDLDirective):
	"""
	The directive ``vhdl:library``: a library's target, index entry and design units, and the current library of the
	document.

	.. code-block:: rst

	   .. vhdl:library:: lib_StopWatch
	      :design: StopWatch

	The argument is the library's name; without ``:design:``, the library is in the current design. Every directive and
	reference following it in the document is in this library. The directive writes the library's documentation, its
	content, and a table of the library's design units - each name referring to the unit's description, if there is
	one. With ``:no-index:``, it only makes the library the current one, and writes nothing.
	"""

	directiveName: ClassVar[str] = "vhdl:library"  #: Name the directive is invoked by.

	has_content =        True  #: The content describes the library.
	required_arguments = 1     #: The library's name.
	option_spec =        {
		"design":   directives.unchanged_required,
		"no-index": directives.flag,
	}  #: The design, if not the current one; ``:no-index:`` makes the library current, without describing it.

	#: The kinds of design units the table lists, with the collection of :class:`~pyVHDLModel.Library` and the role.
	_UNIT_KINDS: ClassVar[tuple[tuple[str, str, str], ...]] = (
		("Context",       "Contexts",       "ctx"),
		("Entity",        "Entities",       "ent"),
		("Package",       "Packages",       "pack"),
		("Configuration", "Configurations", "config"),
	)

	def run(self) -> list[Node]:
		"""
		Register the library, make it the current one, and write its documentation, content and design units.

		:returns: An index node, the library's target, and the library's description.
		"""
		name = self.arguments[0].strip()
		designName, design = self._CurrentDesign()
		if designName is None:
			return []

		self.env.ref_context["vhdl:design"] =  designName
		self.env.ref_context["vhdl:library"] = name
		if "no-index" in self.options:
			return []

		result = self._Target("library", f"{designName}.{name}", f"{name} (VHDL library in {designName})")
		if design is None:
			return result

		if (library := design.Libraries.get(name.lower(), None)) is None:
			_logger.warning(
				f"{self.directiveName}: Library '{name}' is not in design '{designName}'.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="library"
			)
			return result

		if library.Documentation is not None:
			result.append(nodes.paragraph(library.Documentation, library.Documentation))

		result.extend(self.parse_content_to_nodes())
		if (table := self._DesignUnits(library)) is not None:
			result.append(table)

		return result

	def _DesignUnits(self, library: Library) -> Nullable[nodes.table]:
		"""
		Create the table of a library's design units: kind and name, the name referring to the unit's description.

		:param library: The library.
		:returns:       The table, or ``None`` if the library has no design units.
		"""
		rows: list[nodes.row] = []
		for kindName, collectionName, roleName in self._UNIT_KINDS:
			for unit in getattr(library, collectionName).values():
				reference = addnodes.pending_xref(
					"", refdomain="vhdl", reftype=roleName, reftarget=f"{library.Identifier}.{unit.Identifier}",
					refexplicit=True, refwarn=False, refdoc=self.env.docname
				)
				reference["vhdl:design"] =  self.env.ref_context["vhdl:design"]
				reference["vhdl:library"] = library.Identifier
				reference += nodes.literal(unit.Identifier, unit.Identifier)

				rows.append(nodes.row(
					"",
					nodes.entry("", nodes.paragraph(kindName, kindName)),
					nodes.entry("", nodes.paragraph("", "", reference))
				))

		if len(rows) == 0:
			return None

		table = nodes.table("", classes=["vhdl", "vhdl-library-units"])
		table += (tableGroup := nodes.tgroup(cols=2))
		tableGroup += nodes.colspec(colwidth=20)
		tableGroup += nodes.colspec(colwidth=80)
		tableGroup += (tableHeader := nodes.thead())
		tableHeader += nodes.row(
			"",
			nodes.entry("", nodes.paragraph("Kind", "Kind")),
			nodes.entry("", nodes.paragraph("Design Unit", "Design Unit"))
		)
		tableGroup += (tableBody := nodes.tbody())
		tableBody.extend(rows)

		return table
