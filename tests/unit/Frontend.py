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
"""Unit tests for reading the designs declared in ``vhdl_designs``."""
from pathlib                  import Path
from tempfile                 import TemporaryDirectory
from unittest                 import skipUnless
from unittest.mock            import patch

from pyTooling.Exceptions     import MissingDependencyError
from pyTooling.Testing        import Testcase

from VHDLDomain.Frontend      import DesignConfiguration, DesignConfigurationError

try:
	from pyGHDL.dom.NonStandard import Design as GHDLDesign  # noqa: F401
	pyGHDLIsUsable = True
except Exception:
	pyGHDLIsUsable = False


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: The StopWatch example of this repository.
STOPWATCH = Path(__file__).parent.parent.parent / "examples" / "StopWatch"


class Parse(Testcase):
	def test_Design(self) -> None:
		configuration = DesignConfiguration.Parse(
			"StopWatch",
			{"directory": "examples", "libraries": {"lib_A": ["a.vhdl", Path("b.vhdl")], "lib_B": []}},
			Path("/doc")
		)

		self.assertEqual("StopWatch", configuration.Name)
		self.assertEqual(Path("/doc/examples").resolve(), configuration.Directory)
		self.assertEqual({"lib_A": [Path("a.vhdl"), Path("b.vhdl")], "lib_B": []}, configuration.Libraries)

	def test_Defaults(self) -> None:
		configuration = DesignConfiguration.Parse("StopWatch", {}, Path("/doc"))

		self.assertEqual(Path("/doc").resolve(), configuration.Directory)
		self.assertEqual({}, configuration.Libraries)
		self.assertIsNone(configuration.Pages)

	def test_Pages(self) -> None:
		"""Surrounding slashes are removed from the document name."""
		configuration = DesignConfiguration.Parse("StopWatch", {"pages": "/designs/StopWatch/"}, Path("/doc"))

		self.assertEqual("designs/StopWatch", configuration.Pages)

	def test_Errors(self) -> None:
		for name, value, message in (
			(1,   {},                               "vhdl_designs: Design name is not a string."),
			("",  {},                               "vhdl_designs: Design name is empty."),
			("D", [],                               "vhdl_designs['D']: Value is not a mapping."),
			("D", {"files": []},                    "vhdl_designs['D']: Unknown key(s) 'files'."),
			("D", {"directory": 1},                 "vhdl_designs['D'].directory: Value is not a string or a path."),
			("D", {"libraries": []},                "vhdl_designs['D'].libraries: Value is not a mapping."),
			("D", {"libraries": {1: []}},           "vhdl_designs['D'].libraries: Library name is not a string."),
			("D", {"libraries": {"": []}},          "vhdl_designs['D'].libraries: Library name is empty."),
			("D", {"libraries": {"lib": "a.vhdl"}}, "vhdl_designs['D'].libraries['lib']: Value is not a list."),
			("D", {"libraries": {"lib": [1]}},      "vhdl_designs['D'].libraries['lib']: File is not a string or a path."),
			("D", {"pages": 1},                     "vhdl_designs['D'].pages: Value is not a string."),
			("D", {"pages": "a/../b"},              "vhdl_designs['D'].pages: 'a/../b' is not a relative document name."),
			("D", {"pages": "a\\b"},                "vhdl_designs['D'].pages: 'a\\b' is not a relative document name."),
		):
			with self.subTest(message=message):
				with self.assertRaises(DesignConfigurationError) as context:
					DesignConfiguration.Parse(name, value, Path("/doc"))

				self.assertEqual(message, str(context.exception))


class Constructor(Testcase):
	def test_Checks(self) -> None:
		for name, directory, libraries, pages, exception in (
			(None,  Path("."), {},   None, ValueError),
			(1,     Path("."), {},   None, TypeError),
			("",    Path("."), {},   None, ValueError),
			("D",   None,      {},   None, ValueError),
			("D",   ".",       {},   None, TypeError),
			("D",   Path("."), None, None, ValueError),
			("D",   Path("."), [],   None, TypeError),
			("D",   Path("."), {},   1,    TypeError),
		):
			with self.subTest(name=name, directory=directory, libraries=libraries, pages=pages):
				with self.assertRaises(exception):
					DesignConfiguration(name, directory, libraries, pages)


class SourceFiles(Testcase):
	_directory: TemporaryDirectory
	_path:      Path

	def setUp(self) -> None:
		self._directory = TemporaryDirectory()
		self._path = Path(self._directory.name)
		for name in ("a.vhdl", "b.vhdl", "c.vhd"):
			(self._path / name).write_text("", encoding="utf-8")

	def tearDown(self) -> None:
		self._directory.cleanup()

	def test_Files(self) -> None:
		configuration = DesignConfiguration("D", self._path, {"lib": [Path("b.vhdl"), Path("a.vhdl")]})

		self.assertEqual({"lib": [self._path / "b.vhdl", self._path / "a.vhdl"]}, configuration.SourceFiles())

	def test_Pattern(self) -> None:
		"""A pattern's matches are sorted; a file already listed keeps its position."""
		configuration = DesignConfiguration("D", self._path, {"lib": [Path("b.vhdl"), Path("*.vhd*")]})

		self.assertEqual(
			{"lib": [self._path / "b.vhdl", self._path / "a.vhdl", self._path / "c.vhd"]},
			configuration.SourceFiles()
		)

	def test_MissingFile(self) -> None:
		configuration = DesignConfiguration("D", self._path, {"lib": [Path("d.vhdl")]})

		with self.assertRaises(DesignConfigurationError) as context:
			configuration.SourceFiles()

		self.assertEqual("vhdl_designs['D'].libraries['lib']: File 'd.vhdl' doesn't exist.", str(context.exception))

	def test_NoMatch(self) -> None:
		configuration = DesignConfiguration("D", self._path, {"lib": [Path("*.vhdx")]})

		with self.assertRaises(DesignConfigurationError) as context:
			configuration.SourceFiles()

		self.assertEqual("vhdl_designs['D'].libraries['lib']: Pattern '*.vhdx' matches no file.", str(context.exception))


class Load(Testcase):
	def test_WithoutPyGHDL(self) -> None:
		configuration = DesignConfiguration("StopWatch", STOPWATCH, {"lib_StopWatch": [Path("Counter.vhdl")]})

		with patch.dict("sys.modules", {"pyGHDL": None, "pyGHDL.dom": None, "pyGHDL.dom.NonStandard": None}):
			with self.assertRaises(MissingDependencyError) as context:
				configuration.Load()

		self.assertIsInstance(context.exception.__cause__, ImportError)

	@skipUnless(pyGHDLIsUsable, "pyGHDL isn't installed, or doesn't import with this pyTooling and pyVHDLModel.")
	def test_StopWatch(self) -> None:  # pragma: no cover
		configuration = DesignConfiguration(
			"StopWatch", STOPWATCH,
			{
				"lib_Utilities": [
					Path(f"{name}.vhdl") for name in ("Utilities.pkg", "Utilities.ctx", "Counter", "sync_Bits", "Debouncer")
				],
				"lib_StopWatch": [
					Path(f"{name}.vhdl") for name in (
						"StopWatch.pkg", "StopWatch.ctx", "seg7_Encoder", "seg7_Display", "seg7_Display.cfg", "StopWatch",
						"toplevel"
					)
				],
			}
		)

		design = configuration.Load()

		self.assertEqual("StopWatch", design.Name)
		self.assertIn("counter", design.Libraries["lib_utilities"].Entities)
		self.assertIn("seg7_encoder", design.Libraries["lib_stopwatch"].Entities)
