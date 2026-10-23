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
Unit tests for the Sphinx domain ``vhdl``.

Every testcase builds a small Sphinx project in a temporary directory, whose :file:`conf.py` adds designs built by hand
- no frontend needed -, and checks the HTML, the domain's data and the warnings.
"""
from io                  import StringIO
from pathlib             import Path
from tempfile            import TemporaryDirectory
from textwrap            import dedent
from typing              import Any, ClassVar
from unittest.mock       import patch
from warnings            import catch_warnings, filterwarnings

from sphinx.testing.util import SphinxTestApp
from sphinx.util.console import strip_colors

from pyTooling.Testing   import Testcase

from pyVHDLModel         import Design

from VHDLDomain          import VHDLDomain, normalizeName


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


#: A :file:`conf.py` adding two designs: ``Demo`` with libraries ``lib_A`` and ``lib_B``, and ``Other`` with ``lib_A``.
CONF = dedent("""\
	from pathlib                   import Path

	from pyVHDLModel               import Design, Document
	from pyVHDLModel.Configuration import BlockConfiguration
	from pyVHDLModel.DesignUnit    import Configuration, Context, Entity, Package
	from pyVHDLModel.Name          import SimpleName
	from pyVHDLModel.Symbol        import EntitySymbol, PossibleReference, Symbol

	extensions = ["VHDLDomain"]


	def demo():
		design = Design("Demo")

		documentA = Document(Path("a.vhdl"))
		documentA._AddDesignUnit(Entity("Counter"))
		documentA._AddDesignUnit(Package("Utilities"))
		documentA._AddDesignUnit(Configuration(
			"cfg",
			EntitySymbol(SimpleName("Counter")),
			BlockConfiguration(Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label))
		))
		documentA._AddDesignUnit(Context("ctx"))
		design.AddDocument(documentA, design.GetLibrary("lib_A"))

		documentB = Document(Path("b.vhdl"))
		documentB._AddDesignUnit(Entity("Counter"))
		documentB._AddDesignUnit(Entity("Adder"))
		design.AddDocument(documentB, design.GetLibrary("lib_B"))

		return design


	def other():
		design = Design("Other")

		document = Document(Path("c.vhdl"))
		document._AddDesignUnit(Entity("Counter"))
		design.AddDocument(document, design.GetLibrary("lib_A"))

		return design


	def addDesigns(app):
		domain = app.env.get_domain("vhdl")
		domain.AddDesign("Demo", demo())
		domain.AddDesign("Other", other())


	def setup(app):
		app.connect("builder-inited", addDesigns)
