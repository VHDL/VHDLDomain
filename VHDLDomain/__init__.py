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

.. admonition:: Copyright Information

   :copyright: Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany
   :copyright: Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
   :license: Apache License, Version 2.0
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2016-2023, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.1.0"

from pathlib import Path
from typing import Dict, Tuple, Any, Optional as Nullable

from docutils import nodes
from pyGHDL.dom.NonStandard import Design, Document
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.domains import Domain

from VHDLDomain.Directive import DescribeDesign, DescribeLibrary, DescribeDocument, DescribeEntity, DescribeArchitecture
from VHDLDomain.Directive import DescribePackage, DescribePackageBody, DescribeConfiguration, DescribeContext
from VHDLDomain.Index import ComponentIndex, PackageIndex, SubprogramIndex, TypeIndex, DUMMY
from VHDLDomain.Role import DesignRole, LibraryRole, DocumentRole, ContextRole, EntityRole, ArchitectureRole, PackageRole, PackageBodyRole, ConfigurationRole


class VHDLDomain(Domain):
	name =  "vhdl"  #: The name of this domain
	label = "VHDL"  #: The label of this domain

	dependencies = [
	]  #: A list of other extensions this domain depends on.

	directives = {
		# "describedesign":        DescribeDesign,
		"describelibrary":       DescribeLibrary,
		# "describedocument":      DescribeDocument,
		# "describecontext":       DescribeContext,
		"describeentity":        DescribeEntity,
		# "describearchitecture":  DescribeArchitecture,
		# "describepackage":       DescribePackage,
		# "describepackagebody":   DescribePackageBody,
		# "describeconfiguration": DescribeConfiguration,
	}  #: A dictionary of all directives in this domain.

	roles = {
		# "design":   DesignRole,
		# "lib":      LibraryRole,
		# "doc":      DocumentRole,
		# "ctx":      ContextRole,
		"ent":      EntityRole,
		# "arch":     ArchitectureRole,
		# "pack":     PackageRole,
		# "packbody": PackageBodyRole,
		# "config":   ConfigurationRole,
	}  #: A dictionary of all roles in this domain.

	indices = {
		ComponentIndex,
		PackageIndex,
		SubprogramIndex,
		TypeIndex
	}  #: A dictionary of all indices in this domain.

	configValues: Dict[str, Tuple[Any, str, Any]] = {
		"designs": ({}, "env", Dict),
	}  #: A dictionary of all configuration values used by this domain.

	initial_data = {
	}

	@staticmethod
	def ReadDesigns(app: Sphinx, docname: str, source: str) -> None:
		print(f"Callback: source-read -> ReadDesigns")
		print(docname)
#		print(source)

	callbacks = {
		"source-read": ReadDesigns
	}  #: A dictionary of all callbacks used by this domain.

	def resolve_xref(
		self,
		env: 'BuildEnvironment',
		fromdocname: str,
		builder: 'Builder',
		typ: str,
		target: str,
		node: pending_xref,
		contnode: nodes.Element
	) -> Nullable[nodes.Element]:
		raise NotImplementedError()


def setup(sphinxApplication: Sphinx):
	"""
	Extension setup function registering the VHDL domain in Sphinx.

	:param sphinxApplication: The Sphinx application.
	:return:                  Dictionary containing the extension version and some properties.
	"""
	sphinxApplication.add_domain(VHDLDomain)
	for eventName, callback in VHDLDomain.callbacks.items():
		sphinxApplication.connect(eventName, callback)
	for configName, (configDefault, configRebuilt, configTypes) in VHDLDomain.configValues.items():
		sphinxApplication.add_config_value(f"{VHDLDomain.name}_{configName}", configDefault, configRebuilt, configTypes)

	_packageFiles = (
		("lib_Utilities", Path("Utilities.pkg.vhdl")),
		("lib_Utilities", Path("Utilities.ctx.vhdl")),
		("lib_StopWatch", Path("StopWatch.pkg.vhdl")),
		("lib_StopWatch", Path("StopWatch.ctx.vhdl")),
	)
	_encoderFiles = _packageFiles + (
		("lib_StopWatch", Path("seg7_Encoder.vhdl")),
		("lib_StopWatch", Path("toplevel.Encoder.vhdl")),
	)
	_displayFiles = _packageFiles + (
		("lib_StopWatch", Path("Counter.vhdl")),
		("lib_StopWatch", Path("seg7_Encoder.vhdl")),
		("lib_StopWatch", Path("seg7_Display.vhdl")),
		("lib_StopWatch", Path("seg7_Display.cfg.vhdl")),
		("lib_StopWatch", Path("toplevel.Display.vhdl")),
	)
	_stopwatchFiles = _packageFiles + (
		("lib_Utilities", Path("Counter.vhdl")),
		("lib_StopWatch", Path("seg7_Encoder.vhdl")),
		("lib_StopWatch", Path("seg7_Display.vhdl")),
		("lib_StopWatch", Path("seg7_Display.cfg.vhdl")),
		("lib_StopWatch", Path("StopWatch.vhdl")),
		("lib_Utilities", Path("sync_Bits.vhdl")),
		("lib_Utilities", Path("Debouncer.vhdl")),
		("lib_StopWatch", Path("toplevel.StopWatch.vhdl")),
	)

	print("=" * 40)
	print(Path.cwd())
	design = Design()
	design.LoadDefaultLibraries()
	designRoot = (Path.cwd() / "../examples/StopWatch").resolve()
	for libraryName, file in _stopwatchFiles:
		document = Document(designRoot / file)
		design.AddDocument(document, design.GetLibrary(libraryName))
	print("-" * 40)
	design.Analyze()

	DUMMY.VAR = design
	print("=" * 40)

	return {
		"version": __version__,
		'parallel_read_safe': False,
		'parallel_write_safe': False,
	}
