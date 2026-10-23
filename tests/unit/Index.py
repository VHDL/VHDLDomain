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
"""Unit tests for the indices of the Sphinx domain ``vhdl``."""
from textwrap              import dedent

from sphinx.domains        import IndexEntry

from VHDLDomain.Index      import EntityIndex, PackageIndex, SubprogramIndex, TypeIndex

from tests.unit.DesignUnit import DesignUnitProject
from tests.unit.Domain     import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Indices(DesignUnitProject):
	def test_Pages(self) -> None:
		body = ".. vhdl:entity:: Counter\n\n.. vhdl:package:: Utilities\n\n:ref:`vhdl-entities` :ref:`vhdl-subprograms`\n"
		self._page(body)

		self.assertEqual([], self._warningLines())
		for name, text in (
			("vhdl-entities",    "Counter"),
			("vhdl-packages",    "Utilities"),
			("vhdl-subprograms", "to_index(unsigned, positive, positive)"),
			("vhdl-types",       "T_SMALL"),
		):
			with self.subTest(index=name):
				self.assertIn(text, self._html(name))

		html = self._html("page")
		self.assertIn('href="vhdl-entities.html"', html)
		self.assertIn('href="vhdl-subprograms.html"', html)

	def test_Entries(self) -> None:
		domain = self._page(".. vhdl:entity:: Counter\n\n.. vhdl:package:: Utilities\n")

		content, collapse = SubprogramIndex(domain).generate()

		self.assertFalse(collapse)
		extra = "function in lib_A.Utilities"
		anchor = "vhdl-function-demo.lib_a.utilities"
		self.assertEqual(
			[
				("R", [
					IndexEntry("random()", 0, "page", f"{anchor}.random", extra, "", ""),
					IndexEntry(
						"reset(natural)", 0, "page", "vhdl-procedure-demo.lib_a.utilities.reset-natural",
						"procedure in lib_A.Utilities", "", ""
					),
				]),
				("T", [
					IndexEntry("to_index(natural)", 0, "page", f"{anchor}.to_index-natural", extra, "", ""),
					IndexEntry(
						"to_index(unsigned, positive, positive)", 0, "page", f"{anchor}.to_index-unsigned-positive-positive",
						extra, "", ""
					),
				]),
			],
			content
		)

	def test_Types(self) -> None:
		domain = self._page(".. vhdl:package:: Utilities\n")

		content, _ = TypeIndex(domain).generate()

		self.assertEqual(
			[("T", ["subtype in lib_A.Utilities", "type in lib_A.Utilities"])],
			[(letter, [entry.extra for entry in entries]) for letter, entries in content]
		)

	def test_DocNames(self) -> None:
		"""Only the objects of the given documents are listed."""
		domain = self._page(".. vhdl:entity:: Counter\n")

		self.assertEqual(1, len(EntityIndex(domain).generate(["page"])[0]))
		self.assertEqual([], EntityIndex(domain).generate(["other"])[0])
		self.assertEqual([], PackageIndex(domain).generate()[0])


class SeveralDesigns(Project):
	"""With several designs described, an entry's extra information starts with the design."""

	def test_Design(self) -> None:
		page = dedent("""\
			Page
			####

			.. vhdl:entity:: lib_A.Counter
			   :design: Demo

			.. vhdl:entity:: lib_A.Counter
			   :design: Other
			""")
		app = self._build({"page": page})

		self.assertEqual([], self._warningLines())
		content, _ = EntityIndex(app.env.get_domain("vhdl")).generate()
		self.assertEqual(
			[("C", ["entity in Demo.lib_A", "entity in Other.lib_A"])],
			[(letter, [entry.extra for entry in entries]) for letter, entries in content]
		)
