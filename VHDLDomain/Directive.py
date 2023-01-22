from typing import List

from docutils import nodes
from pyTooling.Decorators import export
from sphinx.directives import ObjectDescription


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
		paragraph = nodes.paragraph(text="Describe design")

		return [paragraph]


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
