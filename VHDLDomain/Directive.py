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
import dataclasses
from typing import List, Dict

from docutils import nodes
from docutils.nodes import Node, section
from pyGHDL.dom.DesignUnit import Entity
from pyGHDL.dom.InterfaceItem import GenericConstantInterfaceItem, PortSignalInterfaceItem
from pyTooling.Decorators import export
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain


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

	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)


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
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe context")

		return [paragraph]


@export
class DescribeEntity(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL entity.
	"""

	has_content = True
	required_arguments = 0
	optional_arguments = 0

	def CreateDefinitionSection(self, entity: Entity) -> section:
		title = nodes.title(text="Definition")
		paragraph = nodes.paragraph(text="code block")
		section = nodes.section("", title, paragraph, ids=[f"{entity.Identifier}-definition"])

		return section

	def CreateGenericSection(self, entity: Entity) -> section:
		title = nodes.title(text="Generics")
		paragraph = nodes.paragraph(text="list of all generics")

		generics = []
		for generic in entity.GenericItems:
			if isinstance(generic, GenericConstantInterfaceItem):
				genericTitle = nodes.title(text=", ".join(generic.Identifiers))
				genericParagraph = nodes.paragraph(text=generic.Documentation)
				generics.append(nodes.section("", genericTitle, genericParagraph, ids=[f"{entity.Identifier}-generic-{nID}" for nID in generic.NormalizedIdentifiers]))

		section = nodes.section("", title, paragraph, *generics, ids=[f"{entity.Identifier}-generics"])

		return section

	def CreatePortSection(self, entity: Entity) -> section:
		title = nodes.title(text="Ports")
		paragraph = nodes.paragraph(text="list of all ports")

		ports = []
		for port in entity.PortItems:
			if isinstance(port, PortSignalInterfaceItem):
				portTitle = nodes.title(text=", ".join(port.Identifiers))
				portParagraph = nodes.paragraph(text=port.Documentation)
				ports.append(nodes.section("", portTitle, portParagraph, ids=[f"{entity.Identifier}-port-{nID}" for nID in port.NormalizedIdentifiers]))

		section = nodes.section("", title, paragraph, *ports, ids=[f"{entity.Identifier}-ports"])

		return section

	def CreateArchitectureSection(self, entity: Entity) -> section:
		title = nodes.title(text="Architectures")
		paragraph = nodes.paragraph(text=", ".join(entity.Architectures))
		section = nodes.section("", title, paragraph, ids=[f"{entity.Identifier}-architectures"])

		return section

	def CreateReferencedBySection(self, entity: Entity) -> section:
		title = nodes.title(text="Referenced By")
		paragraph = nodes.paragraph(text="list of usages and back links")
		section = nodes.section("", title, paragraph, ids=[f"{entity.Identifier}-referenced-by"])

		return section

	def CreateInnerHierarchySection(self, entity: Entity) -> section:
		title = nodes.title(text="Inner Hierarchy")
		paragraph = nodes.paragraph(text="diagram of inner instances")
		section = nodes.section("", title, paragraph, ids=[f"{entity.Identifier}-hierarchy"])

		return section

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		if len(self.content) == 1:
			try:
				libraryName, entityName = self.content[0].split(".")
			except ValueError:
				raise ValueError(f"Parameter to 'vhdl:describeentity' has incorrect format.")
		else:
			raise ValueError(f"Parameter to 'vhdl:describeentity' directive has too many content lines.")

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]
		library = design.GetLibrary(libraryName.lower())
		entity = library.Entities[entityName.lower()]

		entityDescriptionParagraph = nodes.paragraph(text=entity.Documentation)

		definitionSection = self.CreateDefinitionSection(entity)
		genericSection = self.CreateGenericSection(entity)
		portSection = self.CreatePortSection(entity)
		architecturesSection = self.CreateArchitectureSection(entity)
		referencedBySection = self.CreateReferencedBySection(entity)
		innerHierarchySection = self.CreateInnerHierarchySection(entity)

		entityTitle = nodes.title(text=entity.Identifier)
		entitySection = nodes.section(
			"",
			entityTitle,
			entityDescriptionParagraph,
			definitionSection,
			genericSection,
			portSection,
			architecturesSection,
			referencedBySection,
			innerHierarchySection,
			ids=[entity.NormalizedIdentifier]
		)

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
class DescribePackage(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL package.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe package")

		return [paragraph]


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
	optional_arguments = 0

	def run(self) -> List[Node]:
		from VHDLDomain import Design

		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe configuration")

		return [paragraph]
