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
"""
The directive ``vhdl:symbol``, which draws an entity's or a component's interface symbol, and the node it emits.

HTML draws the symbol as inline SVG, LaTeX as TikZ picture. Every other builder writes the node's text, a listing of
the symbol's parameters and pins.
"""
from __future__             import annotations

from typing                 import ClassVar, Optional as Nullable

from docutils               import nodes
from docutils.nodes         import Node
from docutils.parsers.rst   import directives
from sphinx.application     import Sphinx
from sphinx.builders.latex  import LaTeXBuilder
from sphinx.util.logging    import getLogger
from sphinx.writers.html5   import HTML5Translator
from sphinx.writers.latex   import LaTeXTranslator

from pyTooling.Decorators   import export

from pyVHDLModel            import Design
from pyVHDLModel.DesignUnit import Component, DesignUnit, Entity

from VHDLDomain.Directive   import VHDLDirective
from VHDLDomain.Symbol      import InterfaceSymbol, PinSide
from VHDLDomain.Symbol.VHDL import VHDLConverter


_logger = getLogger(__name__)


@export
class SymbolNode(nodes.literal_block):
	"""
	An entity's or a component's interface symbol, which HTML draws as inline SVG and LaTeX as TikZ picture.

	Attribute ``symbol`` holds the :class:`~VHDLDomain.Symbol.InterfaceSymbol`. The node's text lists the symbol's
	parameters and pins, so a builder without visitors for this node writes it as a literal block.
	"""


@export
def html_visit_SymbolNode(translator: HTML5Translator, node: SymbolNode) -> None:
	"""
	Write an interface symbol in HTML, completely: the inline SVG of :class:`~VHDLDomain.Symbol.SVG.SVGRenderer` in a
	``div`` of the classes ``vhdl`` and ``vhdl-symbol``.

	:param translator: The HTML translator writing the document.
	:param node:       The symbol's node.
	:raises SkipNode:  Always, so the node's text isn't written.
	"""
	from VHDLDomain.Symbol.SVG import SVGRenderer

	svg = SVGRenderer().Render(node["symbol"])
	translator.body.append(f"<div class=\"vhdl vhdl-symbol\">\n{svg}\n</div>\n")

	raise nodes.SkipNode


@export
def latex_visit_SymbolNode(translator: LaTeXTranslator, node: SymbolNode) -> None:
	"""
	Write an interface symbol in LaTeX, completely: the ``tikzpicture`` of :class:`~VHDLDomain.Symbol.TikZ.TikZRenderer`
	as a paragraph of its own.

	:param translator: The LaTeX translator writing the document.
	:param node:       The symbol's node.
	:raises SkipNode:  Always, so the node's text isn't written.
	"""
	from VHDLDomain.Symbol.TikZ import TikZRenderer

	tikz = TikZRenderer().Render(node["symbol"])
	translator.body.append(f"\n\n{tikz}\n\n")

	raise nodes.SkipNode


@export
def loadTikZLibraries(sphinx: Sphinx) -> None:
	"""
	Call-back for Sphinx' ``builder-inited`` event, loading the TikZ libraries the symbols' pictures need in the LaTeX
	preamble.

	The libraries are those of :class:`~VHDLDomain.Symbol.TikZ.TikZRenderer`; other builders than LaTeX are left alone.

	:param sphinx: The Sphinx application.
	"""
	if sphinx.builder.format != "latex":
		return

	from VHDLDomain.Symbol.TikZ import TikZRenderer

	builder: LaTeXBuilder = sphinx.builder  # type: ignore[assignment]
	if len(libraries := TikZRenderer.TIKZ_LIBRARIES) > 0:
		builder.context["preamble"] += f"\n\\usetikzlibrary{{{','.join(libraries)}}}\n"