""")


class Project(Testcase):
	"""Builds a Sphinx project in a temporary directory, removed after each test."""

	_CONF: ClassVar[str] = CONF  #: The project's :file:`conf.py`.

	_directory: TemporaryDirectory
	_path:      Path
	_warnings:  StringIO

	def setUp(self) -> None:
		self._directory = TemporaryDirectory()
		self._path = Path(self._directory.name)
		(self._path / "src").mkdir()

	def tearDown(self) -> None:
		self._directory.cleanup()

	def _build(self, documents: dict[str, str], parallel: int = 0, **config: Any) -> SphinxTestApp:
		"""
		Write the documents and build the project as HTML.

		:param documents: Content of the documents, by name; ``index`` has a toctree of the others.
		:param parallel:  Optional, number of processes reading the documents. Default: ``0``.
		:param config:    Configuration values overriding the defaults.
		:returns:         The Sphinx application after the build.
		"""
		source = self._path / "src"
		(source / "conf.py").write_text(self._CONF, encoding="utf-8")
		others = "".join(f"   {name}\n" for name in documents if name != "index")
		index = documents.get("index", "Index\n#####\n")
		(source / "index.rst").write_text(f"{index}\n\n.. toctree::\n\n{others}", encoding="utf-8")
		for name, content in documents.items():
			if name != "index":
				(source / f"{name}.rst").write_text(content, encoding="utf-8")

		self._warnings = StringIO()
		app = SphinxTestApp(
			"html", source, self._path / "build", freshenv=True, confoverrides=config, status=StringIO(),
			warning=self._warnings, parallel=parallel
		)
		try:
			with catch_warnings():
				# Sphinx forks its reading processes; in a multi-threaded process, like a pytest-xdist worker, Python warns
				# about fork(), and pytest turns a DeprecationWarning into an error.
				filterwarnings("ignore", r"This process .* is multi-threaded, use of fork\(\)", DeprecationWarning)
				app.build()
		finally:
			app.cleanup()

		return app

	def _html(self, name: str) -> str:
		"""
		Read a built page.

		:param name: Name of the document.
		:returns:    The page's HTML.
		"""
		return (self._path / "build" / "html" / f"{name}.html").read_text(encoding="utf-8")

	def _warningLines(self) -> list[str]:
		"""
		Return the warnings of the last build, without the temporary directory's path.

		:returns: One line per warning.
		"""
		prefixes = sorted({str(self._path), str(self._path.resolve())}, key=len, reverse=True)
		lines = []
		for line in strip_colors(self._warnings.getvalue()).splitlines():
			for prefix in prefixes:
				line = line.replace(prefix, "")
			lines.append(line.replace("\\", "/"))

		return lines


class DesignDirective(Project):
	def test_Design(self) -> None:
		page = "Page\n####\n\n.. vhdl:design:: Demo\n\n   The demo design.\n\nSee :vhdl:design:`Demo`.\n"
		app = self._build({"page": page})

		self.assertEqual([], self._warningLines())
		domain: VHDLDomain = app.env.get_domain("vhdl")
		self.assertEqual(("page", "vhdl-design-demo", "Demo"), domain.Objects[("design", "demo")])
		html = self._html("page")
		self.assertIn("The demo design.", html)
		self.assertIn('href="#vhdl-design-demo"', html)

	def test_UnknownDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:design:: Missing\n"})

		self.assertEqual(
			["/src/page.rst:4: WARNING: vhdl:design: Design 'Missing' was not read. [vhdl.design]"],
			self._warningLines()
		)


class NoIndex(Project):
	def test_NoIndex(self) -> None:
		"""Without target, the design and library are current for the references."""
		page = dedent("""\
			Page
			####

			.. vhdl:design:: Demo
			   :no-index:

			.. vhdl:library:: lib_B
			   :no-index:

			   Not written.
			""")
		app = self._build({"page": page})

		self.assertEqual([], self._warningLines())
		domain: VHDLDomain = app.env.get_domain("vhdl")
		self.assertEqual({}, domain.Objects)
		self.assertNotIn("Not written.", self._html("page"))


class LibraryDirective(Project):
	def test_Library(self) -> None:
		page = dedent("""\
			Page
			####

			.. vhdl:design:: Demo

			.. vhdl:library:: lib_A

			   Library A.

			See :vhdl:lib:`lib_A`.
			""")
		app = self._build({"page": page})

		self.assertEqual([], self._warningLines())
		domain: VHDLDomain = app.env.get_domain("vhdl")
		self.assertEqual(("page", "vhdl-library-demo.lib_a", "Demo.lib_A"), domain.Objects[("library", "demo.lib_a")])
		html = self._html("page")
		self.assertIn("Library A.", html)
		self.assertIn('href="#vhdl-library-demo.lib_a"', html)
		for kind, unit in (("Context", "ctx"), ("Entity", "Counter"), ("Package", "Utilities"), ("Configuration", "cfg")):
			with self.subTest(unit=unit):
				self.assertIn(f"<p>{kind}</p>", html)
				self.assertIn(f'<span class="pre">{unit}</span>', html)

	def test_DesignOption(self) -> None:
		app = self._build({"page": "Page\n####\n\n.. vhdl:library:: lib_A\n   :design: Other\n"})

		self.assertEqual([], self._warningLines())
		domain: VHDLDomain = app.env.get_domain("vhdl")
		self.assertIn(("library", "other.lib_a"), domain.Objects)

	def test_NoDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:library:: lib_A\n"})

		self.assertEqual(
			[
				"/src/page.rst:4: WARNING: vhdl:library: No design: give option ':design:' or place a 'vhdl:design' before it. "
				"[vhdl.design]"
			],
			self._warningLines()
		)

	def test_NotInDesign(self) -> None:
		self._build({"page": "Page\n####\n\n.. vhdl:design:: Demo\n\n.. vhdl:library:: lib_C\n"})

		self.assertEqual(
			["/src/page.rst:6: WARNING: vhdl:library: Library 'lib_C' is not in design 'Demo'. [vhdl.library]"],
			self._warningLines()
		)

	def test_Duplicate(self) -> None:
		page = "Page {0}\n######\n\n.. vhdl:design:: Demo\n{1}\n.. vhdl:library:: lib_A\n"
		self._build({"page1": page.format(1, ""), "page2": page.format(2, "   :no-index:\n")})

		self.assertEqual(
			[
				"/src/page2.rst:7: WARNING: Duplicate description of vhdl:library 'Demo.lib_A', other instance in 'page1'. "
				"[vhdl.duplicate]"
			],
			self._warningLines()
		)


class References(Project):
	def test_Dangling(self) -> None:
		self._build({"page": "Page\n####\n\nSee :vhdl:ent:`Nope`.\n"})

		self.assertEqual(["/src/page.rst:4: WARNING: VHDL entity 'Nope' not found [ref.ent]"], self._warningLines())

	def test_Ambiguous(self) -> None:
		page = dedent("""\
			Page
			####

			.. vhdl:library:: lib_A
			   :design: Demo

			.. vhdl:library:: lib_A
			   :design: Other
			""")
		self._build({"page": page, "refs": "Refs\n####\n\nSee :vhdl:lib:`lib_A`.\n"})

		self.assertEqual(
			["/src/refs.rst:4: WARNING: VHDL library 'lib_A' is ambiguous, candidates: Demo.lib_A, Other.lib_A [vhdl.ref]"],
			self._warningLines()
		)

	def test_CurrentDesign(self) -> None:
		"""An ambiguous name is resolved in the current design."""
		page = dedent("""\
			Page
			####

			.. vhdl:library:: lib_A
			   :design: Demo

			.. vhdl:design:: Other

			.. vhdl:library:: lib_A

			See :vhdl:lib:`lib_A` and :vhdl:lib:`~Demo.lib_A`.
			""")
		self._build({"page": page})

		self.assertEqual([], self._warningLines())
		html = self._html("page")
		self.assertIn('href="#vhdl-library-other.lib_a" title="Other.lib_A"', html)
		self.assertIn('href="#vhdl-library-demo.lib_a" title="Demo.lib_A"', html)

	def test_Parallel(self) -> None:
		"""Objects collected by parallel readers are merged."""
		pages = {
			f"page{index}": f"Page {index}\n######\n\n.. vhdl:library:: lib_{library}\n   :design: Demo\n"
			for index, library in enumerate("AB")
		}
		pages["refs"] = "Refs\n####\n\n:vhdl:lib:`Demo.lib_A`, :vhdl:lib:`Demo.lib_B`\n"
		app = self._build(pages, parallel=2)

		self.assertEqual([], self._warningLines())
		domain: VHDLDomain = app.env.get_domain("vhdl")
		self.assertEqual({("library", "demo.lib_a"), ("library", "demo.lib_b")}, set(domain.Objects))


class FindObjects(Project):
	"""Name matching, on objects entered into the domain's data directly."""

	_domain: VHDLDomain

	def setUp(self) -> None:
		super().setUp()
		app = self._build({})
		self._domain = app.env.get_domain("vhdl")
		for objectType, qualifiedName in (
			("entity",   "Demo.lib_A.Counter"),
			("entity",   "Demo.lib_B.Counter"),
			("entity",   "Other.lib_A.Counter"),
			("function", "Demo.lib_A.Utilities.to_index(natural)"),
			("function", "Demo.lib_A.Utilities.to_index(natural,positive)"),
			("function", "Demo.lib_A.Utilities.resize(ieee.numeric_std.unsigned,natural)"),
		):
			self._domain.Objects[(objectType, normalizeName(qualifiedName))] = ("page", "anchor", qualifiedName)

	def _find(self, objectType: str, target: str, design: str = None, library: str = None) -> list[str]:
		return sorted(name for _, name in self._domain.FindObjects((objectType, ), target, design, library))

	def test_Suffix(self) -> None:
		self.assertEqual(
			["demo.lib_a.counter", "demo.lib_b.counter", "other.lib_a.counter"],
			self._find("entity", "Counter")
		)
		self.assertEqual(["demo.lib_a.counter", "other.lib_a.counter"], self._find("entity", "lib_A.Counter"))
		self.assertEqual(["demo.lib_b.counter"], self._find("entity", "lib_B.Counter"))

	def test_Qualified(self) -> None:
		self.assertEqual(["demo.lib_a.counter"], self._find("entity", "Demo.lib_A.Counter"))

	def test_PartOfName(self) -> None:
		"""A suffix matches at a name's boundary only."""
		self.assertEqual([], self._find("entity", "ounter"))

	def test_CaseInsensitive(self) -> None:
		self.assertEqual(["demo.lib_b.counter"], self._find("entity", "LIB_b.COUNTER"))

	def test_Context(self) -> None:
		self.assertEqual(["demo.lib_a.counter", "demo.lib_b.counter"], self._find("entity", "Counter", "Demo"))
		self.assertEqual(["demo.lib_b.counter"], self._find("entity", "Counter", "Demo", "lib_B"))
		self.assertEqual(["other.lib_a.counter"], self._find("entity", "Counter", "Other", "lib_B"))

	def test_Context_Qualified(self) -> None:
		"""A qualified name isn't narrowed by the current design."""
		self.assertEqual(["demo.lib_a.counter"], self._find("entity", "Demo.lib_A.Counter", "Other"))

	def test_Signature(self) -> None:
		self.assertEqual(
			["demo.lib_a.utilities.to_index(natural)", "demo.lib_a.utilities.to_index(natural,positive)"],
			self._find("function", "to_index")
		)
		self.assertEqual(
			["demo.lib_a.utilities.to_index(natural,positive)"],
			self._find("function", "Utilities.to_index(Natural, Positive)")
		)
		self.assertEqual([], self._find("function", "to_index(integer)"))
		self.assertEqual([], self._find("function", "to_index(natural, positive, positive)"))

	def test_Signature_TypeMarkSuffix(self) -> None:
		"""A signature's type mark may be a part of the declared type mark, ending with the type's name."""
		resize = "demo.lib_a.utilities.resize(ieee.numeric_std.unsigned,natural)"
		self.assertEqual([resize], self._find("function", "resize(unsigned, natural)"))
		self.assertEqual([resize], self._find("function", "resize(numeric_std.unsigned, natural)"))
		self.assertEqual([], self._find("function", "resize(signed, natural)"))
		self.assertEqual([], self._find("function", "resize(d.unsigned, natural)"))

	def test_OtherType(self) -> None:
		self.assertEqual([], self._find("package", "Counter"))


