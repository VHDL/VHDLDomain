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
Unit tests for the design-unit directives of the Sphinx domain ``vhdl``: ``vhdl:entity``, ``vhdl:package``,
``vhdl:context`` and ``vhdl:configuration``.
"""
from textwrap          import dedent
from typing            import ClassVar

from VHDLDomain        import VHDLDomain

from tests.unit.Domain import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: A :file:`conf.py` adding design ``Demo``: library ``lib_A`` with an entity, its architecture, a package, a context
#: and a configuration.
CONF = dedent("""\
	from pathlib                   import Path

	from pyVHDLModel               import Design, Document
	from pyVHDLModel.Base          import Direction, Mode, SimpleRange
	from pyVHDLModel.Configuration import BlockConfiguration
	from pyVHDLModel.DesignUnit    import Architecture, Configuration, Context, Entity, LibraryClause, Package
	from pyVHDLModel.Expression    import FunctionCall, IntegerLiteral
	from pyVHDLModel.Interface     import GenericConstantInterfaceItem, GenericTypeInterfaceItem
	from pyVHDLModel.Interface     import ParameterConstantInterfaceItem, PortSimpleSignalInterfaceItem
	from pyVHDLModel.Name          import SimpleName
	from pyVHDLModel.Object        import Constant
	from pyVHDLModel.Subprogram    import Function, Procedure
	from pyVHDLModel.Symbol        import ConstrainedArraySubtypeSymbol, EntitySymbol, LibraryReferenceSymbol
	from pyVHDLModel.Symbol        import PossibleReference, SimpleSubtypeSymbol, Symbol
	from pyVHDLModel.Type          import EnumeratedType, EnumerationLiteral, Subtype

	extensions = ["VHDLDomain"]


	def subtype(name):
		return SimpleSubtypeSymbol(SimpleName(name))


	def demo():
		design = Design("Demo")
		document = Document(Path("a.vhdl"))
		document._AddDesignUnit(Entity(
			"Counter",
			genericItems=[
				GenericConstantInterfaceItem(("MODULO", ), Mode.In, subtype("positive"), documentation="-- Modulo value."),
				GenericConstantInterfaceItem(("BITS", "WIDTH"), Mode.In, subtype("natural"), IntegerLiteral(8)),
				GenericTypeInterfaceItem("T_DATA"),
			],
			portItems=[
				PortSimpleSignalInterfaceItem(("Clock", ), Mode.In, subtype("std_logic"), documentation="-- *Clock* input."),
				PortSimpleSignalInterfaceItem(("Q0", "Q1"), Mode.Out, subtype("std_logic")),
			],
			documentation="-- A counter.\\n--\\n-- Second paragraph."
		))
		document._AddDesignUnit(Entity(
			"Wide",
			portItems=[
				PortSimpleSignalInterfaceItem(
					("Value", ), Mode.Out,
					ConstrainedArraySubtypeSymbol(
						SimpleName("unsigned"), [SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)]
					),
					FunctionCall()
				),
			]
		))
		document._AddDesignUnit(Architecture("rtl", EntitySymbol(SimpleName("Counter")), documentation="-- The RTL model."))
		document._AddDesignUnit(Package(
			"Utilities",
			declaredItems=[
				EnumeratedType("T_STATE", [EnumerationLiteral("Idle"), EnumerationLiteral("Run")], documentation="-- States."),
				Subtype("T_SMALL", subtype("natural")),
				Constant(("C_ONE", "C_UNO"), subtype("natural"), IntegerLiteral(1), documentation="-- One."),
				Function("to_index", subtype("natural"), parameterItems=[
					ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("natural"))
				]),
				Function("to_index", subtype("natural"), parameterItems=[
					ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("unsigned")),
					ParameterConstantInterfaceItem(("low", "high"), Mode.In, subtype("positive"))
				]),
				Function("random", subtype("natural"), isPure=False),
				Procedure("reset", parameterItems=[ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("natural"))]),
			],
			documentation="-- Utilities."
		))
		document._AddDesignUnit(Context("ctx", [LibraryClause([LibraryReferenceSymbol(SimpleName("IEEE"))])]))
		document._AddDesignUnit(Configuration(
			"cfg",
			EntitySymbol(SimpleName("Counter")),
			BlockConfiguration(Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label))
		))
		design.AddDocument(document, design.GetLibrary("lib_A"))
		design.CreateDependencyGraph()
		design.LinkArchitectures()

		return design


	def addDesigns(app):
		app.env.get_domain("vhdl").AddDesign("Demo", demo())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")