@export
class SymbolDirective(VHDLDirective):
	"""
	The directive ``vhdl:symbol``: an entity's or a component's interface symbol.

	.. code-block:: rst

	   .. vhdl:symbol:: lib_Utilities.Counter

	The argument names an entity as ``[library.]entity``, a component declared in a package as
	``[library.]package.component``, or a component declared in an architecture as
	``[library.]entity.architecture.component``. The name is looked up in the current library and - if its first part
	names a library - in that library; a name matching no unit or several units is warned about.

	The generics become the symbol's parameters, the ports its pins (see :class:`~VHDLDomain.Symbol.VHDL.VHDLConverter`).
	The directive describes no object of the domain: it has no target and no index entry.
	"""

	directiveName: ClassVar[str] = "vhdl:symbol"  #: Name the directive is invoked by.

	has_content =        False                                      #: The directive has no content.
	required_arguments = 1                                          #: The entity's or component's name.
	option_spec =        {"design": directives.unchanged_required}  #: The design, if not the current one.

	def run(self) -> list[Node]:
		"""
		Find the entity or component, and convert it into a symbol.

		:returns: The symbol's node, or nothing if the name matches no unit or several units.
		"""
		name = self.arguments[0].strip()
		designName, design = self._CurrentDesign()
		if design is None:
			return []

		parts =   name.split(".")
		library = self.env.ref_context.get("vhdl:library", None)
		if len(parts) == 1 and library is None:
			_logger.warning(
				f"{self.directiveName}: No library: name it as '<library>.{name}' or place a 'vhdl:library' before it.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="library"
			)
			return []

		candidates = self._Candidates(design, parts, library)
		if len(candidates) == 0:
			_logger.warning(
				f"{self.directiveName}: Entity or component '{name}' is not in design '{designName}'.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="symbol"
			)
			return []
		elif len(candidates) > 1:
			_logger.warning(
				f"{self.directiveName}: '{name}' is ambiguous, candidates: "
				f"{', '.join(sorted(description for description, _, _ in candidates))}.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="symbol"
			)
			return []

		_, unit, designUnit = candidates[0]
		document = getattr(designUnit, "Document", None)
		if document is not None and (path := getattr(document, "Path", None)) is not None:
			self.env.note_dependency(str(path))

		symbol = VHDLConverter(self._Format).Convert(unit)
		text =   self._Text(symbol)
		node =   SymbolNode(text, text, symbol=symbol, classes=["vhdl", "vhdl-symbol"])
		self.set_source_info(node)

		return [node]

	@staticmethod
	def _Candidates(
		design:  Design,
		parts:   list[str],
		library: Nullable[str]
	) -> list[tuple[str, Entity | Component, DesignUnit]]:
		"""
		Find the entities and components a name's parts name: in the current library, and in the library named by the
		first part.

		:param design:  The design.
		:param parts:   The name's parts, split at the dots.
		:param library: The current library's name, or ``None`` if no library is current.
		:returns:       Per match, its description - as ``entity lib_A.Counter`` -, the entity or component, and the design
		                unit declaring it.
		"""
		candidates: list[tuple[str, Entity | Component, DesignUnit]] = []

		def findIn(libraryName: str, names: list[str]) -> None:
			"""
			Nested function adding the entity or component the names - without the library - name in a library.

			:param libraryName: The library's name.
			:param names:       The names of the entity, or of the package and the component, or of the entity, the
			                    architecture and the component.
			"""
			if (library := design.Libraries.get(libraryName.lower(), None)) is None:
				return

			if len(names) == 1:
				if (entity := library.Entities.get(names[0].lower(), None)) is not None:
					candidates.append((f"entity {library.Identifier}.{entity.Identifier}", entity, entity))

				return

			if len(names) == 2:
				if (package := library.Packages.get(names[0].lower(), None)) is None:
					return

				prefix =       f"{library.Identifier}.{package.Identifier}"
				designUnit =   package
				declarations = package.DeclaredItems
			elif len(names) == 3:
				if (entity := library.Entities.get(names[0].lower(), None)) is None:
					return
				elif (architecture := entity.Architectures.get(names[1].lower(), None)) is None:
					return

				prefix =       f"{library.Identifier}.{entity.Identifier}.{architecture.Identifier}"
				designUnit =   architecture
				declarations = architecture.DeclaredItems
			else:
				return

			for item in declarations:
				if isinstance(item, Component) and item.NormalizedIdentifier == names[-1].lower():
					candidates.append((f"component {prefix}.{item.Identifier}", item, designUnit))

		if library is not None:
			findIn(library, parts)

		if len(parts) > 1:
			findIn(parts[0], parts[1:])

		return candidates

	@staticmethod
	def _Text(symbol: InterfaceSymbol) -> str:
		"""
		Write an interface symbol as text: its name, then a line per parameter and per pin.

		A parameter's line starts with ``parameter``, a pin's line with its side, ``left`` or ``right``; a named group's
		parameters or pins follow a line with the group's name.

		:param symbol: The interface symbol.
		:returns:      The text.
		"""
		lines = [symbol.Name]
		for parameterGroup in symbol.ParameterGroups:
			if parameterGroup.Name is not None:
				lines.append(f"  -- {parameterGroup.Name}")

			for parameter in parameterGroup.Parameters:
				default = "" if parameter.DefaultValue is None else f" := {parameter.DefaultValue}"
				lines.append(f"  parameter {parameter.Name} : {parameter.TypeLabel}{default}")

		for pinGroup in symbol.PinGroups:
			if pinGroup.Name is not None:
				lines.append(f"  -- {pinGroup.Name}")

			for pin in pinGroup.Pins:
				side = "left" if pin.Side is PinSide.Left else "right"
				lines.append(f"  {side:<9} {pin.Name} : {pin.TypeLabel}")

		return "\n".join(lines)