class ReadDesigns(Project):
	"""Designs of ``vhdl_designs``, which can't be read, are logged as errors."""

	def test_ConfigurationError(self) -> None:
		self._build({}, vhdl_designs={"Broken": []})

		self.assertEqual(
			[
				"ERROR: Design 'Broken' not read: vhdl_designs['Broken']: Value is not a mapping.",
				"  Got type 'list'. [vhdl.design]"
			],
			self._warningLines()
		)

	def test_WithoutPyGHDL(self) -> None:
		with patch.dict("sys.modules", {"pyGHDL": None, "pyGHDL.dom": None, "pyGHDL.dom.NonStandard": None}):
			self._build({}, vhdl_designs={"Empty": {"libraries": {}}})

		self.assertEqual(
			[
				"ERROR: Design 'Empty' not read: Optional dependency 'pyGHDL' not installed.",
				"  Install 'pyGHDL'. [vhdl.design]"
			],
			self._warningLines()
		)


class AddDesign(Project):
	def test_Checks(self) -> None:
		app = self._build({})
		domain: VHDLDomain = app.env.get_domain("vhdl")

		for name, design, exception in (
			(None,  Design(), ValueError),
			(1,     Design(), TypeError),
			("",    Design(), ValueError),
			("New", None,     ValueError),
			("New", "design", TypeError),
		):
			with self.subTest(name=name, design=design):
				with self.assertRaises(exception):
					domain.AddDesign(name, design)

	def test_Duplicate(self) -> None:
		app = self._build({})
		domain: VHDLDomain = app.env.get_domain("vhdl")

		with self.assertRaises(Exception) as context:
			domain.AddDesign("DEMO", Design())

		self.assertEqual("Design 'DEMO' was added already.", str(context.exception))

	def test_GetDesign(self) -> None:
		app = self._build({})
		domain: VHDLDomain = app.env.get_domain("vhdl")

		self.assertEqual("Demo", domain.GetDesign("demo").Name)
		self.assertIsNone(domain.GetDesign("Missing"))
