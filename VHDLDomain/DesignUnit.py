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
The directives describing a design unit of a design read into the domain ``vhdl``: an entity, a package, a context or
a configuration.

A directive's argument is the unit's name, optionally preceded by its library, e.g. ``lib_Utilities.Counter``; without
a library, the unit is in the current one. A unit is described by its declaration - the kind and the name -, its
documentation comment, the directive's content, and its public interface: an entity's generics, ports and
architectures; a package's generics, types, subtypes, constants and subprograms; a context's context items; a
configuration's entity. Each of them is an object of the domain, which a role refers to.
"""
from __future__                  import annotations

from typing                      import ClassVar, Iterable, Optional as Nullable

from docutils                    import nodes
from docutils.nodes              import Node
from docutils.parsers.rst        import directives
from sphinx                      import addnodes
from sphinx.util.logging         import getLogger

from pyTooling.Decorators        import export
from pyTooling.MetaClasses       import abstractmethod

from pyVHDLModel                 import Library
from pyVHDLModel.DesignUnit      import Configuration, Context, DesignUnit, Entity, Package
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericPackageInterfaceItem
from pyVHDLModel.Interface       import GenericTypeInterfaceItem, PortSignalInterfaceItem
from pyVHDLModel.Object          import Constant, DeferredConstant
from pyVHDLModel.Subprogram      import Function, Procedure, Subprogram
from pyVHDLModel.Type            import BaseType, Subtype

from VHDLDomain.Directive        import VHDLDirective


__all__ = ["identifiersOf", "signatureOf"]

_logger = getLogger(__name__)


@export
def identifiersOf(item: object) -> tuple[str, ...]:
	"""
	Return the identifiers a declaration declares.

	A declaration with an identifier list, e.g. a constant or a port, declares each of them; others declare their single
	identifier.

	:param item: The declaration.
	:returns:    The identifiers, as declared.
	"""
	if (identifiers := getattr(item, "Identifiers", None)) is not None:
		return tuple(identifiers)

	return (item.Identifier, )  # type: ignore[attr-defined]


@export
def signatureOf(subprogram: Subprogram) -> str:
	"""
	Return a subprogram's signature, which a reference to an overload names: the type marks of its parameters.

	A parameter declaring several identifiers contributes its type mark once per identifier.

	:param subprogram: The subprogram.
	:returns:          The signature, as ``(unsigned, positive)``.
	"""
	typeMarks: list[str] = []
	for item in subprogram.ParameterItems:
		symbol = getattr(item, "Subtype", None)
		name = getattr(symbol, "Name", None)
		typeMark = "?" if name is None else name.Identifier
		typeMarks.extend(typeMark for _ in identifiersOf(item))

	return f"({', '.join(typeMarks)})"


@export
class DesignUnitDirective(VHDLDirective):
	"""
	Base-class of the directives describing a design unit: finding the unit in the current design and library, and
	writing its declaration, documentation and content.

	A derived class names the unit's kind and the collection of :class:`~pyVHDLModel.Library` holding it, and writes
	the unit's interface.
	"""

	_KEYWORD:     ClassVar[str]  #: The unit's keyword in VHDL, as ``entity``.
	_COLLECTION:  ClassVar[str]  #: Name of the collection of :class:`~pyVHDLModel.Library` holding the unit.
	_OBJECT_TYPE: ClassVar[str]  #: The unit's object type in the domain.

	has_content =        True  #: The content describes the unit.
	required_arguments = 1     #: The unit's name, optionally with its library.
	option_spec =        {
		"design":   directives.unchanged_required,
		"no-index": directives.flag,
	}  #: The design, if not the current one; ``:no-index:`` describes the unit without targets and index entries.

	def run(self) -> list[Node]:
		"""
		Find the unit, and write its description.

		:returns: The index node and the unit's description, or nothing if the unit isn't found.
		"""
		givenLibrary, _, unitName = self.arguments[0].strip().rpartition(".")
		designName, design = self._CurrentDesign()
		if design is None:
			return []

		libraryName: Nullable[str] = givenLibrary if givenLibrary != "" else self.env.ref_context.get("vhdl:library", None)
		if libraryName is None:
			_logger.warning(
				f"{self.directiveName}: No library: name it as '<library>.{unitName}' or place a 'vhdl:library' before it.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="library"
			)
			return []

		if (library := design.Libraries.get(libraryName.lower(), None)) is None:
			_logger.warning(
				f"{self.directiveName}: Library '{libraryName}' is not in design '{designName}'.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="library"
			)
			return []

		if (unit := getattr(library, self._COLLECTION).get(unitName.lower(), None)) is None:
			_logger.warning(
				f"{self.directiveName}: {self._KEYWORD.capitalize()} '{unitName}' is not in library '{library.Identifier}' of "
				f"design '{designName}'.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype=self._OBJECT_TYPE
			)
			return []

		document = getattr(unit, "Document", None)
		if document is not None and (path := getattr(document, "Path", None)) is not None:
			self.env.note_dependency(str(path))

		qualifiedName = f"{designName}.{library.Identifier}.{unit.Identifier}"
		description, content, index = self._Description(
			self._OBJECT_TYPE, qualifiedName, [self._KEYWORD], unit.Identifier,
			f"{unit.Identifier} (VHDL {self._KEYWORD} in {library.Identifier})"
		)
		content.extend(self._Documentation(unit.Documentation))
		content.extend(self.parse_content_to_nodes())
		self._Interface(unit, library, qualifiedName, content)

		return [index, description]

	def _Description(
		self,
		objectType:    str,
		qualifiedName: str,
		keywords:      list[str],
		name:          str,
		indexText:     str,
		suffix:        Iterable[Node] = ()
	) -> tuple[addnodes.desc, addnodes.desc_content, addnodes.index]:
		"""
		Create the description of an object: its signature line - keywords, name and suffix -, its content, its target
		and index entry, and register it in the domain.

		With ``:no-index:``, the signature has no target, and neither the index nor the domain records the object.

		:param objectType:    The object type, as ``function``.
		:param qualifiedName: The object's qualified name, as ``StopWatch.lib_Utilities.Utilities_pkg.log2(positive)``.
		:param keywords:      The VHDL keywords preceding the name, as ``["pure", "function"]``.
		:param name:          The object's name.
		:param indexText:     The text of the object's entry in the general index.
		:param suffix:        Optional, the nodes following the name, e.g. a subprogram's parameters. Default: none.
		:returns:             The description, its content node the caller fills, and the index node.
		"""
		description = addnodes.desc(
			"", domain="vhdl", objtype=objectType, desctype=objectType, classes=["vhdl", objectType]
		)
		signature = addnodes.desc_signature("", "")
		for keyword in keywords:
			signature += addnodes.desc_annotation(f"{keyword} ", "", addnodes.desc_sig_keyword(keyword, keyword),
				addnodes.desc_sig_space())
		signature += addnodes.desc_name(name, name)
		signature.extend(suffix)
		description += signature
		description += (content := addnodes.desc_content())

		index = addnodes.index(entries=[])
		if "no-index" not in self.options:
			nodeID = self._NodeID(objectType, qualifiedName)
			signature["ids"].append(nodeID)
			self.set_source_info(signature)
			self.state.document.note_explicit_target(signature)
			self.Domain.NoteObject(objectType, qualifiedName, nodeID, signature)
			index["entries"].append(("single", indexText, nodeID, "", None))

		return description, content, index

	def _RowTarget(self, row: nodes.row, objectType: str, qualifiedNames: Iterable[str]) -> None:
		"""
		Make a table row the target of the objects it describes, and register them in the domain.

		A row describes several objects, if its declaration has an identifier list, e.g. a port ``Q0, Q1``.

		:param row:            The row.
		:param objectType:     The objects' type, as ``port``.
		:param qualifiedNames: The objects' qualified names.
		"""
		if "no-index" in self.options:
			return

		for qualifiedName in qualifiedNames:
			nodeID = self._NodeID(objectType, qualifiedName)
			row["ids"].append(nodeID)
			self.Domain.NoteObject(objectType, qualifiedName, nodeID, row)

	@staticmethod
	def _Table(
		columns: list[tuple[str, int]],
		rows:    list[list[list[Node]]],
		classes: list[str]
	) -> tuple[nodes.table, list[nodes.row]]:
		"""
		Create a table with a header row.

		:param columns: One ``(title, width)`` pair per column.
		:param rows:    The rows: per row, per cell, the cell's nodes.
		:param classes: CSS classes of the table.
		:returns:       The table, and its body rows in the order of ``rows``.
		"""
		table = nodes.table("", classes=["vhdl", *classes])
		table += (tableGroup := nodes.tgroup(cols=len(columns)))
		for _, width in columns:
			tableGroup += nodes.colspec(colwidth=width)

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow := nodes.row())
		for title, _ in columns:
			headerRow += nodes.entry("", nodes.paragraph(title, title))

		tableGroup += (tableBody := nodes.tbody())
		bodyRows = []
		for cells in rows:
			tableBody += (row := nodes.row())
			for cell in cells:
				row += nodes.entry("", *cell)

			bodyRows.append(row)

		return table, bodyRows

	@staticmethod
	def _Code(text: str) -> list[Node]:
		"""
		Create a cell's content showing VHDL source text.

		:param text: The text, or an empty string for an empty cell.
		:returns:    A paragraph with the text as literal, or nothing.
		"""
		if text == "":
			return []

		return [nodes.paragraph("", "", nodes.literal(text, text, language="vhdl"))]

	def _Generics(self, unit: Entity | Package, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write a unit's generics as a table: name, kind or type, default value and documentation.

		:param unit:          The entity or package.
		:param qualifiedName: The unit's qualified name.
		:param content:       The unit's description content, the table is added to.
		"""
		if len(unit.GenericItems) == 0:
			return

		rows: list[list[list[Node]]] = []
		names: list[list[str]] = []
		for item in unit.GenericItems:
			identifiers = identifiersOf(item)
			default = ""
			if isinstance(item, GenericConstantInterfaceItem):
				kind = self._Format(item.Subtype)
				if item.DefaultExpression is not None:
					default = self._Format(item.DefaultExpression)
			elif isinstance(item, GenericTypeInterfaceItem):
				kind = "type"
			elif isinstance(item, GenericPackageInterfaceItem):
				kind = "package"
			else:
				kind = "subprogram"

			rows.append([
				self._Code(", ".join(identifiers)),
				self._Code(kind),
				self._Code(default),
				self._Documentation(item.Documentation)
			])
			names.append([f"{qualifiedName}.{identifier}" for identifier in identifiers])

		table, bodyRows = self._Table(
			[("Generic", 20), ("Type", 20), ("Default", 20), ("Description", 40)], rows, ["vhdl-generics"]
		)
		for row, qualifiedNames in zip(bodyRows, names):
			self._RowTarget(row, "generic", qualifiedNames)

		content += nodes.rubric("Generics", "Generics")
		content += table

	@abstractmethod
	def _Interface(self, unit: DesignUnit, library: Library, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write a unit's public interface into its description.

		:param unit:          The design unit.
		:param library:       The unit's library.
		:param qualifiedName: The unit's qualified name.
		:param content:       The unit's description content.
		"""


@export
class EntityDirective(DesignUnitDirective):
	"""
	The directive ``vhdl:entity``: an entity's declaration, documentation, generics, ports and architectures.

	.. code-block:: rst

	   .. vhdl:entity:: lib_Utilities.Counter

	Each generic, port and architecture is an object of the domain: ``:vhdl:generic:`Counter.BITS```,
	``:vhdl:port:`Counter.Clock``` and ``:vhdl:arch:`Counter.rtl```.
	"""

	directiveName: ClassVar[str] = "vhdl:entity"  #: Name the directive is invoked by.

	_KEYWORD:     ClassVar[str] = "entity"    #: The unit's keyword in VHDL.
	_COLLECTION:  ClassVar[str] = "Entities"  #: The collection of :class:`~pyVHDLModel.Library` holding entities.
	_OBJECT_TYPE: ClassVar[str] = "entity"    #: The unit's object type in the domain.

	def _Interface(self, unit: DesignUnit, library: Library, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write an entity's generics, ports and architectures.

		:param unit:          The entity.
		:param library:       The entity's library.
		:param qualifiedName: The entity's qualified name.
		:param content:       The entity's description content.
		"""
		entity: Entity = unit  # type: ignore[assignment]
		self._Generics(entity, qualifiedName, content)

		if len(entity.PortItems) > 0:
			rows: list[list[list[Node]]] = []
			names: list[list[str]] = []
			for item in entity.PortItems:
				identifiers = identifiersOf(item)
				if isinstance(item, PortSignalInterfaceItem) and hasattr(item, "Mode"):
					mode = str(item.Mode)
				elif hasattr(item, "ModeViewIndication"):
					mode = "view"
				else:
					mode = ""

				subtype = "" if (symbol := getattr(item, "Subtype", None)) is None else self._Format(symbol)
				default = "" if (expression := getattr(item, "DefaultExpression", None)) is None else self._Format(expression)
				rows.append([
					self._Code(", ".join(identifiers)), self._Code(mode), self._Code(subtype), self._Code(default),
					self._Documentation(item.Documentation)
				])
				names.append([f"{qualifiedName}.{identifier}" for identifier in identifiers])

			table, bodyRows = self._Table(
				[("Port", 18), ("Mode", 8), ("Type", 20), ("Default", 14), ("Description", 40)], rows, ["vhdl-ports"]
			)
			for row, qualifiedNames in zip(bodyRows, names):
				self._RowTarget(row, "port", qualifiedNames)

			content += nodes.rubric("Ports", "Ports")
			content += table

		if len(entity.Architectures) > 0:
			content += nodes.rubric("Architectures", "Architectures")
			for architecture in entity.Architectures.values():
				description, archContent, index = self._Description(
					"architecture", f"{qualifiedName}.{architecture.Identifier}", ["architecture"], architecture.Identifier,
					f"{architecture.Identifier} (VHDL architecture of {entity.Identifier} in {library.Identifier})",
					[addnodes.desc_annotation(" of ", "", addnodes.desc_sig_space(), addnodes.desc_sig_keyword("of", "of"),
						addnodes.desc_sig_space()), addnodes.desc_addname(entity.Identifier, entity.Identifier)]
				)
				archContent.extend(self._Documentation(architecture.Documentation))
				content += index
				content += description


@export
class PackageDirective(DesignUnitDirective):
	"""
	The directive ``vhdl:package``: a package's declaration, documentation, generics, types, subtypes, constants and
	subprograms, in declaration order.

	.. code-block:: rst

	   .. vhdl:package:: lib_Utilities.Utilities_pkg

	Each declaration is an object of the domain: ``:vhdl:type:`Utilities_pkg.freq```,
	``:vhdl:const:`Utilities_pkg.IS_SIMULATION``` and ``:vhdl:func:`Utilities_pkg.to_index(natural, positive)```. A
	subprogram's qualified name ends in its signature, the type marks of its parameters.
	"""

	directiveName: ClassVar[str] = "vhdl:package"  #: Name the directive is invoked by.

	_KEYWORD:     ClassVar[str] = "package"   #: The unit's keyword in VHDL.
	_COLLECTION:  ClassVar[str] = "Packages"  #: The collection of :class:`~pyVHDLModel.Library` holding packages.
	_OBJECT_TYPE: ClassVar[str] = "package"   #: The unit's object type in the domain.

	def _Interface(self, unit: DesignUnit, library: Library, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write a package's generics and declarations.

		:param unit:          The package.
		:param library:       The package's library.
		:param qualifiedName: The package's qualified name.
		:param content:       The package's description content.
		"""
		package: Package = unit  # type: ignore[assignment]
		self._Generics(package, qualifiedName, content)

		for item in package.DeclaredItems:
			if isinstance(item, Subtype):
				self._Declaration(content, "subtype", qualifiedName, item.Identifier, [], item.Documentation, package)
			elif isinstance(item, BaseType):
				self._Declaration(content, "type", qualifiedName, item.Identifier, [], item.Documentation, package)
			elif isinstance(item, (Constant, DeferredConstant)):
				subtype = self._Format(item.Subtype)
				for identifier in item.Identifiers:
					suffix = [addnodes.desc_annotation(f" : {subtype}", f" : {subtype}")]
					self._Declaration(content, "constant", qualifiedName, identifier, suffix, item.Documentation, package)
			elif isinstance(item, (Function, Procedure)):
				self._Subprogram(content, qualifiedName, item, package)

	def _Declaration(
		self,
		content:       addnodes.desc_content,
		objectType:    str,
		qualifiedName: str,
		name:          str,
		suffix:        Iterable[Node],
		documentation: Nullable[str],
		package:       Package,
		keywords:      Nullable[list[str]] = None
	) -> None:
		"""
		Write a declaration of a package as a description of its own.

		:param content:       The package's description content.
		:param objectType:    The declaration's object type, as ``constant``.
		:param qualifiedName: The package's qualified name.
		:param name:          The declared name, with a subprogram's signature.
		:param suffix:        The nodes following the name.
		:param documentation: The declaration's documentation comment.
		:param package:       The package.
		:param keywords:      Optional, the VHDL keywords preceding the name. Default: the object type.
		"""
		displayName = name.partition("(")[0]
		description, declarationContent, index = self._Description(
			objectType, f"{qualifiedName}.{name}", [objectType] if keywords is None else keywords, displayName,
			f"{displayName} (VHDL {objectType} in {package.Identifier})", suffix
		)
		declarationContent.extend(self._Documentation(documentation))
		content += index
		content += description

	def _Subprogram(
		self,
		content:       addnodes.desc_content,
		qualifiedName: str,
		subprogram:    Function | Procedure,
		package:       Package
	) -> None:
		"""
		Write a function or procedure with its parameter list - and a function's return type - as a declaration.

		:param content:       The package's description content.
		:param qualifiedName: The package's qualified name.
		:param subprogram:    The subprogram.
		:param package:       The package.
		"""
		parameters = addnodes.desc_parameterlist()
		for item in subprogram.ParameterItems:
			subtype = "" if (symbol := getattr(item, "Subtype", None)) is None else f" : {self._Format(symbol)}"
			for identifier in identifiersOf(item):
				text = f"{identifier}{subtype}"
				parameters += addnodes.desc_parameter(text, text)

		suffix: list[Node] = [parameters]
		if isinstance(subprogram, Function):
			objectType = "function"
			keywords =   ["function"] if subprogram.IsPure else ["impure", "function"]
			returnType = self._Format(subprogram.ReturnType)
			suffix.append(addnodes.desc_returns(returnType, returnType))
		else:
			objectType = "procedure"
			keywords =   ["procedure"]

		self._Declaration(
			content, objectType, qualifiedName, f"{subprogram.Identifier}{signatureOf(subprogram)}", suffix,
			subprogram.Documentation, package, keywords
		)


@export
class ContextDirective(DesignUnitDirective):
	"""
	The directive ``vhdl:context``: a context's declaration, documentation and context items - its library clauses, use
	clauses and context references, in this order.

	.. code-block:: rst

	   .. vhdl:context:: lib_Utilities.Utilities_ctx
	"""

	directiveName: ClassVar[str] = "vhdl:context"  #: Name the directive is invoked by.

	_KEYWORD:     ClassVar[str] = "context"   #: The unit's keyword in VHDL.
	_COLLECTION:  ClassVar[str] = "Contexts"  #: The collection of :class:`~pyVHDLModel.Library` holding contexts.
	_OBJECT_TYPE: ClassVar[str] = "context"   #: The unit's object type in the domain.

	def _Interface(self, unit: DesignUnit, library: Library, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write a context's context items, as VHDL source text: its library clauses, use clauses and context references.

		:param unit:          The context.
		:param library:       The context's library.
		:param qualifiedName: The context's qualified name.
		:param content:       The context's description content.
		"""
		context: Context = unit  # type: ignore[assignment]
		lines = []
		for keyword, items in (
			("library", context.LibraryReferences),
			("use",     context.PackageReferences),
			("context", context.ContextReferences)
		):
			for item in items:
				lines.append(f"{keyword} {', '.join(self._Format(symbol) for symbol in item.Symbols)};")

		if len(lines) > 0:
			code = "\n".join(lines)
			content += nodes.literal_block(code, code, language="vhdl")


@export
class ConfigurationDirective(DesignUnitDirective):
	"""
	The directive ``vhdl:configuration``: a configuration's declaration - with the entity it configures, referring to
	the entity's description - and documentation.

	.. code-block:: rst

	   .. vhdl:configuration:: lib_StopWatch.seg7_Display_cfg
	"""

	directiveName: ClassVar[str] = "vhdl:configuration"  #: Name the directive is invoked by.

	_KEYWORD:     ClassVar[str] = "configuration"   #: The unit's keyword in VHDL.
	_COLLECTION:  ClassVar[str] = "Configurations"  #: The collection of :class:`~pyVHDLModel.Library` holding them.
	_OBJECT_TYPE: ClassVar[str] = "configuration"   #: The unit's object type in the domain.

	def _Interface(self, unit: DesignUnit, library: Library, qualifiedName: str, content: addnodes.desc_content) -> None:
		"""
		Write the entity a configuration configures, referring to the entity's description.

		:param unit:          The configuration.
		:param library:       The configuration's library.
		:param qualifiedName: The configuration's qualified name.
		:param content:       The configuration's description content.
		"""
		configuration: Configuration = unit  # type: ignore[assignment]
		entityName = self._Format(configuration.Entity)
		reference = addnodes.pending_xref(
			"", refdomain="vhdl", reftype="ent", reftarget=f"{library.Identifier}.{entityName}", refexplicit=True,
			refwarn=False, refdoc=self.env.docname
		)
		reference["vhdl:design"] =  qualifiedName.partition(".")[0]
		reference["vhdl:library"] = library.Identifier
		reference += nodes.literal(entityName, entityName)
		content += nodes.paragraph("", "Configures entity ", reference, nodes.Text("."))
