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
from pyVHDLModel.Base            import identifiersOf
from pyVHDLModel.DesignUnit      import Component, Configuration, Context, DesignUnit, Entity, Package
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericFunctionInterfaceItem, \
                                        GenericInterfaceItemMixin, GenericPackageInterfaceItem, \
                                        GenericTypeInterfaceItem, InterfaceItemWithModeMixin, PortSignalInterfaceItem
from pyVHDLModel.Object          import Constant, DeferredConstant, SharedVariable, Signal, WithDefaultExpressionMixin
from pyVHDLModel.Subprogram      import Function, Procedure, Subprogram
from pyVHDLModel.Type            import BaseType, PhysicalType, RecordType, Subtype

from VHDLDomain.Directive        import VHDLDirective


_logger = getLogger(__name__)


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
			self._Domain().NoteObject(objectType, qualifiedName, nodeID, signature)
			index["entries"].append(("single", indexText, nodeID, "", None))

		return description, content, index

	@staticmethod
	def _Field(label: str, bodies: list[list[Node]]) -> nodes.field:
		"""
		Create a field of a description, as Sphinx writes the fields of a Python function.

		A field is e.g. a function's parameters. A field of one item writes it as paragraphs, a field of several items as
		a bullet list.

		:param label:  The field's name, as ``Ports``.
		:param bodies: Per item, its nodes: the paragraph declaring it, followed by further paragraphs of its documentation.
		:returns:      The field.
		"""
		if len(bodies) == 1:
			fieldBody = nodes.field_body("", *bodies[0])
		else:
			fieldBody = nodes.field_body("", nodes.bullet_list("", *(nodes.list_item("", *body) for body in bodies)))

		return nodes.field("", nodes.field_name(label, label), fieldBody)

	def _Item(self, paragraph: nodes.paragraph, documentation: Nullable[str]) -> list[Node]:
		"""
		Complete an item of a field by its documentation comment.

		The comment's first paragraph follows the item's declaration after a dash; its further paragraphs follow below.

		:param paragraph:     The paragraph declaring the item.
		:param documentation: The item's documentation comment, or ``None``.
		:returns:             The item's nodes.
		"""
		body: list[Node] = [paragraph]
		if len(description := self._Documentation(documentation)) > 0:
			paragraph += nodes.Text(" -- ")
			if isinstance(description[0], nodes.paragraph):
				paragraph.extend(list(description.pop(0).children))

			body.extend(description)

		return body

	def _InterfaceField(
		self,
		label:         str,
		objectType:    Nullable[str],
		qualifiedName: str,
		entries:       Iterable[tuple[Iterable[str], str, str, Nullable[str]]]
	) -> nodes.field:
		"""
		Create the field of an interface list, as Sphinx writes a Python function's parameters.

		An interface list is e.g. an entity's generics or ports. Each entry is an item of the list: its names in bold, its
		declaration - e.g. mode and subtype -, its default value and its documentation. Each item is the target of the
		objects it declares; an item declares several objects, if its declaration has an identifier list, e.g. a port
		``Q0, Q1``.

		:param label:         The field's name, as ``Ports``.
		:param objectType:    The object type of the items, as ``port``, or ``None`` if they are no objects of the domain,
		                      as a subprogram's parameters.
		:param qualifiedName: The qualified name of the unit or declaration declaring the items.
		:param entries:       Per item: its identifiers, its declaration, its default value or an empty string, and its
		                      documentation comment.
		:returns:             The field.
		"""
		bodies: list[list[Node]] = []
		for identifiers, declaration, default, documentation in entries:
			names =     ", ".join(identifiers)
			paragraph = nodes.paragraph()
			paragraph += addnodes.literal_strong(names, names)
			paragraph += nodes.Text(" : ")
			paragraph += addnodes.literal_emphasis(declaration, declaration)
			if default != "":
				paragraph += nodes.Text(" := ")
				paragraph += addnodes.literal_emphasis(default, default)

			if objectType is not None and "no-index" not in self.options:
				for identifier in identifiers:
					itemName = f"{qualifiedName}.{identifier}"
					nodeID =   self._NodeID(objectType, itemName)
					paragraph["ids"].append(nodeID)
					self._Domain().NoteObject(objectType, itemName, nodeID, paragraph)

			bodies.append(self._Item(paragraph, documentation))

		return self._Field(label, bodies)

	def _Generics(
		self,
		unit:          Entity | Package | Component | Subprogram,
		qualifiedName: str,
		*,
		objects:       bool = True
	) -> Nullable[nodes.field]:
		"""
		Create the field of a unit's generics: per generic its name, its subtype - or the kind of a generic type, package
		or subprogram -, its default value and its documentation.

		:param unit:          The entity, package, component or subprogram.
		:param qualifiedName: The unit's qualified name.
		:param objects:       Optional, whether the generics are objects of the domain. Default: ``True``.
		:returns:             The field, or ``None`` if the unit has no generics.
		"""
		if len(unit.GenericItems) == 0:
			return None

		entries: list[tuple[Iterable[str], str, str, Nullable[str]]] = []
		for item in unit.GenericItems:
			default = ""
			if isinstance(item, GenericConstantInterfaceItem):
				kind = self._Format(item.Subtype)
				if item.DefaultExpression is not None:
					default = self._Format(item.DefaultExpression)
			elif isinstance(item, GenericTypeInterfaceItem):
				kind = "type"
			elif isinstance(item, GenericPackageInterfaceItem):
				kind = "package"
			elif isinstance(item, GenericFunctionInterfaceItem):
				kind = "function"
			else:
				kind = "procedure"

			entries.append((self._Designators(item), kind, default, item.Documentation))

		return self._InterfaceField("Generics", "generic" if objects else None, qualifiedName, entries)

	@staticmethod
	def _Designators(item: GenericInterfaceItemMixin) -> tuple[str, ...]:
		"""
		Return the designators a generic declares: its identifiers, or a generic function's operator symbol in quotes.

		pyVHDLModel keeps an operator symbol without quotes, e.g. ``<`` for the generic function ``"<"``.

		:param item: The generic.
		:returns:    The designators.
		"""
		return tuple(
			identifier if identifier[0].isalnum() or identifier[0] == "\\" else f'"{identifier}"'
			for identifier in identifiersOf(item)
		)

	def _Ports(self, unit: Entity | Component, qualifiedName: str, *, objects: bool = True) -> Nullable[nodes.field]:
		"""
		Create the field of a unit's ports: per port its name, its mode and subtype, its default value and its
		documentation.

		:param unit:          The entity or component.
		:param qualifiedName: The unit's qualified name.
		:param objects:       Optional, whether the ports are objects of the domain. Default: ``True``.
		:returns:             The field, or ``None`` if the unit has no ports.
		"""
		if len(unit.PortItems) == 0:
			return None

		entries: list[tuple[Iterable[str], str, str, Nullable[str]]] = []
		for item in unit.PortItems:
			if isinstance(item, PortSignalInterfaceItem) and hasattr(item, "Mode"):
				mode = str(item.Mode)
			elif hasattr(item, "ModeViewIndication"):
				mode = "view"
			else:
				mode = ""

			subtype = "" if (symbol := getattr(item, "Subtype", None)) is None else self._Format(symbol)
			default = "" if (expression := getattr(item, "DefaultExpression", None)) is None else self._Format(expression)

			declaration = " ".join(part for part in (mode, subtype) if part != "")
			entries.append((identifiersOf(item), declaration, default, item.Documentation))

		return self._InterfaceField("Ports", "port" if objects else None, qualifiedName, entries)

	def _InterfaceFields(
		self,
		unit:          Entity | Component,
		qualifiedName: str,
		*,
		objects:       bool = True
	) -> Nullable[nodes.field_list]:
		"""
		Create the fields of an entity's or component's interface: its generics and its ports.

		:param unit:          The entity or component.
		:param qualifiedName: The unit's qualified name.
		:param objects:       Optional, whether the generics and ports are objects of the domain. Default: ``True``.
		:returns:             The fields, or ``None`` if the unit has neither generics nor ports.
		"""
		fields = nodes.field_list(classes=["vhdl-interface"])
		if (generics := self._Generics(unit, qualifiedName, objects=objects)) is not None:
			fields += generics

		if (ports := self._Ports(unit, qualifiedName, objects=objects)) is not None:
			fields += ports

		return fields if len(fields) > 0 else None

	def _EntityReference(self, designName: str, libraryName: str, entityName: str) -> addnodes.pending_xref:
		"""
		Create a reference to an entity's description.

		A configuration and a component refer to their entity. An entity without a description is written as its name,
		without a warning.

		:param designName:  The entity's design.
		:param libraryName: The entity's library.
		:param entityName:  The entity's name.
		:returns:           The reference.
		"""
		reference = addnodes.pending_xref(
			"", refdomain="vhdl", reftype="ent", reftarget=f"{libraryName}.{entityName}", refexplicit=True, refwarn=False,
			refdoc=self.env.docname
		)
		reference["vhdl:design"] =  designName
		reference["vhdl:library"] = libraryName
		reference += nodes.literal(entityName, entityName)

		return reference

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
		if (fields := self._InterfaceFields(entity, qualifiedName)) is not None:
			content += fields

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
	The directive ``vhdl:package``: a package's declaration, documentation, generics, and - in declaration order - its
	types, subtypes, constants, signals, shared variables, components and subprograms.

	.. code-block:: rst

	   .. vhdl:package:: lib_Utilities.Utilities_pkg

	Each declaration is an object of the domain: ``:vhdl:type:`Utilities_pkg.freq```,
	``:vhdl:const:`Utilities_pkg.IS_SIMULATION```, ``:vhdl:comp:`Utilities_pkg.Debouncer``` and
	``:vhdl:func:`Utilities_pkg.to_index(natural, positive)```. A subprogram's qualified name ends in its signature, the
	type marks of its parameters. A component's generics and ports are no objects: a reference to a port names the
	entity's port.
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
		if (generics := self._Generics(package, qualifiedName)) is not None:
			content += nodes.field_list("", generics, classes=["vhdl-interface"])

		for item in package.DeclaredItems:
			if isinstance(item, BaseType):
				self._Type(content, qualifiedName, item, package)
			elif isinstance(item, Constant):
				self._Objects(content, "constant", ["constant"], qualifiedName, item, package)
			elif isinstance(item, DeferredConstant):
				self._Objects(content, "constant", ["deferred", "constant"], qualifiedName, item, package)
			elif isinstance(item, Signal):
				self._Objects(content, "signal", ["signal"], qualifiedName, item, package)
			elif isinstance(item, SharedVariable):
				self._Objects(content, "variable", ["shared", "variable"], qualifiedName, item, package)
			elif isinstance(item, Component):
				self._Component(content, qualifiedName, item, package)
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
	) -> addnodes.desc_content:
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
		:returns:             The declaration's description content, holding its documentation.
		"""
		displayName = name.partition("(")[0]
		description, declarationContent, index = self._Description(
			objectType, f"{qualifiedName}.{name}", [objectType] if keywords is None else keywords, displayName,
			f"{displayName} (VHDL {objectType} in {package.Identifier})", suffix
		)
		declarationContent.extend(self._Documentation(documentation))
		content += index
		content += description

		return declarationContent

	def _Type(self, content: addnodes.desc_content, qualifiedName: str, item: BaseType, package: Package) -> None:
		"""
		Write a type or subtype declaration: its definition as pyVHDLModel's writer writes it, a record type's elements
		and a physical type's units.

		The signature shows the definition's first line, e.g. ``is array (natural range <>) of T_BCD`` or ``is record``.

		:param content:       The package's description content.
		:param qualifiedName: The package's qualified name.
		:param item:          The type or subtype.
		:param package:       The package.
		"""
		keyword =     "subtype" if isinstance(item, Subtype) else "type"
		prefix =      f"{keyword} {item.Identifier}"
		declaration = self._Format(item).strip().partition("\n")[0].removesuffix(";")

		suffix: list[Node] = []
		if declaration.startswith(prefix) and (definition := declaration[len(prefix):]) != "":
			suffix.append(addnodes.desc_annotation(definition, definition))

		typeContent = self._Declaration(
			content, keyword, qualifiedName, item.Identifier, suffix, item.Documentation, package
		)
		if isinstance(item, RecordType) and len(item.Elements) > 0:
			entries = [
				(element.Identifiers, self._Format(element.Subtype), "", element.Documentation) for element in item.Elements
			]
			typeContent += nodes.field_list(
				"", self._InterfaceField("Elements", None, qualifiedName, entries), classes=["vhdl-interface"]
			)
		elif isinstance(item, PhysicalType):
			bodies: list[list[Node]] = []
			for unit in (item.PrimaryUnit, *item.SecondaryUnits):
				paragraph = nodes.paragraph("", "", addnodes.literal_strong(unit.Identifier, unit.Identifier))
				if unit.Value is not None:
					value = self._Format(unit.Value)
					paragraph += nodes.Text(" = ")
					paragraph += addnodes.literal_emphasis(value, value)

				bodies.append(self._Item(paragraph, unit.Documentation))

			typeContent += nodes.field_list("", self._Field("Units", bodies), classes=["vhdl-interface"])

	def _Component(self, content: addnodes.desc_content, qualifiedName: str, item: Component, package: Package) -> None:
		"""
		Write a component declaration: the entity it is bound to, its generics and its ports.

		The field *Entity* refers to the entity of the same name in the package's library, if pyVHDLModel linked the
		component to it.

		:param content:       The package's description content.
		:param qualifiedName: The package's qualified name.
		:param item:          The component.
		:param package:       The package.
		"""
		componentContent = self._Declaration(
			content, "component", qualifiedName, item.Identifier, [], item.Documentation, package
		)
		fields = self._InterfaceFields(item, f"{qualifiedName}.{item.Identifier}", objects=False)
		if (entity := item.Entity) is not None:
			reference = self._EntityReference(qualifiedName.partition(".")[0], entity.Library.Identifier, entity.Identifier)
			if fields is None:
				fields = nodes.field_list(classes=["vhdl-interface"])

			fields.insert(0, self._Field("Entity", [[nodes.paragraph("", "", reference)]]))

		if fields is not None:
			componentContent += fields

	def _Objects(
		self,
		content:       addnodes.desc_content,
		objectType:    str,
		keywords:      list[str],
		qualifiedName: str,
		item:          Constant | DeferredConstant | Signal | SharedVariable,
		package:       Package
	) -> None:
		"""
		Write an object declaration - a constant, signal or shared variable -, a description per identifier: its subtype
		and its default value.

		A deferred constant has no value in the package, its signature is marked ``deferred constant``; a shared variable
		has no default value.

		:param content:       The package's description content.
		:param objectType:    The objects' object type, as ``signal``.
		:param keywords:      The VHDL keywords preceding the name, as ``["shared", "variable"]``.
		:param qualifiedName: The package's qualified name.
		:param item:          The object declaration.
		:param package:       The package.
		"""
		text = f" : {self._Format(item.Subtype)}"
		if isinstance(item, WithDefaultExpressionMixin) and item.DefaultExpression is not None:
			text += f" := {self._Format(item.DefaultExpression)}"

		for identifier in item.Identifiers:
			suffix = [addnodes.desc_annotation(text, text)]
			self._Declaration(content, objectType, qualifiedName, identifier, suffix, item.Documentation, package, keywords)

	def _Subprogram(
		self,
		content:       addnodes.desc_content,
		qualifiedName: str,
		subprogram:    Function | Procedure,
		package:       Package
	) -> None:
		"""
		Write a function or procedure with its parameter list - and a function's return type - as a declaration.

		A generic subprogram's signature shows the names of its generics before the parameter list, as Sphinx writes a
		Python function's type parameters; its description has the field *Generics*, as an entity's. A parameter shows
		its mode, if the declaration gives one, its subtype and its default value. If a parameter is documented, the
		description has the field *Parameters*, as an entity's *Ports*.

		:param content:       The package's description content.
		:param qualifiedName: The package's qualified name.
		:param subprogram:    The subprogram.
		:param package:       The package.
		"""
		parameters = addnodes.desc_parameterlist()
		entries: list[tuple[Iterable[str], str, str, Nullable[str]]] = []
		for item in subprogram.ParameterItems:
			mode =    str(item.Mode) if isinstance(item, InterfaceItemWithModeMixin) else ""
			subtype = "" if (symbol := getattr(item, "Subtype", None)) is None else self._Format(symbol)
			default = "" if (expression := getattr(item, "DefaultExpression", None)) is None else self._Format(expression)

			declaration = " ".join(part for part in (mode, subtype) if part != "")
			for identifier in identifiersOf(item):
				text = identifier if declaration == "" else f"{identifier} : {declaration}"
				if default != "":
					text += f" := {default}"

				parameters += addnodes.desc_parameter(text, text)

			entries.append((identifiersOf(item), declaration, default, item.Documentation))

		suffix: list[Node] = [parameters]
		if len(subprogram.GenericItems) > 0:
			typeParameters = addnodes.desc_type_parameter_list()
			for generic in subprogram.GenericItems:
				for designator in self._Designators(generic):
					typeParameters += addnodes.desc_type_parameter(designator, designator)

			suffix.insert(0, typeParameters)

		if isinstance(subprogram, Function):
			objectType = "function"
			keywords =   ["function"] if subprogram.IsPure else ["impure", "function"]
			returnType = self._Format(subprogram.ReturnType)
			suffix.append(addnodes.desc_returns(returnType, returnType))
		else:
			objectType = "procedure"
			keywords =   ["procedure"]

		signature = ", ".join(subprogram.Signature.ParameterTypeNames)
		subprogramContent = self._Declaration(
			content, objectType, qualifiedName, f"{subprogram.Identifier}({signature})", suffix, subprogram.Documentation,
			package, keywords
		)
		fields = nodes.field_list(classes=["vhdl-interface"])
		if (generics := self._Generics(subprogram, qualifiedName, objects=False)) is not None:
			fields += generics

		if any(documentation is not None for *_, documentation in entries):
			fields += self._InterfaceField("Parameters", None, qualifiedName, entries)

		if len(fields) > 0:
			subprogramContent += fields


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
		reference = self._EntityReference(
			qualifiedName.partition(".")[0], library.Identifier, self._Format(configuration.Entity)
		)
		content += nodes.paragraph("", "Configures entity ", reference, nodes.Text("."))
