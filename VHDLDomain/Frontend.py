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
The designs a documentation describes, as declared in :file:`conf.py`, and the frontend reading their source files.

A design is declared in the configuration value ``vhdl_designs`` by its name, the directory of its source files, and
its libraries with their source files:

.. code-block:: Python

   vhdl_designs = {
     "StopWatch": {
       "directory": "../examples/StopWatch",
       "libraries": {
         "lib_Utilities": ["Utilities.pkg.vhdl", "Counter.vhdl"],
         "lib_StopWatch": ["StopWatch.pkg.vhdl", "*.vhdl"],
       },
     },
   }

The directory is relative to the Sphinx source directory; a file is relative to the directory and may be a glob
pattern. With the key ``pages`` - a document name, e.g. ``"StopWatch"`` -, the design gets a generated page per library
and design unit below that document name (see :mod:`VHDLDomain.Pages`). The frontend - pyGHDL.dom, the only one keeping
the comments a documentation is extracted from - parses the files into a :class:`pyVHDLModel.Design` and analyzes it.
"""
from __future__            import annotations

from pathlib               import Path
from typing                import Any, Mapping, Optional as Nullable

from sphinx.errors         import ExtensionError

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError
from pyTooling.MetaClasses import ExtendedType

from pyVHDLModel           import Design


@export
class VHDLDomainException(ExtensionError):
	"""
	Base-class of the exceptions of the VHDL domain.
	"""


@export
class DesignConfigurationError(VHDLDomainException):
	"""
	A design's entry in ``vhdl_designs`` is malformed.
	"""


@export
class DesignConfiguration(metaclass=ExtendedType, slots=True):
	"""
	A design declared in ``vhdl_designs``: its name, the directory of its source files, and its libraries' files.
	"""

	_name:      str                    #: Name of the design, the key in ``vhdl_designs``.
	_directory: Path                   #: Directory of the source files.
	_libraries: dict[str, list[Path]]  #: Source files, by library name, in declaration order.
	_pages:     Nullable[str]          #: Document name the design's pages are generated below, or ``None`` for none.

	def __init__(
		self,
		name:      str,
		directory: Path,
		libraries: Mapping[str, list[Path]],
		pages:     Nullable[str] = None
	) -> None:
		"""
		Initializes a design's configuration.

		:param name:        Name of the design.
		:param directory:   Directory of the source files.
		:param libraries:   Source files, by library name.
		:param pages:       Optional, document name the design's pages are generated below. Default: ``None``, no pages.
		:raises ValueError: If parameter 'name' is ``None`` or empty.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'directory' is ``None``.
		:raises TypeError:  If parameter 'directory' is not of type :class:`~pathlib.Path`.
		:raises ValueError: If parameter 'libraries' is ``None``.
		:raises TypeError:  If parameter 'libraries' is not a mapping.
		:raises TypeError:  If parameter 'pages' is not of type :class:`str`.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if directory is None:
			raise ValueError("Parameter 'directory' is None.")
		elif not isinstance(directory, Path):
			ex = TypeError("Parameter 'directory' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(directory)}'.")
			raise ex

		if libraries is None:
			raise ValueError("Parameter 'libraries' is None.")
		elif not isinstance(libraries, Mapping):
			ex = TypeError("Parameter 'libraries' is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraries)}'.")
			raise ex

		if pages is not None and not isinstance(pages, str):
			ex = TypeError("Parameter 'pages' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(pages)}'.")
			raise ex

		self._name =      name
		self._directory = directory
		self._libraries = {libraryName: list(files) for libraryName, files in libraries.items()}
		self._pages =     pages

	@classmethod
	def Parse(cls, name: Any, value: Any, sourceDirectory: Path) -> DesignConfiguration:
		"""
		Read a design's entry of ``vhdl_designs``.

		:param name:                      The entry's key, the design's name.
		:param value:                     The entry's value, a mapping with the keys ``directory``, ``libraries`` and
		                                  ``pages``.
		:param sourceDirectory:           The Sphinx source directory, which ``directory`` is relative to.
		:returns:                         The design's configuration.
		:raises DesignConfigurationError: If the key isn't a string.
		:raises DesignConfigurationError: If the key is empty.
		:raises DesignConfigurationError: If the value isn't a mapping.
		:raises DesignConfigurationError: If the value has a key other than ``directory``, ``libraries`` and ``pages``.
		:raises DesignConfigurationError: If ``directory`` isn't a string or a path.
		:raises DesignConfigurationError: If ``libraries`` isn't a mapping.
		:raises DesignConfigurationError: If a library name isn't a string, or is empty.
		:raises DesignConfigurationError: If a library's value isn't a list of file names or paths.
		:raises DesignConfigurationError: If ``pages`` isn't a string.
		:raises DesignConfigurationError: If ``pages`` isn't a relative document name. |br|
		                                  Use a name like 'designs/StopWatch', separated by '/', without '.' or '..'.
		"""
		if not isinstance(name, str):
			ex = DesignConfigurationError("vhdl_designs: Design name is not a string.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise DesignConfigurationError("vhdl_designs: Design name is empty.")

		if not isinstance(value, Mapping):
			ex = DesignConfigurationError(f"vhdl_designs['{name}']: Value is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		if len(unknownKeys := set(value) - {"directory", "libraries", "pages"}) > 0:
			keys = ", ".join(sorted(map(repr, unknownKeys)))
			ex = DesignConfigurationError(f"vhdl_designs['{name}']: Unknown key(s) {keys}.")
			ex.add_note("Allowed keys: 'directory', 'libraries', 'pages'")
			raise ex

		directory = value.get("directory", ".")
		if not isinstance(directory, (str, Path)):
			ex = DesignConfigurationError(f"vhdl_designs['{name}'].directory: Value is not a string or a path.")
			ex.add_note(f"Got type '{getFullyQualifiedName(directory)}'.")
			raise ex

		libraries = value.get("libraries", {})
		if not isinstance(libraries, Mapping):
			ex = DesignConfigurationError(f"vhdl_designs['{name}'].libraries: Value is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(libraries)}'.")
			raise ex

		files: dict[str, list[Path]] = {}
		for libraryName, libraryFiles in libraries.items():
			if not isinstance(libraryName, str):
				ex = DesignConfigurationError(f"vhdl_designs['{name}'].libraries: Library name is not a string.")
				ex.add_note(f"Got type '{getFullyQualifiedName(libraryName)}'.")
				raise ex
			elif libraryName == "":
				raise DesignConfigurationError(f"vhdl_designs['{name}'].libraries: Library name is empty.")
			elif not isinstance(libraryFiles, (list, tuple)):
				ex = DesignConfigurationError(f"vhdl_designs['{name}'].libraries['{libraryName}']: Value is not a list.")
				ex.add_note(f"Got type '{getFullyQualifiedName(libraryFiles)}'.")
				raise ex

			for file in libraryFiles:
				if not isinstance(file, (str, Path)):
					ex = DesignConfigurationError(
						f"vhdl_designs['{name}'].libraries['{libraryName}']: File is not a string or a path."
					)
					ex.add_note(f"Got type '{getFullyQualifiedName(file)}'.")
					raise ex

			files[libraryName] = [Path(file) for file in libraryFiles]

		if (pages := value.get("pages", None)) is not None:
			if not isinstance(pages, str):
				ex = DesignConfigurationError(f"vhdl_designs['{name}'].pages: Value is not a string.")
				ex.add_note(f"Got type '{getFullyQualifiedName(pages)}'.")
				raise ex

			parts = pages.strip("/").split("/")
			if "\\" in pages or any(part in ("", ".", "..") for part in parts):
				ex = DesignConfigurationError(f"vhdl_designs['{name}'].pages: '{pages}' is not a relative document name.")
				ex.add_note("Use a name like 'designs/StopWatch', separated by '/', without '.' or '..'.")
				raise ex

			pages = "/".join(parts)

		return cls(name, (sourceDirectory / directory).resolve(), files, pages)

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the design's name (:attr:`_name`).

		:returns: The name of the design.
		"""
		return self._name

	@readonly
	def Directory(self) -> Path:
		"""
		Read-only property to access the directory of the source files (:attr:`_directory`).

		:returns: The directory.
		"""
		return self._directory

	@readonly
	def Pages(self) -> Nullable[str]:
		"""
		Read-only property to access the document name the design's pages are generated below (:attr:`_pages`).

		:returns: The document name, or ``None`` if the design has no pages.
		"""
		return self._pages

	@readonly
	def Libraries(self) -> dict[str, list[Path]]:
		"""
		Read-only property to access the source files by library name, as declared (:attr:`_libraries`).

		:returns: Dictionary of the declared file names or glob patterns, indexed by library name.
		"""
		return self._libraries

	def SourceFiles(self) -> dict[str, list[Path]]:
		"""
		Return the source files of every library: the declared files, and the files a glob pattern matches, sorted.

		A file declared twice in a library - also by a pattern - is listed once, at its first position.

		:returns:                         Dictionary of the source files, indexed by library name.
		:raises DesignConfigurationError: If a declared file doesn't exist, or a pattern matches no file.
		"""
		result: dict[str, list[Path]] = {}
		for libraryName, declaredFiles in self._libraries.items():
			files: list[Path] = []
			for declaredFile in declaredFiles:
				if any(character in str(declaredFile) for character in "*?["):
					if len(matches := sorted(self._directory.glob(str(declaredFile)))) == 0:
						ex = DesignConfigurationError(
							f"vhdl_designs['{self._name}'].libraries['{libraryName}']: Pattern '{declaredFile}' matches no file."
						)
						ex.add_note(f"Searched in '{self._directory}'.")
						raise ex
				elif not (path := self._directory / declaredFile).is_file():
					ex = DesignConfigurationError(
						f"vhdl_designs['{self._name}'].libraries['{libraryName}']: File '{declaredFile}' doesn't exist."
					)
					ex.add_note(f"Searched in '{self._directory}'.")
					raise ex
				else:
					matches = [path]

				for match in matches:
					if match not in files:
						files.append(match)

			result[libraryName] = files

		return result

	def Load(self) -> Design:
		"""
		Parse the source files with pyGHDL.dom into a design, and analyze it.

		:returns:                         The analyzed design.
		:raises MissingDependencyError:   If pyGHDL isn't installed.
		:raises DesignConfigurationError: If a declared file doesn't exist, or a pattern matches no file.
		"""
		try:
			from pyGHDL.dom.NonStandard import Design as GHDLDesign, Document as GHDLDocument
		except ImportError as ex:
			raise MissingDependencyError(dependency="pyGHDL") from ex

		sourceFiles = self.SourceFiles()

		design = GHDLDesign(self._name)
		design.LoadDefaultLibraries()
		for libraryName, files in sourceFiles.items():
			library = design.GetLibrary(libraryName)
			for file in files:
				design.AddDocument(GHDLDocument(file), library)

		design.Analyze()

		return design
