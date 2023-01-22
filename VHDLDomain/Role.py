from pyTooling.Decorators import export
from sphinx.roles import XRefRole


@export
class DesignRole(XRefRole):
	"""
	This role will reference a VHDL design.
	"""


@export
class LibraryRole(XRefRole):
	"""
	This role will reference a VHDL library.
	"""


@export
class DocumentRole(XRefRole):
	"""
	This role will reference a VHDL document.
	"""


@export
class ContextRole(XRefRole):
	"""
	This role will reference a context.
	"""


@export
class EntityRole(XRefRole):
	"""
	This role will reference a entity.
	"""


@export
class ArchitectureRole(XRefRole):
	"""
	This role will reference an architecture.
	"""


@export
class ComponentRole(XRefRole):
	"""
	This role will reference a component.
	"""


@export
class PackageRole(XRefRole):
	"""
	This role will reference a package.
	"""


@export
class PackageBodyRole(XRefRole):
	"""
	This role will reference a package body.
	"""


@export
class ConfigurationRole(XRefRole):
	"""
	This role will reference a configuration.
	"""


@export
class TypeRole(XRefRole):
	"""
	This role will reference a type.
	"""


@export
class FunctionRole(XRefRole):
	"""
	This role will reference a function.
	"""


@export
class ProcedureRole(XRefRole):
	"""
	This role will reference a procedure.
	"""


@export
class ConstantRole(XRefRole):
	"""
	This role will reference a constant.
	"""


@export
class GenericRole(XRefRole):
	"""
	This role will reference a generic.
	"""


@export
class PortRole(XRefRole):
	"""
	This role will reference a port.
	"""


@export
class ParameterRole(XRefRole):
	"""
	This role will reference a parameter.
	"""
