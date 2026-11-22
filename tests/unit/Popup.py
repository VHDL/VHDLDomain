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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Unit tests for the popups of references of the Sphinx domain ``vhdl``.

The popup a declaration of a package notes in the domain, its HTML, the configuration value ``vhdl_reference_popups``,
and the output of other builders.
"""
from docutils              import nodes
from sphinx                import addnodes

from VHDLDomain.DesignUnit import PackageDirective
from VHDLDomain.Popup      import PopupNode, popupContent

from tests.unit.DesignUnit import DesignUnitProject


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: The page's references to declarations of package ``Utilities``: a record, a physical type, a function, a component,
#: a method of a protected type and a deferred constant.
REFERENCES = (
	":vhdl:type:`T_PAIR` :vhdl:type:`T_FREQ` :vhdl:func:`to_index(natural)` :vhdl:comp:`Adder` "
	":vhdl:proc:`T_COUNTER.Increment` :vhdl:const:`C_LATE`\n"
)


class Popups(DesignUnitProject):
	def test_Domain(self) -> None:
		"""Every declaration of a package has a popup, titled by its signature."""
		domain = self._page(".. vhdl:package:: Utilities\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			{key for key in domain.Objects if key[0] not in ("package", "generic")},
			set(domain.Popups)
		)
		for key, title in (
			(("type",      "demo.lib_a.utilities.t_state"),              "type T_STATE is (Idle, Run)"),
			(("subtype",   "demo.lib_a.utilities.t_small"),              "subtype T_SMALL is natural"),
			(("constant",  "demo.lib_a.utilities.c_late"),               "deferred constant C_LATE : boolean"),
			(("function",  "demo.lib_a.utilities.to_index(natural)"),    "function to_index(value : in natural) -> natural"),
			(("procedure", "demo.lib_a.utilities.t_counter.increment(positive)"), "procedure Increment(Count : positive)"),
			(("component", "demo.lib_a.utilities.adder"),                "component Adder"),
		):
			with self.subTest(key=key):
				self.assertEqual(title, domain.Popups[key][0])
				self.assertIsInstance(domain.Popups[key][1], PopupNode)

	def test_NotePopup(self) -> None:
		"""A popup needs a documented object."""
		domain = self._page(".. vhdl:package:: Utilities\n")

		with self.assertRaises(ValueError) as context:
			domain.NotePopup("type", "Demo.lib_A.Utilities.T_NONE", "type T_NONE", PopupNode())

		self.assertEqual("Parameter 'qualifiedName' names no documented vhdl:type.", str(context.exception))
		self.assertEqual(["Got value 'Demo.lib_A.Utilities.T_NONE'."], context.exception.__notes__)

	def test_TypeMark(self) -> None:
		"""A type mark in a signature is a link with a popup: location, signature, documentation and literals."""
		self._page(".. vhdl:package:: Utilities\n")

		self.assertIn(
			'<span class="pre">:</span> <span class="vhdl-popup-anchor"><a aria-describedby="vhdl-popup-2" '
			'class="reference internal" href="#vhdl-type-demo.lib_a.utilities.t_state"><span class="pre">T_STATE</span></a>'
			'<span class="vhdl-popup no-search" id="vhdl-popup-2" role="tooltip">'
			'<span class="vhdl-popup-location">lib_A.Utilities</span>'
			'<span class="vhdl-popup-signature"><span class="property"><span class="k">type</span><span class="w"> </span>'
			'</span><span class="sig-name descname">T_STATE</span><span class="property"> is (Idle, Run)</span></span>'
			'<span class="vhdl-popup-documentation">States.</span>'
			'<span class="vhdl-popup-members"><span class="vhdl-popup-label">Literals</span>'
			'<span class="vhdl-popup-member">Idle</span><span class="vhdl-popup-member">Run</span></span>'
			'</span></span>',
			self._html("page")
		)

	def test_Roles(self) -> None:
		"""A role's reference has a popup: a record's elements, a physical type's units, a subprogram's signature."""
		self._page(f".. vhdl:package:: Utilities\n\n{REFERENCES}")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for text in (
			'<span class="vhdl-popup-documentation">A pair.</span><span class="vhdl-popup-members">'
			'<span class="vhdl-popup-label">Elements</span><span class="vhdl-popup-member">Low, High : natural</span></span>',
			'<span class="vhdl-popup-label">Units</span><span class="vhdl-popup-member">Hz</span>'
			'<span class="vhdl-popup-member">kHz = 1000 Hz</span>',
			'<span class="sig-name descname">to_index</span>(value : in natural) <span class="sig-return">'
			'<span class="sig-return-icon">&#x2192;</span> <span class="sig-return-typehint">natural</span></span></span>',
			'<span class="sig-name descname">Adder</span></span><span class="vhdl-popup-documentation">An adder.</span>',
			'<span class="vhdl-popup-location">lib_A.Utilities.T_COUNTER</span>',
			'<span class="sig-name descname">C_LATE</span><span class="property"> : boolean</span></span>'
			'<span class="vhdl-popup-documentation">Set by the body.</span>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

		self.assertEqual(html.count('class="vhdl-popup-anchor"'), html.count('role="tooltip"'))
		self.assertEqual(8, html.count('role="tooltip"'))

	def test_Stylesheet(self) -> None:
		"""An HTML page links the stylesheet, which the build holds."""
		self._page(".. vhdl:package:: Utilities\n")

		static = self._path / "build" / "html" / "_static"
		files =  sorted(path.name for path in static.glob("VHDLDomain.*.css"))
		self.assertEqual(1, len(files))
		self.assertIn(f'href="_static/{files[0]}', self._html("page"))
		self.assertIn(".vhdl-popup-anchor:hover > .vhdl-popup", (static / files[0]).read_text(encoding="utf-8"))

	def test_Off(self) -> None:
		"""With ``vhdl_reference_popups = False``, a link is titled by the signature, and no stylesheet is linked."""
		self._page(f".. vhdl:package:: Utilities\n\n{REFERENCES}", vhdl_reference_popups=False)

		html = self._html("page")
		self.assertNotIn("vhdl-popup", html)
		self.assertNotIn("VHDLDomain.", html)
		self.assertIn(
			'<a class="reference internal" href="#vhdl-type-demo.lib_a.utilities.t_pair" title="type T_PAIR is record">',
			html
		)

	def test_NoIndex(self) -> None:
		"""A declaration described with ``:no-index:`` has no popup."""
		domain = self._page(".. vhdl:package:: Utilities\n   :no-index:\n")

		self.assertEqual({}, domain.Popups)

	def test_OtherPage(self) -> None:
		"""A reference on another page - read by another process - has the popup, linking to the description's page."""
		pages = {"refs": f"Refs\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n{REFERENCES}"}
		self._build(
			{
				"page": "Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n.. vhdl:package:: lib_A.Utilities\n",
				**pages
			},
			parallel=2
		)

		self.assertEqual([], self._warningLines())
		html = self._html("refs")
		self.assertEqual(6, html.count('role="tooltip"'))
		self.assertIn('href="page.html#vhdl-type-demo.lib_a.utilities.t_pair"', html)

	def test_LaTeX(self) -> None:
		"""LaTeX writes no popup: the document is the same with and without popups."""
		texts = []
		for popups in (True, False):
			with self.subTest(popups=popups):
				self._page(f".. vhdl:package:: Utilities\n\n{REFERENCES}", builder="latex", vhdl_reference_popups=popups)

				texts.append((self._path / "build" / "latex" / "projectnamenotset.tex").read_text(encoding="utf-8"))

		self.assertEqual(texts[0], texts[1])
		self.assertNotIn("Literals", texts[0])

	def test_Text(self) -> None:
		"""The text builder writes no popup."""
		self._page(f".. vhdl:package:: Utilities\n\n{REFERENCES}", builder="text")

		text = (self._path / "build" / "text" / "page.txt").read_text(encoding="utf-8")
		self.assertTrue(text.endswith('"T_PAIR" "T_FREQ" "to_index(natural)" "Adder" "T_COUNTER.Increment"\n"C_LATE"\n'))
		self.assertNotIn("Literals", text)


