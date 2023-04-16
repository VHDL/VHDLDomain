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

This module contains all the directives of the VHDL domain.
"""
from enum import Flag, auto
from textwrap import dedent
from typing import List, Dict, Tuple

from docutils import nodes
from docutils.nodes import Node, section, table, tgroup
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from pyTooling.Decorators import export
from pyGHDL.dom.DesignUnit import Entity
from pyGHDL.dom.InterfaceItem import GenericConstantInterfaceItem, PortSignalInterfaceItem


@export
class ParameterStyle(Flag):
	Never = auto()
	Table = auto()
	Sections = auto()


@export
class ArchitecturesStyle(Flag):
	Never = auto()
	Multiple = auto()
	Always = auto()


@export
def strip(option: str):
	return option.strip().lower()


@export
class BaseDirective(ObjectDescription):
	has_content: bool = False
	"""
	A boolean; ``True`` if content is allowed.

	Client code must handle the case where content is required but not supplied (an empty content list will be supplied).
	"""

	required_arguments = 0
	"""Number of required directive arguments."""

	optional_arguments = 0
	"""Number of optional arguments after the required arguments."""

	final_argument_whitespace = False
	"""A boolean, indicating if the final argument may contain whitespace."""

	option_spec = None
	"""
	Mapping of option names to validator functions.

	A dictionary, mapping known option names to conversion functions such as :py:class:`int` or :py:class:`float`
	(default: {}, no options). Several conversion functions are defined in the ``directives/__init__.py`` module.

	Option conversion functions take a single parameter, the option argument (a string or :py:class:`None`), validate it
	and/or convert it to the appropriate form. Conversion functions may raise :py:exc:`ValueError` and
	:py:exc:`TypeError` exceptions.
	"""

	def ParseBooleanOption(self, optionName: str, default: bool) -> bool:
		try:
			option = self.options[optionName]
		except KeyError:
			try:
				option = self.defaultValues[optionName]
			except KeyError:
				return default

		if option in ("yes", "true"):
			return True
		elif option in ("no", "false"):
			return False
		else:
			raise ValueError(f"Value '{option}' not supported for a boolean value (yes/true, no/false).")

	def _PrepareTable(self, columns: Dict[str, int], classes: List[str]) -> Tuple[table, tgroup]:
		tableGroup = nodes.tgroup(cols=(len(columns)))
		table = nodes.table("", tableGroup, classes=classes)

		tableRow = nodes.row()
		for columnTitle, width in columns.items():
			tableGroup += nodes.colspec(colwidth=width)
			tableRow += nodes.entry("", nodes.paragraph(text=columnTitle))

		tableGroup += nodes.thead("", tableRow)

		return table, tableGroup


@export
class WithParametersMixin:
	def ParseParameterStyleOption(self, optionName: str) -> ParameterStyle:
		try:
			option = self.options[optionName]
		except KeyError:
			try:
				option = self.defaultValues[optionName]
			except KeyError:
				return ParameterStyle.Table

		if option == "never":
			return ParameterStyle.Never
		elif option == "table":
			return ParameterStyle.Table
		elif option == "sections":
			return ParameterStyle.Sections
		else:
			raise ValueError(f"value '{option}' is not in list of choices: never, table, sections.")


@export
class WithGenericsMixin(WithParametersMixin):
	def _CreateGenericsAsTable(self, entity: Entity) -> table:
		table, tableGroup = self._PrepareTable(
			columns={
				"Generic Name": 2,
				"Type": 1,
				"Default Value": 2,
				"Description": 4,
			},
			classes=["vhdl", "vhdl-generic-table"]
		)

		tableBody = nodes.tbody()
		tableGroup += tableBody

		for generic in entity.GenericItems:
			cellGenericName = nodes.entry()
			cellGenericType = nodes.entry()
			cellDefaultValue = nodes.entry()
			cellDescription = nodes.entry()
			tableBody += nodes.row("", cellGenericName, cellGenericType, cellDefaultValue, cellDescription)

			if isinstance(generic, GenericConstantInterfaceItem):
				cellGenericName += nodes.paragraph(text=", ".join(generic.Identifiers))
				cellGenericType += nodes.paragraph(text=generic.Documentation)
				if generic.DefaultExpression is not None:
					cellDefaultValue += nodes.paragraph(text="??")  # str(generic.DefaultExpression))
				if generic.Documentation is not None:
					cellDescription += nodes.paragraph(text=generic.Documentation)

		return table

	def _CreateGenericsAsSections(self, entity: Entity) -> List[section]:
		content = []
		for generic in entity.GenericItems:
			if isinstance(generic, GenericConstantInterfaceItem):
				genericSection = nodes.section(ids=[f"{entity.NormalizedIdentifier}-generic-{nID}" for nID in generic.NormalizedIdentifiers])
				genericSection.append(nodes.title(text=", ".join(generic.Identifiers)))
				genericSection.append(nodes.paragraph(text=generic.Documentation))

				content.append(genericSection)

		return content

	def CreateGenericSection(self, entity: Entity, style: ParameterStyle) -> section:
		content = [
			nodes.title(text="Generics")
		]

		if True:
			content.append(nodes.paragraph(text="list of all generics"))

		if style is ParameterStyle.Table:
			content.append(self._CreateGenericsAsTable(entity))
		elif style is ParameterStyle.Sections:
			content.extend(self._CreateGenericsAsSections(entity))

		section = nodes.section(
			ids=[f"{entity.NormalizedIdentifier}-generics"],
			classes=["vhdl", "vhdl-entity-generic-section"]
		)
		section.extend(content)

		return section


@export
class WithPortsMixin(WithParametersMixin):
	def _CreatePortsAsTable(self, entity: Entity) -> table:
		table, tableGroup = self._PrepareTable(
			columns={
				"Port Name": 2,
				"Direction": 1,
				"Type": 1,
				"Default Value": 2,
				"Description": 4,
			},
			classes=["vhdl", "vhdl-port-table"]
		)

		tableBody = nodes.tbody()
		tableGroup += tableBody

		for port in entity.PortItems:
			cellPortName = nodes.entry()
			cellPortDirection = nodes.entry()
			cellPortType = nodes.entry()
			cellDefaultValue = nodes.entry()
			cellDescription = nodes.entry()
			tableBody += nodes.row("", cellPortName, cellPortDirection, cellPortType, cellDefaultValue, cellDescription)

			if isinstance(port, PortSignalInterfaceItem):
				cellPortName += nodes.paragraph(text=", ".join(port.Identifiers))
				cellPortDirection += nodes.paragraph(text=str(port.Mode))
				cellPortType += nodes.paragraph(text=port.Documentation)
				if port.DefaultExpression is not None:
					cellDefaultValue += nodes.paragraph(text=str(port.DefaultExpression))
				if port.Documentation is not None:
					cellDescription += nodes.paragraph(text=port.Documentation)

		return table

	def _CreatePortsAsSections(self, entity: Entity) -> List[section]:
		content = []
		for port in entity.PortItems:
			if isinstance(port, PortSignalInterfaceItem):
				portSection = nodes.section(ids=[f"{entity.NormalizedIdentifier}-port-{nID}" for nID in port.NormalizedIdentifiers])
				portSection.append(nodes.title(text=", ".join(port.Identifiers)))
				portSection.append(nodes.paragraph(text=port.Documentation))

				content.append(portSection)

		return content


	def CreatePortSection(self, entity: Entity, style: ParameterStyle) -> section:
		content = [
			nodes.title(text="Ports")
		]

		if True:
			content.append(nodes.paragraph(text="list of all ports"))

		if style is ParameterStyle.Table:
			content.append(self._CreatePortsAsTable(entity))
		elif style is ParameterStyle.Sections:
			content.extend(self._CreatePortsAsSections(entity))

		section = nodes.section(
			ids=[f"{entity.NormalizedIdentifier}-ports"],
			classes=["vhdl", "vhdl-entity-port-section"]
		)
		section.extend(content)

		return section


@export
class DescribeDesign(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL design.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe design")

		items = []
		for document in design.Documents:
			term = nodes.term(text=f"{document.ShortPath}")
			description = nodes.paragraph(text=f"{document.Documentation}")
			description = nodes.literal_block(text=f"{document.Documentation}")
			definition = nodes.definition("", description)

			items.append(nodes.definition_list_item("", term, definition))

		definitionList = nodes.definition_list("", *items)

		return [paragraph, definitionList]


@export
class DescribeLibrary(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL library.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe library")

		return [paragraph]


@export
class DescribeDocument(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL document.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]


		paragraph = nodes.paragraph(text="Describe document")

		return [paragraph]


@export
class DescribeContext(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL context.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 1

	option_spec = {
		"referencedby":  strip,
	}

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		# FIXME: check with regexp
		# FIXME: better error message(s)
		if len(self.arguments) == 1:
			try:
				libraryName, contextName = self.arguments[0].split(".")
			except ValueError:
				raise ValueError(f"Parameter to 'vhdl:describecontext' has incorrect format.")
		else:
			raise ValueError(f"Parameter to 'vhdl:describecontext' directive has too many content lines ({len(self.arguments)}).")

		# TODO: Can this be done in an __init__ or so?
		self.directiveName = self.name.split(":")[1]
		self.defaultValues = self.env.config.vhdl_defaults[self.directiveName]

		# parse all directive options or use default values
		optionReferencedBy = self.ParseBooleanOption("referencedby", True)

		# Get entity object from design
		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]  # FIXME: allow specification of design name or default design
		library = design.GetLibrary(libraryName.lower())
		context = library.Contexts[contextName.lower()]

		content = [
			nodes.title(text=context.Identifier),
			nodes.paragraph(text=context.Documentation)
		]

		# if optionReferencedBy:
		# 	content.append(self.CreateReferencedBySection(package))

		contextSection = nodes.section(
			ids=[context.NormalizedIdentifier],
			classes=["vhdl", "vhdl-context-section"]
		)
		contextSection.extend(content)

		return [contextSection]


@export
class DescribeEntity(BaseDirective, WithGenericsMixin, WithPortsMixin):
	"""
	This directive will be replaced by the description of a VHDL entity.
	"""

	has_content = True
	required_arguments = 0
	optional_arguments = 4

	option_spec = {
		"genericlist":   strip,
		"portlist":      strip,
		"architectures": strip,
		"referencedby":  strip,
	}

	def CreateDefinitionSection(self, entity: Entity) -> section:
		title = nodes.title(text="Definition")
		paragraph = nodes.literal_block(text=dedent(f"""\
		entity {entity.Identifier} is
		  generics (
		    MODULO : positive;
		    BITS   : positive := log2(MODULO)
		  );
		  ports (
		    Clock : std_logic;
		    Reset : std_logic
		  );
		end entity;
		"""))
		section = nodes.section(
			"",
			title,
			paragraph,
			ids=[f"{entity.NormalizedIdentifier}-definition"],
			classes=["vhdl", "vhdl-entity-definition-section"]
		)

		return section

	def CreateArchitectureSection(self, entity: Entity) -> section:
		section = nodes.section(
			ids=[f"{entity.NormalizedIdentifier}-architectures"],
			classes=["vhdl", "vhdl-entity-architectures-section"]
		)
		section += nodes.title(text="Architectures")
		section += nodes.paragraph(text=", ".join(entity.Architectures))

		return section

	def CreateReferencedBySection(self, entity: Entity) -> section:
		section = nodes.section(
			ids=[f"{entity.NormalizedIdentifier}-referenced-by"],
			classes=["vhdl", "vhdl-entity-referencedby-section"]
		)

		predecessors = entity.HierarchyVertex.Predecessors

		section += nodes.title(text="Referenced By")
		section += nodes.paragraph(text=f"Entity '{entity.Identifier}' is referenced from {len(predecessors)} code locations:")

		bulletList = nodes.bullet_list()
		section += bulletList

		for referencingVertex in predecessors:
			listItem = nodes.list_item()
			listItem += nodes.paragraph(text=repr(referencingVertex.Value))
			bulletList += listItem

		return section

	def CreateInnerHierarchySection(self, entity: Entity) -> section:
		section = nodes.section(
			ids=[f"{entity.NormalizedIdentifier}-hierarchy"],
			classes=["vhdl", "vhdl-entity-innerhierarchy-section"]
		)
		section += nodes.title(text="Inner Hierarchy")
		section += nodes.paragraph(text="diagram of inner instances")

		return section

	def ParseArchitecturesStyleOption(self, optionName: str) -> ArchitecturesStyle:
		try:
			option = self.options[optionName]
		except KeyError:
			try:
				option = self.defaultValues[optionName]
			except KeyError:
				return ArchitecturesStyle.Multiple

		if option == "never":
			return ArchitecturesStyle.Never
		elif option == "multiple":
			return ArchitecturesStyle.Multiple
		elif option == "always":
			return ArchitecturesStyle.Always
		else:
			raise ValueError(f"value '{option}' is not in list of choices: never, multiple, always.")

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		# FIXME: check with regexp
		# FIXME: better error message(s)
		if len(self.arguments) == 1:
			try:
				libraryName, entityName = self.arguments[0].split(".")
			except ValueError:
				raise ValueError(f"Parameter to 'vhdl:describeentity' has incorrect format.")
		else:
			raise ValueError(f"Parameter to 'vhdl:describeentity' directive has too many content lines ({len(self.arguments)}).")

		# TODO: Can this be done in an __init__ or so?
		self.directiveName = self.name.split(":")[1]
		self.defaultValues = self.env.config.vhdl_defaults[self.directiveName]

		# parse all directive options or use default values
		optionDefinition = self.ParseBooleanOption("definition", True)
		optionGenerics = self.ParseParameterStyleOption("genericlist")
		optionPorts = self.ParseParameterStyleOption("portlist")
		optionArchitectures = self.ParseArchitecturesStyleOption("architectures")
		optionReferencedBy = self.ParseBooleanOption("referencedby", True)
		optionHierarchy = self.ParseBooleanOption("hierarchy", True)

		# Get entity object from design
		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]  # FIXME: allow specification of design name or default design
		library = design.GetLibrary(libraryName.lower())
		entity = library.Entities[entityName.lower()]

		content = [
			nodes.title(text=entity.Identifier),
			nodes.paragraph(text=entity.Documentation)
		]

		if optionDefinition:
			content.append(self.CreateDefinitionSection(entity))

		if optionGenerics is not ParameterStyle.Never and len(entity.GenericItems) > 0:
			content.append(self.CreateGenericSection(entity, optionGenerics))
		if optionPorts is not ParameterStyle.Never and len(entity.PortItems) > 0:
			content.append(self.CreatePortSection(entity, optionPorts))

		if (optionArchitectures is ArchitecturesStyle.Always or
			(optionArchitectures is ArchitecturesStyle.Multiple and len(entity.Architectures) > 1)):
			content.append(self.CreateArchitectureSection(entity))

		if optionReferencedBy:
			content.append(self.CreateReferencedBySection(entity))

		if optionHierarchy:
			content.append(self.CreateInnerHierarchySection(entity))

		entitySection = nodes.section(
			ids=[entity.NormalizedIdentifier],
			classes=["vhdl", "vhdl-entity-section"]
		)
		entitySection.extend(content)

		return [entitySection]


@export
class DescribeArchitecture(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL architecture.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe architecture")

		return [paragraph]


@export
class DescribePackage(BaseDirective, WithGenericsMixin):
	"""
	This directive will be replaced by the description of a VHDL package.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = {
		"genericlist":   strip,
		"referencedby":  strip,
	}

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		# FIXME: check with regexp
		# FIXME: better error message(s)
		if len(self.arguments) == 1:
			try:
				libraryName, packageName = self.arguments[0].split(".")
			except ValueError:
				raise ValueError(f"Parameter to 'vhdl:describepackage' has incorrect format.")
		else:
			raise ValueError(f"Parameter to 'vhdl:describepackage' directive has too many content lines ({len(self.arguments)}).")

		# TODO: Can this be done in an __init__ or so?
		self.directiveName = self.name.split(":")[1]
		self.defaultValues = self.env.config.vhdl_defaults[self.directiveName]

		# parse all directive options or use default values
		optionDefinition = self.ParseBooleanOption("definition", True)
		optionGenerics = self.ParseParameterStyleOption("genericlist")
		optionReferencedBy = self.ParseBooleanOption("referencedby", True)

		# Get entity object from design
		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]  # FIXME: allow specification of design name or default design
		library = design.GetLibrary(libraryName.lower())
		package = library.Packages[packageName.lower()]

		content = [
			nodes.title(text=package.Identifier),
			nodes.paragraph(text=package.Documentation)
		]

		# if optionDefinition:
		# 	content.append(self.CreateDefinitionSection(package))
		if optionGenerics is not ParameterStyle.Never and len(package.GenericItems) > 0:
			content.append(self.CreateGenericSection(package, optionGenerics))
		# if optionReferencedBy:
		# 	content.append(self.CreateReferencedBySection(package))

		content.append(nodes.paragraph(text="Constants"))
		for constant in package.Constants.values():
			content.append(nodes.paragraph(text=constant.Identifiers))

		content.append(nodes.paragraph(text="Subprograms"))
		for subprogram in package.Subprograms.values():
			content.append(nodes.paragraph(text=subprogram.Identifiers))

		packageSection = nodes.section(
			ids=[package.NormalizedIdentifier],
			classes=["vhdl", "vhdl-package-section"]
		)
		packageSection.extend(content)

		return [packageSection]


