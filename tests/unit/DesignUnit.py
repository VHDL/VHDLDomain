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
from typing            import Any, ClassVar, Optional as Nullable

from sphinx.errors     import ConfigError

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
	from pyVHDLModel.DesignUnit    import Architecture, Component, Configuration, Context, Entity, LibraryClause, Package
	from pyVHDLModel.Expression    import FunctionCall, IntegerLiteral, PhysicalIntegerLiteral
	from pyVHDLModel.Interface     import GenericConstantInterfaceItem, GenericFunctionInterfaceItem
	from pyVHDLModel.Interface     import GenericTypeInterfaceItem, ParameterConstantInterfaceItem
	from pyVHDLModel.Interface     import ParameterVariableInterfaceItem, PortSimpleSignalInterfaceItem
	from pyVHDLModel.Name          import SimpleName
	from pyVHDLModel.Object        import Constant, DeferredConstant, SharedVariable, Signal
	from pyVHDLModel.Subprogram    import Function, Procedure
	from pyVHDLModel.Symbol        import ConstrainedArraySubtypeSymbol, EntitySymbol, LibraryReferenceSymbol
	from pyVHDLModel.Symbol        import PossibleReference, SimpleSubtypeSymbol, Symbol
	from pyVHDLModel.Type          import EnumeratedType, EnumerationLiteral, PhysicalType, PhysicalUnit, ProtectedType
	from pyVHDLModel.Type          import RecordType, RecordTypeElement, Subtype

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
					FunctionCall(),
					documentation="-- The value.\\n--\\n-- Second paragraph."
				),
			]
		))
		document._AddDesignUnit(Entity("Adder"))
		document._AddDesignUnit(Architecture("rtl", EntitySymbol(SimpleName("Counter")), documentation="-- The RTL model."))
		document._AddDesignUnit(Architecture("sim", EntitySymbol(SimpleName("Counter")), documentation="-- A model."))
		document._AddDesignUnit(Architecture("rtl", EntitySymbol(SimpleName("Adder")), documentation="-- The adder."))
		document._AddDesignUnit(Package(
			"Utilities",
			genericItems=[GenericConstantInterfaceItem(("SIZE", ), Mode.In, subtype("positive"))],
			declaredItems=[
				EnumeratedType("T_STATE", [EnumerationLiteral("Idle"), EnumerationLiteral("Run")], documentation="-- States."),
				Subtype("T_SMALL", subtype("natural")),
				Constant(("C_ONE", "C_UNO"), subtype("natural"), IntegerLiteral(1), documentation="-- One."),
				DeferredConstant(("C_LATE", ), subtype("boolean"), documentation="-- Set by the body."),
				Function("to_index", subtype("natural"), parameterItems=[
					ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("natural"))
				]),
				Function("to_index", subtype("natural"), parameterItems=[
					ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("unsigned")),
					ParameterConstantInterfaceItem(("low", "high"), Mode.In, subtype("positive"))
				]),
				Function("random", subtype("T_SMALL"), isPure=False),
				Procedure("reset", parameterItems=[ParameterConstantInterfaceItem(("value", ), Mode.In, subtype("natural"))]),
				RecordType(
					"T_PAIR",
					[RecordTypeElement(("Low", "High"), subtype("natural"), documentation="-- The bounds.")],
					documentation="-- A pair."
				),
				PhysicalType(
					"T_FREQ", SimpleRange(IntegerLiteral(0), IntegerLiteral(1000), Direction.To), PhysicalUnit("Hz"),
					[PhysicalUnit("kHz", PhysicalIntegerLiteral(1000, "Hz"), documentation="-- Kilohertz.")]
				),
				Signal(("S_READY", ), subtype("std_logic"), IntegerLiteral(0), documentation="-- Ready."),
				Signal(("S_STATE", ), subtype("T_STATE")),
				SharedVariable(("V_COUNT", ), subtype("natural")),
				Component(
					"Adder",
					genericItems=[GenericConstantInterfaceItem(("WIDTH", ), Mode.In, subtype("positive"))],
					portItems=[
						PortSimpleSignalInterfaceItem(("A", "B"), Mode.In, subtype("std_logic"), documentation="-- Summands."),
						PortSimpleSignalInterfaceItem(("Sum", ), Mode.Out, subtype("std_logic")),
					],
					documentation="-- An adder."
				),
				Function("clip", subtype("natural"), parameterItems=[
					ParameterConstantInterfaceItem(
						("value", ), Mode.Default, subtype("natural"), IntegerLiteral(0), documentation="-- The value."
					)
				]),
				Procedure(
					"swap",
					genericItems=[GenericTypeInterfaceItem("T_VALUE", documentation="-- The values' type.")],
					parameterItems=[ParameterVariableInterfaceItem(("A", "B"), Mode.InOut, subtype("T_VALUE"))],
					documentation="-- Swap two values."
				),
				Function(
					"maximum", subtype("T_VALUE"),
					genericItems=[
						GenericTypeInterfaceItem("T_VALUE"), GenericFunctionInterfaceItem("<", subtype("boolean"))
					],
					parameterItems=[ParameterConstantInterfaceItem(("L", "R"), Mode.Default, subtype("T_VALUE"))]
				),
				ProtectedType(
					"T_COUNTER",
					[
						Procedure(
							"Increment",
							parameterItems=[ParameterConstantInterfaceItem(("Count", ), Mode.Default, subtype("positive"))],
							documentation="-- Add to the counter."
						),
						Function("Value", subtype("natural"), isPure=False, documentation="-- The counter's value."),
					],
					documentation="-- A counter."
				),
			],
			documentation="-- Utilities."
		))
		document._AddDesignUnit(Package("Second", declaredItems=[EnumeratedType("T_STATE", [EnumerationLiteral("Off")])]))
		document._AddDesignUnit(Context("ctx", [LibraryClause([LibraryReferenceSymbol(SimpleName("IEEE"))])]))
		document._AddDesignUnit(Configuration(
			"cfg",
			EntitySymbol(SimpleName("Counter")),
			BlockConfiguration(Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label))
		))
		design.AddDocument(document, design.GetLibrary("lib_A"))
		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.IndexPackages()
		design.LinkComponents()

		return design


	def addDesigns(app):
		app.env.get_domain("vhdl").AddDesign("Demo", demo())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")


