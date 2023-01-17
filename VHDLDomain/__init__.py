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

from pyGHDL.dom.NonStandard import Design, Document
from sphinx.application import Sphinx
from sphinx.domains import Domain

from VHDLDomain.Index import ComponentIndex, PackageIndex, SubprogramIndex, TypeIndex, DUMMY


class VHDLDomain(Domain):
	name =  "vhdl"
	label = "VHDL"
	initial_data = {}
	directives = {}
	roles = {}
	indices = {
		ComponentIndex,
		PackageIndex,
		SubprogramIndex,
		TypeIndex
	}


def setup(sphinxApplication: Sphinx):
	sphinxApplication.add_domain(VHDLDomain)
	# sphinxApplication.add_config_value('vhdl_autodoc_source_path', '.', 'env', [str])

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