@export
class DescribePackageBody(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL package body.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe package body")

		return [paragraph]


@export
class DescribeConfiguration(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL configuration.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 1

	option_spec = {
		"referencedby":  strip,
	}

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		# FIXME: check with regexp
		# FIXME: better error message(s)
		if len(self.arguments) == 1:
			try:
				libraryName, configurationName = self.arguments[0].split(".")
			except ValueError:
				raise ValueError(f"Parameter to 'vhdl:describepackage' has incorrect format.")
		else:
			raise ValueError(f"Parameter to 'vhdl:describepackage' directive has too many content lines ({len(self.arguments)}).")

		# TODO: Can this be done in an __init__ or so?
		self.directiveName = self.name.split(":")[1]
		self.defaultValues = self.env.config.vhdl_defaults[self.directiveName]

		# parse all directive options or use default values
		optionReferencedBy = self.ParseBooleanOption("referencedby", True)

		# Get entity object from design
		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]  # FIXME: allow specification of design name or default design
		library = design.GetLibrary(libraryName.lower())
		configuration = library.Configurations[configurationName.lower()]

		content = [
			nodes.title(text=configuration.Identifier),
			nodes.paragraph(text=configuration.Documentation)
		]

		# if optionReferencedBy:
		# 	content.append(self.CreateReferencedBySection(package))

		configurationSection = nodes.section(
			ids=[configuration.NormalizedIdentifier],
			classes=["vhdl", "vhdl-configuration-section"]
		)
		configurationSection.extend(content)

		return [configurationSection]
