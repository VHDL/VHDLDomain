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
from typing import Dict, Tuple, Any, Optional as Nullable, cast

from docutils import nodes
from pyGHDL.dom.NonStandard import Design as DOMDesign, Document as DOMDocument
from pyTooling.Decorators import export
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.extension import Extension

from VHDLDomain.Directive import DescribeDesign, DescribeLibrary, DescribeDocument, DescribeEntity, DescribeArchitecture
from VHDLDomain.Directive import DescribePackage, DescribePackageBody, DescribeConfiguration, DescribeContext
from VHDLDomain.Index import LibraryIndex, DocumentIndex, ComponentIndex, PackageIndex, SubprogramIndex, TypeIndex
from VHDLDomain.Role import DesignRole, LibraryRole, DocumentRole, ContextRole, EntityRole, ArchitectureRole, PackageRole, PackageBodyRole, ConfigurationRole


@export
class Design(DOMDesign):
	_baseDirectory: Nullable[Path]

	def __init__(self, name: str = None, baseDirectory: Path = None):
		"""
		Initializes a VHDL design.

		:param name:          Name of the design.
		:param baseDirectory: Base directory of the design.
		"""
		super().__init__(name)
		self._baseDirectory = baseDirectory

	@property
	def BaseDirectory(self) -> Path:
		return self._baseDirectory


@export
class Document(DOMDocument):
	@property
	def ShortPath(self) -> Path:
		design = cast(Design, self.Parent)
		if design._baseDirectory is None:
			return self._path
		else:
			return self._path.relative_to(design._baseDirectory)


@export
class VHDLDomain(Domain):
	name =  "vhdl"  #: The name of this domain
	label = "VHDL"  #: The label of this domain

	dependencies = [
	]  #: A list of other extensions this domain depends on.

	directives = {
		"describedesign":        DescribeDesign,
		# "describelibrary":       DescribeLibrary,
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
		"ent":      EntityRole(),
		# "arch":     ArchitectureRole,
		# "pack":     PackageRole,
		# "packbody": PackageBodyRole,
		# "config":   ConfigurationRole,
	}  #: A dictionary of all roles in this domain.

	indices = {
		LibraryIndex,
		DocumentIndex,
		ComponentIndex,
		PackageIndex,
		SubprogramIndex,
		TypeIndex
	}  #: A dictionary of all indices in this domain.

	configValues: Dict[str, Tuple[Any, str, Any]] = {
		"designs": ({}, "env", Dict),
		"defaults": ({}, "env", Dict),
	}  #: A dictionary of all configuration values used by this domain.

	initial_data = {
		"designs": {}
	}  #: A dictionary of all global data fields used by this domain.

	@property
	def Designs(self) -> Dict[str, Design]:
		return self.data["designs"]

	@staticmethod
	def ReadDesigns(sphinxApplication: Sphinx) -> None:
		"""
		Call back for Sphinx ``builder-inited`` event.

		This callback will read the configuration variable ``vhdl_designs`` and parse the found VHDL source files.

		.. seealso::

		   Sphinx *builder-inited* event
		     See http://sphinx-doc.org/extdev/appapi.html#event-builder-inited

		:param sphinxApplication: The Sphinx application.
		:return:
		"""
		print(f"Callback: builder-inited -> ReadDesigns")
		print(f"[VHDL] Reading designs ...")

		# Get modules to build documentation for
		designConfigurations: Dict[str, Path] = sphinxApplication.config.vhdl_designs
		print(designConfigurations)
		if not designConfigurations:
			return

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
			("lib_StopWatch", Path("toplevel.vhdl")),
		)

		vhdlDomain: Domain = sphinxApplication.env.domains[VHDLDomain.name]
		designs: Dict[str, Design] = vhdlDomain.data["designs"]

		for designName, designRoot in designConfigurations.items():
			if not isinstance(designName, str):
				print(f"[VHDL][ERROR] '{designName}' is not a string.")
			if not isinstance(designRoot, Path):
				print(f"[VHDL][ERROR] '{designRoot}' is not a Path.")
			print(f"[VHDL]   Loading design '{designName}' ...")
			if not designRoot.exists():
				print(f"[VHDL][ERROR] Path '{designRoot}' does not exist.")
			design = Design(designName, designRoot)
			design.LoadDefaultLibraries()
			for libraryName, file in _stopwatchFiles:
				sourceFile = designRoot / file

				print(f"[VHDL]     Parsing '{sourceFile}'")
				document = Document(sourceFile)
				design.AddDocument(document, design.GetLibrary(libraryName))

			print(f"[VHDL]     Analyzing design '{designName}' ...")
			design.Analyze()

			designs[designName] = design


# 	@staticmethod
# 	def ReadDesigns(app: Sphinx, docname: str, source: str) -> None:
# 		print(f"Callback: source-read -> ReadDesigns")
# 		print(docname)
# #		print(source)

	callbacks = {
		"builder-inited": ReadDesigns,
		# "source-read": ReadDesigns
	}  #: A dictionary of all callbacks used by this domain.

	def resolve_xref(
		self,
		env: BuildEnvironment,
		fromdocname: str,
		builder: Builder,
		typ: str,
		target: str,
		node: pending_xref,
		contnode: nodes.Element
	) -> Nullable[nodes.Element]:
		raise NotImplementedError()


@export
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

	return {
		"version": __version__,                          # version of the extension
		"env_version": int(__version__.split(".")[0]),   # version of the data structure stored in the environment
		'parallel_read_safe': False,                     # Not yet evaluated, thus false
		'parallel_write_safe': True,                     # Internal data structure is used read-only, thus no problems will occur by parallel writing.
	}
