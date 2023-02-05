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

This module contains all the roles of the VHDL domain.
"""
from pyTooling.Decorators import export
from sphinx.roles import XRefRole


@export
class BaseRole(XRefRole):
	pass


@export
class DesignRole(BaseRole):
	"""
	This role will reference a VHDL design.
	"""


@export
class LibraryRole(BaseRole):
	"""
	This role will reference a VHDL library.
	"""


@export
class DocumentRole(BaseRole):
	"""
	This role will reference a VHDL document.
	"""


@export
class ContextRole(BaseRole):
	"""
	This role will reference a context.
	"""


@export
class EntityRole(BaseRole):
	"""
	This role will reference a entity.
	"""


@export
class ArchitectureRole(BaseRole):
	"""
	This role will reference an architecture.
	"""


@export
class ComponentRole(BaseRole):
	"""
	This role will reference a component.
	"""


@export
class PackageRole(BaseRole):
	"""
	This role will reference a package.
	"""


@export
class PackageBodyRole(BaseRole):
	"""
	This role will reference a package body.
	"""


@export
class ConfigurationRole(BaseRole):
	"""
	This role will reference a configuration.
	"""


@export
class TypeRole(BaseRole):
	"""
	This role will reference a type.
	"""


@export
class FunctionRole(BaseRole):
	"""
	This role will reference a function.
	"""


@export
class ProcedureRole(BaseRole):
	"""
	This role will reference a procedure.
	"""


@export
class ConstantRole(BaseRole):
	"""
	This role will reference a constant.
	"""


@export
class GenericRole(BaseRole):
	"""
	This role will reference a generic.
	"""


@export
class PortRole(BaseRole):
	"""
	This role will reference a port.
	"""


@export
class ParameterRole(BaseRole):
	"""
	This role will reference a parameter.
	"""