class DesignUnitProject(Project):
	"""A project with design ``Demo``, every page starting in its library ``lib_A``."""

	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	def _page(self, body: str, **pages: str) -> VHDLDomain:
		"""
		Build a page placing the body after ``vhdl:design`` and ``vhdl:library``, and further pages as given.

		:param body:  The page's body.
		:param pages: Further pages by name.
		:returns:     The domain after the build.
		"""
		page = f"Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n.. vhdl:library:: lib_A\n   :no-index:\n\n{body}"
		app = self._build({"page": page, **pages})

		return app.env.get_domain("vhdl")


class Entity(DesignUnitProject):
	def test_Objects(self) -> None:
		domain = self._page(".. vhdl:entity:: Counter\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			{
				("entity",       "demo.lib_a.counter"),
				("generic",      "demo.lib_a.counter.modulo"),
				("generic",      "demo.lib_a.counter.bits"),
				("generic",      "demo.lib_a.counter.width"),
				("generic",      "demo.lib_a.counter.t_data"),
				("port",         "demo.lib_a.counter.clock"),
				("port",         "demo.lib_a.counter.q0"),
				("port",         "demo.lib_a.counter.q1"),
				("architecture", "demo.lib_a.counter.rtl"),
			},
			set(domain.Objects)
		)

	def test_Description(self) -> None:
		self._page(".. vhdl:entity:: Counter\n\n   Written by hand.\n")

		html = self._html("page")
		for text in (
			"<p>A counter.</p>", "<p>Second paragraph.</p>", "<p>Written by hand.</p>", "<em>Clock</em> input.",
			'<span class="pre">positive</span>', '<span class="pre">8</span>', '<span class="pre">type</span>',
			'<span class="pre">BITS,</span>', '<span class="pre">in</span>', "<p>The RTL model.</p>",
			'<span class="sig-name descname"><span class="pre">rtl</span></span>'
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_References(self) -> None:
		self._page(".. vhdl:entity:: Counter\n\n:vhdl:port:`Counter.Clock` :vhdl:generic:`WIDTH` :vhdl:arch:`rtl`\n")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for anchor in (
			"vhdl-port-demo.lib_a.counter.clock", "vhdl-generic-demo.lib_a.counter.width",
			"vhdl-architecture-demo.lib_a.counter.rtl"
		):
			with self.subTest(anchor=anchor):
				self.assertIn(f'id="{anchor}"', html)
				self.assertIn(f'href="#{anchor}"', html)

	def test_QualifiedArgument(self) -> None:
		app = self._build({"page": "Page\n####\n\n.. vhdl:design:: Demo\n\n.. vhdl:entity:: lib_A.Counter\n"})

		self.assertEqual([], self._warningLines())
		self.assertIn(("entity", "demo.lib_a.counter"), app.env.get_domain("vhdl").Objects)

	def test_NoIndex(self) -> None:
		domain = self._page(".. vhdl:entity:: Counter\n   :no-index:\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual({}, domain.Objects)
		self.assertIn("<p>A counter.</p>", self._html("page"))

	def test_Writer(self) -> None:
		"""What pyVHDLModel writes is written as VHDL; what it can't write yet is written as ``...``, and warned about."""
		self._page(".. vhdl:entity:: Wide\n")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:entity: pyVHDLModel can't write a 'FunctionCall' yet, written as '...'. "
				"[vhdl.writer]"
			],
			self._warningLines()
		)
		html = self._html("page")
		self.assertIn('<span class="pre">unsigned(7</span>', html)
		self.assertIn('<span class="pre">0)</span>', html)