class Members(DesignUnitProject):
	def test_Limit(self) -> None:
		"""A popup lists the first 8 members, followed by ``...``."""
		memberList = PackageDirective._PopupMembers("Literals", [f"L{index}" for index in range(10)])

		self.assertEqual(1, len(memberList))
		self.assertEqual(
			["Literals", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "..."],
			[child.astext() for child in memberList[0].children]
		)

	def test_None(self) -> None:
		self.assertEqual([], PackageDirective._PopupMembers("Elements", []))


class Content(DesignUnitProject):
	def test_Markup(self) -> None:
		"""Emphasis, strong and literals keep their markup; a reference becomes its text."""
		reference = addnodes.pending_xref("", nodes.literal("Counter", "Counter"), refdomain="vhdl", reftype="ent")
		paragraph = nodes.paragraph(
			"", "", nodes.Text("A "), nodes.emphasis("BCD", "BCD"), nodes.Text(" digit of "), reference,
			nodes.Text(", "), nodes.strong("", "", nodes.literal("x", "x"))
		)

		content = popupContent(paragraph)

		self.assertEqual("A BCD digit of Counter, x", "".join(node.astext() for node in content))
		self.assertEqual(
			[nodes.Text, nodes.emphasis, nodes.Text, nodes.Text, nodes.Text, nodes.strong],
			[type(node) for node in content]
		)
		self.assertIsInstance(content[5][0], nodes.literal)

	def test_Signature(self) -> None:
		"""A signature keeps its keywords and name; a parameter list becomes its text."""
		parameters = addnodes.desc_parameterlist("", "", addnodes.desc_parameter("A : natural", "A : natural"))
		signature = addnodes.desc_signature(
			"", "", addnodes.desc_annotation("", "", addnodes.desc_sig_keyword("procedure", "procedure")),
			addnodes.desc_name("reset", "reset"), parameters
		)

		content = popupContent(signature)

		self.assertEqual("procedurereset(A : natural)", "".join(node.astext() for node in content))
		self.assertEqual([addnodes.desc_annotation, addnodes.desc_name, nodes.Text], [type(node) for node in content])
		self.assertIsInstance(content[0][0], addnodes.desc_sig_keyword)