class DesignUnitProject(Project):
	"""A project with design ``Demo``, every page starting in its library ``lib_A``."""

	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	def _page(self, body: str, pages: Nullable[dict[str, str]] = None, **config: Any) -> VHDLDomain:
		"""
		Build a page placing the body after ``vhdl:design`` and ``vhdl:library``, and further pages as given.

		:param body:   The page's body.
		:param pages:  Optional, further pages by name. Default: ``None``, none.
		:param config: Configuration values overriding the defaults.
		:returns:      The domain after the build.
		"""
		page = f"Page\n####\n\n.. vhdl:design:: Demo\n   :no-index:\n\n.. vhdl:library:: lib_A\n   :no-index:\n\n{body}"
		app =  self._build({"page": page, **({} if pages is None else pages)}, **config)

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
				("architecture", "demo.lib_a.counter.sim"),
			},
			set(domain.Objects)
		)

	def test_Description(self) -> None:
		self._page(".. vhdl:entity:: Counter\n\n   Written by hand.\n")

		html = self._html("page")
		for text in (
			"<p>A counter.</p>", "<p>Second paragraph.</p>", "<p>Written by hand.</p>", "<p>The RTL model.</p>",
			'<span class="sig-name descname"><span class="pre">rtl</span></span>'
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_InterfaceFields(self) -> None:
		"""Generics and ports are fields as Python's parameters: name, declaration, default value and documentation."""
		self._page(".. vhdl:entity:: Counter\n")

		html = self._html("page")
		for text in (
			'<dt class="field-odd">Generics<span class="colon">:</span></dt>',
			'<li><p id="vhdl-generic-demo.lib_a.counter.modulo"><strong>MODULO</strong> : <em>positive</em> – Modulo value.'
			'</p></li>',
			'<li><p id="vhdl-generic-demo.lib_a.counter.bits"><span id="vhdl-generic-demo.lib_a.counter.width"></span>'
			'<strong>BITS, WIDTH</strong> : <em>natural</em> := <em>8</em></p></li>',
			'<li><p id="vhdl-generic-demo.lib_a.counter.t_data"><strong>T_DATA</strong> : <em>type</em></p></li>',
			'<dt class="field-even">Ports<span class="colon">:</span></dt>',
			'<li><p id="vhdl-port-demo.lib_a.counter.clock"><strong>Clock</strong> : <em>in std_logic</em> – <em>Clock</em> '
			'input.</p></li>',
			'<li><p id="vhdl-port-demo.lib_a.counter.q0"><span id="vhdl-port-demo.lib_a.counter.q1"></span>'
			'<strong>Q0, Q1</strong> : <em>out std_logic</em></p></li>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_InterfaceField_SingleItem(self) -> None:
		"""A field of one item is a paragraph; its documentation's first paragraph follows the declaration."""
		self._page(".. vhdl:entity:: Wide\n")

		self.assertIn(
			'<dd class="field-odd"><p id="vhdl-port-demo.lib_a.wide.value"><strong>Value</strong> : '
			'<em>out unsigned(7 downto 0)</em> := <em>...</em> – The value.</p>\n<p>Second paragraph.</p>\n</dd>',
			self._html("page")
		)

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

	def test_Architectures(self) -> None:
		"""By default, every entity lists its architectures with their documentation."""
		domain = self._page(".. vhdl:entity:: Counter\n\n.. vhdl:entity:: Adder\n")

		html = self._html("page")
		self.assertEqual(2, html.count('<p class="rubric">Architectures</p>'))
		for text in ("<p>The RTL model.</p>", "<p>A model.</p>", "<p>The adder.</p>"):
			with self.subTest(text=text):
				self.assertIn(text, html)

		self.assertIn(("architecture", "demo.lib_a.adder.rtl"), domain.Objects)

	def test_Architectures_Multiple(self) -> None:
		"""With ``multiple``, only an entity with more than one architecture lists them."""
		domain = self._page(".. vhdl:entity:: Counter\n\n.. vhdl:entity:: Adder\n", vhdl_architectures="multiple")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertEqual(1, html.count('<p class="rubric">Architectures</p>'))
		self.assertIn("<p>A model.</p>", html)
		self.assertNotIn("<p>The adder.</p>", html)
		self.assertNotIn(("architecture", "demo.lib_a.adder.rtl"), domain.Objects)

	def test_Architectures_Option(self) -> None:
		"""The options override the configuration values; hidden descriptions keep the architectures' signatures."""
		body = dedent("""\
			.. vhdl:entity:: Counter
			   :architectures: never

			.. vhdl:entity:: Adder
			   :architectures: always
			   :architecture-descriptions: show
			""")
		domain = self._page(body, vhdl_architectures="multiple", vhdl_architecture_descriptions="hide")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertEqual(1, html.count('<p class="rubric">Architectures</p>'))
		self.assertNotIn(("architecture", "demo.lib_a.counter.rtl"), domain.Objects)
		self.assertIn("<p>The adder.</p>", html)

		self._page(".. vhdl:entity:: Counter\n", vhdl_architecture_descriptions="hide")

		html = self._html("page")
		self.assertIn('id="vhdl-architecture-demo.lib_a.counter.sim"', html)
		self.assertNotIn("<p>A model.</p>", html)

	def test_Architectures_Invalid(self) -> None:
		self._page(".. vhdl:entity:: Counter\n   :architectures: some\n")

		self.assertEqual(
			[
				"/src/page.rst:10: ERROR: Error in \"vhdl:entity\" directive:",
				"invalid option value: (option: \"architectures\"; value: 'some')",
				"'some' is not a valid ArchitectureListing..",
				"",
				".. vhdl:entity:: Counter",
				"   :architectures: some [docutils]",
			],
			self._warningLines()[:6]
		)

	def test_Architectures_InvalidConfiguration(self) -> None:
		with self.assertRaises(ConfigError) as context:
			self._page(".. vhdl:entity:: Counter\n", vhdl_architectures="some")

		self.assertEqual("conf.py: vhdl_architectures: 'some' is not a listing of architectures.", str(context.exception))
		self.assertEqual(["Allowed values: always, multiple, never."], context.exception.__notes__)

	def test_ArchitectureDescriptions_InvalidConfiguration(self) -> None:
		with self.assertRaises(ConfigError) as context:
			self._page(".. vhdl:entity:: Counter\n", vhdl_architecture_descriptions="full")

		self.assertEqual(
			"conf.py: vhdl_architecture_descriptions: 'full' is not a choice of architecture descriptions.",
			str(context.exception)
		)
		self.assertEqual(["Allowed values: show, hide."], context.exception.__notes__)

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
		self.assertIn("<em>out unsigned(7 downto 0)</em> := <em>...</em>", self._html("page"))


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
				("generic",   "demo.lib_a.utilities.size"),
				("type",      "demo.lib_a.utilities.t_state"),
				("subtype",   "demo.lib_a.utilities.t_small"),
				("constant",  "demo.lib_a.utilities.c_one"),
				("constant",  "demo.lib_a.utilities.c_uno"),
				("constant",  "demo.lib_a.utilities.c_late"),
				("function",  "demo.lib_a.utilities.to_index(natural)"),
				("function",  "demo.lib_a.utilities.to_index(unsigned,positive,positive)"),
				("function",  "demo.lib_a.utilities.random()"),
				("procedure", "demo.lib_a.utilities.reset(natural)"),
				("type",      "demo.lib_a.utilities.t_pair"),
				("type",      "demo.lib_a.utilities.t_freq"),
				("signal",    "demo.lib_a.utilities.s_ready"),
				("signal",    "demo.lib_a.utilities.s_state"),
				("variable",  "demo.lib_a.utilities.v_count"),
				("component", "demo.lib_a.utilities.adder"),
				("function",  "demo.lib_a.utilities.clip(natural)"),
				("procedure", "demo.lib_a.utilities.swap(t_value,t_value)"),
				("function",  "demo.lib_a.utilities.maximum(t_value,t_value)"),
				("type",      "demo.lib_a.utilities.t_counter"),
				("procedure", "demo.lib_a.utilities.t_counter.increment(positive)"),
				("function",  "demo.lib_a.utilities.t_counter.value()"),
			},
			set(domain.Objects)
		)

	def test_Description(self) -> None:
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			"<p>Utilities.</p>", "<p>States.</p>", "<p>One.</p>",
			'<span class="pre">impure</span>', '<span class="pre">low</span>',
			'<p id="vhdl-generic-demo.lib_a.utilities.size"><strong>SIZE</strong> : <em>positive</em></p>'
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Types(self) -> None:
		"""A signature shows a type's definition as pyVHDLModel writes it; a record has elements, a physical type units."""
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			'<span class="property"> <span class="pre">is</span> <span class="pre">(Idle,</span> '
			'<span class="pre">Run)</span></span>',
			'<span class="property"> <span class="pre">is</span> <span class="pre">natural</span></span>',
			'<span class="property"> <span class="pre">is</span> <span class="pre">record</span></span>',
			'<dt class="field-odd">Elements<span class="colon">:</span></dt>\n'
			'<dd class="field-odd"><p><strong>Low, High</strong> : <em>natural</em> – The bounds.</p>',
			'<span class="property"> <span class="pre">is</span> <span class="pre">range</span> <span class="pre">0</span> '
			'<span class="pre">to</span> <span class="pre">1000</span></span>',
			'<li><p><strong>Hz</strong></p></li>\n<li><p><strong>kHz</strong> = <em>1000 Hz</em> – Kilohertz.</p></li>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Objects_Values(self) -> None:
		"""A constant shows its value, a signal its default value; a shared variable has the keywords of both words."""
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			'<span class="sig-name descname"><span class="pre">C_ONE</span></span><span class="property"> <span class="pre">:'
			'</span> <span class="pre">natural</span> <span class="pre">:=</span> <span class="pre">1</span></span>',
			'<span class="sig-name descname"><span class="pre">S_READY</span></span><span class="property"> '
			'<span class="pre">:</span> <span class="pre">std_logic</span> <span class="pre">:=</span> '
			'<span class="pre">0</span></span>',
			'<span class="pre">shared</span></span><span class="w"> </span></span><span class="property"><span class="k">'
			'<span class="pre">variable</span>',
			"<p>Ready.</p>",
			'<span class="pre">deferred</span></span><span class="w"> </span></span><span class="property"><span class="k">'
			'<span class="pre">constant</span></span><span class="w"> </span></span><span class="sig-name descname">'
			'<span class="pre">C_LATE</span></span><span class="property"> <span class="pre">:</span> '
			'<span class="pre">boolean</span></span>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Component(self) -> None:
		"""A component has the fields of an entity; its generics and ports are no objects, an entity's port is."""
		self._page(".. vhdl:package:: Utilities\n\n.. vhdl:entity:: Adder\n\n:vhdl:comp:`Adder` :vhdl:sig:`S_READY`\n")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for text in (
			"<p>An adder.</p>",
			'<dt class="field-odd">Entity<span class="colon">:</span></dt>\n<dd class="field-odd"><p>'
			'<a class="reference internal" href="#vhdl-entity-demo.lib_a.adder" title="Demo.lib_A.Adder">'
			'<code class="docutils literal notranslate"><span class="pre">Adder</span></code></a></p>\n</dd>',
			'<dd class="field-even"><p><strong>WIDTH</strong> : <em>positive</em></p>',
			'<li><p><strong>A, B</strong> : <em>in std_logic</em> – Summands.</p></li>',
			'href="#vhdl-component-demo.lib_a.utilities.adder"', 'href="#vhdl-signal-demo.lib_a.utilities.s_ready"',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Parameters(self) -> None:
		"""A parameter shows its default value; a documented parameter gives the subprogram the field *Parameters*."""
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			'<em class="sig-param"><span class="pre">value</span> <span class="pre">:</span> '
			'<span class="pre">natural</span> <span class="pre">:=</span> <span class="pre">0</span></em>',
			'<dt class="field-odd">Parameters<span class="colon">:</span></dt>\n'
			'<dd class="field-odd"><p><strong>value</strong> : <em>natural</em> := <em>0</em> – The value.</p>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

		self.assertEqual(1, html.count("Parameters<span"))

	def test_Generics(self) -> None:
		"""A generic subprogram's generics are type parameters of the signature and the field *Generics*."""
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			'<span class="sig-name descname"><span class="pre">swap</span></span><span class="sig-paren">[</span>'
			'<em class="sig-param"><span class="pre">T_VALUE</span></em><span class="sig-paren">]</span>'
			'<span class="sig-paren">(</span><em class="sig-param"><span class="pre">A</span> <span class="pre">:</span> '
			'<span class="pre">inout</span> <span class="pre">T_VALUE</span></em>',
			'<p>Swap two values.</p>\n<dl class="vhdl-interface vhdl-list field-list simple">\n'
			'<dt class="field-odd">Generics<span class="colon">:</span></dt>\n'
			'<dd class="field-odd"><p><strong>T_VALUE</strong> : <em>type</em> – The values’ type.</p>\n</dd>\n</dl>',
			'<em class="sig-param"><span class="pre">T_VALUE</span></em>, <em class="sig-param">'
			'<span class="pre">&quot;&lt;&quot;</span></em><span class="sig-paren">]</span>',
			'<li><p><strong>&quot;&lt;&quot;</strong> : <em>function</em></p></li>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Component_Undocumented(self) -> None:
		"""A component's entity without a description is its name, without a warning."""
		self._page(".. vhdl:package:: Utilities\n")

		self.assertEqual([], self._warningLines())
		self.assertIn(
			'<dd class="field-odd"><p><code class="docutils literal notranslate"><span class="pre">Adder</span></code></p>',
			self._html("page")
		)

	def test_ProtectedType(self) -> None:
		"""A protected type's methods are descriptions in the type's description, as a Python class' methods."""
		self._page(".. vhdl:package:: Utilities\n\n:vhdl:proc:`T_COUNTER.Increment` :vhdl:func:`Value`\n")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for text in (
			'<span class="sig-name descname"><span class="pre">T_COUNTER</span></span><span class="property"> '
			'<span class="pre">is</span> <span class="pre">protected</span></span>',
			'<dd><p>A counter.</p>\n<dl class="vhdl procedure vhdl-method">\n<dt class="sig sig-object vhdl" '
			'id="vhdl-procedure-demo.lib_a.utilities.t_counter.increment-positive">',
			"<p>Add to the counter.</p>", "<p>The counter’s value.</p>",
			'href="#vhdl-procedure-demo.lib_a.utilities.t_counter.increment-positive"',
			'href="#vhdl-function-demo.lib_a.utilities.t_counter.value"',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_Classes(self) -> None:
		"""A description has the classes ``vhdl``, its object type, and a ``vhdl-<variant>`` per variant."""
		self._page(".. vhdl:package:: Utilities\n")

		html = self._html("page")
		for text in (
			'<dl class="vhdl package">', '<dl class="vhdl type vhdl-enumeration">', '<dl class="vhdl type vhdl-record">',
			'<dl class="vhdl type vhdl-physical">', '<dl class="vhdl type vhdl-protected">', '<dl class="vhdl subtype">',
			'<dl class="vhdl constant">', '<dl class="vhdl constant vhdl-deferred">', '<dl class="vhdl function">',
			'<dl class="vhdl function vhdl-impure">', '<dl class="vhdl procedure vhdl-generic">',
			'<dl class="vhdl function vhdl-generic">', '<dl class="vhdl procedure vhdl-method">',
			'<dl class="vhdl function vhdl-method vhdl-impure">', '<dl class="vhdl component">',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_TypeReferences(self) -> None:
		"""A type mark refers to the type's description; an undescribed type's stays text, without a warning."""
		self._page(".. vhdl:package:: Utilities\n", vhdl_reference_popups=False)

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		for text in (
			'<span class="pre">S_STATE</span></span><span class="property"> <span class="pre">:</span> '
			'<a class="reference internal" href="#vhdl-type-demo.lib_a.utilities.t_state" '
			'title="type T_STATE is (Idle, Run)"><span class="pre">T_STATE</span></a></span>',
			'<span class="pre">S_READY</span></span><span class="property"> <span class="pre">:</span> '
			'<span class="pre">std_logic</span>',
			'<span class="sig-return-typehint"><a class="reference internal" '
			'href="#vhdl-subtype-demo.lib_a.utilities.t_small" title="subtype T_SMALL is natural">'
			'<span class="pre">T_SMALL</span></a></span>',
		):
			with self.subTest(text=text):
				self.assertIn(text, html)

	def test_TypeReferences_Ambiguous(self) -> None:
		"""A type mark naming several described types stays text, without a warning; a role warns."""
		self._page(".. vhdl:package:: Utilities\n\n.. vhdl:package:: Second\n\n:vhdl:type:`T_STATE`\n")

		self.assertEqual(
			[
				"/src/page.rst:14: WARNING: VHDL type 'T_STATE' is ambiguous, candidates: Demo.lib_A.Second.T_STATE, "
				"Demo.lib_A.Utilities.T_STATE [vhdl.ref]"
			],
			self._warningLines()
		)
		self.assertIn(
			'<span class="pre">S_STATE</span></span><span class="property"> <span class="pre">:</span> '
			'<span class="pre">T_STATE</span></span>',
			self._html("page")
		)

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


class Style(DesignUnitProject):
	def test_Default(self) -> None:
		"""By default, the domain chooses the style: the interface lists are fields with the class ``vhdl-list``."""
		self._page(".. vhdl:entity:: Counter\n\n.. vhdl:package:: Utilities\n")

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIn('<dl class="vhdl-interface vhdl-list field-list simple">', html)
		self.assertNotIn('<dl class="vhdl-interface field-list simple">', html)

	def test_Table(self) -> None:
		"""Style ``table`` isn't supported yet: it is warned about, once per unit, and written as ``list``."""
		self._page(".. vhdl:entity:: Counter\n   :style: table\n\n.. vhdl:package:: Utilities\n   :style: list\n")

		self.assertEqual(
			["/src/page.rst:10: WARNING: vhdl:entity: Style 'table' isn't supported yet, written as 'list'. [vhdl.style]"],
			self._warningLines()
		)
		self.assertIn('<dl class="vhdl-interface vhdl-list field-list simple">', self._html("page"))

	def test_Configuration(self) -> None:
		"""``vhdl_style`` is the default of the option; a unit without interface lists isn't warned about."""
		self._page(
			".. vhdl:entity:: Counter\n\n.. vhdl:entity:: Adder\n   :style: auto\n\n.. vhdl:context:: ctx\n",
			vhdl_style="table"
		)

		self.assertEqual(
			["/src/page.rst:10: WARNING: vhdl:entity: Style 'table' isn't supported yet, written as 'list'. [vhdl.style]"],
			self._warningLines()
		)

	def test_Invalid(self) -> None:
		self._page(".. vhdl:entity:: Counter\n   :style: grid\n")

		self.assertEqual(
			[
				"/src/page.rst:10: ERROR: Error in \"vhdl:entity\" directive:",
				"invalid option value: (option: \"style\"; value: 'grid')",
				"'grid' is not a valid InterfaceStyle..",
			],
			self._warningLines()[:3]
		)

	def test_InvalidConfiguration(self) -> None:
		with self.assertRaises(ConfigError) as context:
			self._page(".. vhdl:entity:: Counter\n", vhdl_style="grid")

		self.assertEqual("conf.py: vhdl_style: 'grid' is not a style of interface lists.", str(context.exception))
		self.assertEqual(["Allowed values: auto, list, table."], context.exception.__notes__)