class Errors(DesignUnitProject):
	def test_NoLibrary(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:design:: Demo\n\n.. vhdl:entity:: Counter\n"})

		self.assertEqual(
			[
				"/src/page.rst:6: WARNING: vhdl:entity: No library: name it as '<library>.Counter' or place a 'vhdl:library' "
				"before it. [vhdl.library]"
			],
			self._warningLines()
		)

	def test_UnknownLibrary(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:design:: Demo\n\n.. vhdl:entity:: lib_X.Counter\n"})

		self.assertEqual(
			["/src/page.rst:6: WARNING: vhdl:entity: Library 'lib_X' is not in design 'Demo'. [vhdl.library]"],
			self._warningLines()
		)

	def test_UnknownUnit(self) -> None:
		self._page(".. vhdl:package:: Counter\n")

		self.assertEqual(
			[
				"/src/page.rst:10: WARNING: vhdl:package: Package 'Counter' is not in library 'lib_A' of design 'Demo'. "
				"[vhdl.package]"
			],
			self._warningLines()
		)

	def test_NoDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:entity:: lib_A.Counter\n"})

		self.assertEqual(
			[
				"/src/page.rst:4: WARNING: vhdl:entity: No design: give option ':design:' or place a 'vhdl:design' before it. "
				"[vhdl.design]"
			],
			self._warningLines()
		)


class Package(DesignUnitProject):
	def test_Objects(self) -> None:
		domain = self._page(".. vhdl:package:: Utilities\n")

		self.assertEqual([], self._warningLines())
		self.assertEqual(
			{
				("package",   "demo.lib_a.utilities"),
				("type",      "demo.lib_a.utilities.t_state"),
				("subtype",   "demo.lib_a.utilities.t_small"),
				("constant",  "demo.lib_a.utilities.c_one"),
				("constant",  "demo.lib_a.utilities.c_uno"),
				("function",  "demo.lib_a.utilities.to_index(natural)"),
				("function",  "demo.lib_a.utilities.to_index(unsigned,positive,positive)"),
				("function",  "demo.lib_a.utilities.random()"),
				("procedure", "demo.lib_a.utilities.reset(natural)"),
			},
			set(domain.Objects)
		)

	def test_Description(self) -> None:
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			"<p>Utilities.</p>", "<p>States.</p>", "<p>One.</p>",
			'<span class="pre">impure</span>', '<span class="pre">low</span>'
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_References(self) -> None:
		body = dedent("""\
			.. vhdl:package:: Utilities

			:vhdl:func:`to_index(unsigned, positive, positive)` :vhdl:type:`T_SMALL` :vhdl:const:`C_UNO` :vhdl:proc:`reset`
			""")
		self._page(body)

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for anchor in (
			"vhdl-function-demo.lib_a.utilities.to_index-unsigned-positive-positive",
			"vhdl-subtype-demo.lib_a.utilities.t_small",
			"vhdl-constant-demo.lib_a.utilities.c_uno",
			"vhdl-procedure-demo.lib_a.utilities.reset-natural"
		):
			with self.subTest(anchor=anchor):
				self.assertIn(f'href="#{anchor}"', html)

	def test_Overloads(self) -> None:
		self._page(".. vhdl:package:: Utilities\n\n:vhdl:func:`to_index`\n")

		self.assertEqual(
			[
				"/src/page.rst:12: WARNING: VHDL function 'to_index' is ambiguous, candidates: "
				"Demo.lib_A.Utilities.to_index(natural), Demo.lib_A.Utilities.to_index(unsigned, positive, positive) [vhdl.ref]"
			],
			self._warningLines()
		)


class Context(DesignUnitProject):
	def test_Context(self) -> None:
		domain = self._page(".. vhdl:context:: ctx\n")

		self.assertEqual([], self._warningLines())
		self.assertIn(("context", "demo.lib_a.ctx"), domain.Objects)
		self.assertIn("IEEE", self._html("page"))


class Configuration(DesignUnitProject):
	def test_Configuration(self) -> None:
		domain = self._page(".. vhdl:entity:: Counter\n\n.. vhdl:configuration:: cfg\n")

		self.assertEqual([], self._warningLines())
		self.assertIn(("configuration", "demo.lib_a.cfg"), domain.Objects)
		self.assertIn('href="#vhdl-entity-demo.lib_a.counter"', self._html("page"))
