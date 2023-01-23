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
from typing import List, Dict

from docutils import nodes
from pyGHDL.dom.NonStandard import Design
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


@export
class DescribeDesign(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL design.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List:
		vhdlDomain: Domain = self.env.domains["vhdl"]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]
		design = designs["StopWatch"]

		paragraph = nodes.paragraph(text="Describe design")

		items = []
		for document in design.Documents:
			term = nodes.term(text=f"{document.ShortPath}")
			description = nodes.paragraph(text=f"{document.Documentation}")
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

	def run(self) -> List:
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

	def run(self) -> List:
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

	def run(self) -> List:
		paragraph = nodes.paragraph(text="Describe context")

		return [paragraph]


@export
class DescribeEntity(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL entity.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List:
		paragraph = nodes.paragraph(text="Describe entity")

		return [paragraph]


@export
class DescribeArchitecture(BaseDirective):
	"""
	This directive will be replaced by the description of a VHDL architecture.
	"""

	has_content = False
	required_arguments = 0
	optional_arguments = 0

	def run(self) -> List:
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

	def run(self) -> List:
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

	def run(self) -> List:
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

	def run(self) -> List:
		paragraph = nodes.paragraph(text="Describe configuration")

		return [paragraph]
