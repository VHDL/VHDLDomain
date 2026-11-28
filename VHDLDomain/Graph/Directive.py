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
The directives ``vhdl:dependencies``, ``vhdl:compile-order`` and ``vhdl:hierarchy``, which draw a design's graphs, and
the node they emit.

Each directive draws one of pyVHDLModel's graphs of a design - or a portion of it -, laid out once by pyTooling's
:class:`~pyTooling.Graph.Layout.Layered.LayeredLayout`. HTML writes the picture as inline SVG, LaTeX as TikZ picture;
in format ``png``, both include a PNG image instead. Every other builder writes the node's text, a listing of the
vertices and edges.
"""
from __future__                        import annotations

from hashlib                           import sha1
from html                              import escape
from pathlib                           import Path, PurePath
from posixpath                         import join as posixJoin
from typing                            import ClassVar, Optional as Nullable

from docutils                          import nodes
from docutils.nodes                    import Node
from docutils.parsers.rst              import directives
from sphinx.util.logging               import getLogger
from sphinx.writers.html5              import HTML5Translator
from sphinx.writers.latex              import LaTeXTranslator

from pyTooling.Cartesian2D.Render.SVG  import SVGRenderer
from pyTooling.Cartesian2D.Render.TikZ import TikZRenderer
from pyTooling.Decorators              import export
from pyTooling.Exceptions              import MissingDependencyError
from pyTooling.Graph                   import Graph, Vertex
from pyTooling.Graph.Layout            import GraphLayout, LayoutDirection
from pyTooling.Graph.Layout.Layered    import LayeredLayout

from pyVHDLModel                       import Design, DependencyGraphVertexKind

from VHDLDomain.Directive              import VHDLDirective
from VHDLDomain.Graph                  import DesignGraphBuilder, FollowEdges, ImageFormat, selectPortion, vertexLabel


_logger = getLogger(__name__)


@export
class GraphNode(nodes.literal_block):
	"""
	The picture of a design's graph, which HTML draws as inline SVG and LaTeX as TikZ picture - or both as PNG image.

	The picture is rendered once, by the directive: attribute ``svg`` holds the SVG image, ``tikz`` the TikZ picture,
	``png`` the PNG image's content in format ``png``, otherwise ``None``; ``alt`` holds the picture's alternative text,
	``width`` its width in points. The node's text lists the vertices and edges, so a builder without visitors for this
	node writes it as a literal block.
	"""

	def WriteImage(self, directory: Path) -> str:
		"""
		Write the PNG image into a directory, named by a hash of its content, unless the file exists already.

		An unchanged picture is written once: a later build finds a file of the same name, thus of the same content.

		:param directory: The directory.
		:returns:         The file's name, e.g. ``vhdl-graph-<hash>.png``.
		"""
		content = self["png"]
		name =    f"vhdl-graph-{sha1(content, usedforsecurity=False).hexdigest()}.png"
		if not (path := directory / name).exists():
			directory.mkdir(parents=True, exist_ok=True)
			with path.open("wb") as file:
				file.write(content)

		return name


@export
def html_visit_GraphNode(translator: HTML5Translator, node: GraphNode) -> None:
	"""
	Write a graph's picture in HTML, completely: the inline SVG image - or an ``img`` element of the PNG image, written
	into the image directory - in a ``div`` of the classes ``vhdl`` and ``vhdl-graph``.

	A picture wider than the page's content scrolls horizontally instead of overflowing it.

	:param translator: The HTML translator writing the document.
	:param node:       The graph's node.
	:raises SkipNode:  Always, so the node's text isn't written.
	"""
	translator.body.append(translator.starttag(node, "div", style="overflow-x: auto;"))
	if node["png"] is None:
		translator.body.append(node["svg"])
	else:
		builder = translator.builder
		name =    node.WriteImage(Path(builder.outdir) / builder.imagedir)
		translator.body.append(
			f"<img src=\"{posixJoin(builder.imgpath, name)}\" alt=\"{escape(node['alt'])}\" "
			f"style=\"width: {node['width']:g}pt;\" />\n"
		)

	translator.body.append("</div>\n")

	raise nodes.SkipNode


@export
def latex_visit_GraphNode(translator: LaTeXTranslator, node: GraphNode) -> None:
	"""
	Write a graph's picture in LaTeX, completely: the ``tikzpicture`` - or the PNG image, written into the output
	directory - as a paragraph of its own.

	A picture wider than the line is scaled down to the line width; a narrower one keeps its size.

	:param translator: The LaTeX translator writing the document.
	:param node:       The graph's node.
	:raises SkipNode:  Always, so the node's text isn't written.
	"""
	translator.body.append(f"\n\n{translator.hypertarget_to(node)}")
	if node["png"] is None:
		width = "\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi"
		translator.body.append(f"\\resizebox{{{width}}}{{!}}{{%\n{node['tikz']}%\n}}\n\n")
	else:
		name = node.WriteImage(Path(translator.builder.outdir))
		translator.body.append(f"\\sphinxincludegraphics{{{name}}}\n\n")

	raise nodes.SkipNode


@export
class GraphDirective(VHDLDirective):
	"""
	Base-class of the directives drawing a design's graph, or a portion of it.

	The optional argument names the vertex a portion starts at; the portion holds the vertices reached from it by
	following edges, see :func:`~VHDLDomain.Graph.selectPortion`. Without argument, the whole graph is drawn. Option
	``:libraries:`` keeps the vertices of the named libraries only. An edge to a vertex, which isn't drawn, is left out.

	A derived class names the graph, its title and the layout direction by default, and finds the start vertex.
	"""

	_GRAPH:     ClassVar[str]              #: Name of the property of :class:`~pyVHDLModel.Design` holding the graph.
	_TITLE:     ClassVar[str]              #: Title of the graph, the start of the picture's alternative text.
	_DIRECTION: ClassVar[LayoutDirection]  #: The layout direction by default.

	_DIRECTIONS: ClassVar[dict[str, LayoutDirection]] = {
		"top-to-bottom": LayoutDirection.TopToBottom,
		"bottom-to-top": LayoutDirection.BottomToTop,
		"left-to-right": LayoutDirection.LeftToRight,
		"right-to-left": LayoutDirection.RightToLeft,
	}  #: The layout directions, by the value of option ``:direction:``.

	has_content =               False  #: The directive has no content.
	optional_arguments =        1      #: The vertex the portion starts at.
	final_argument_whitespace = True   #: A file name may contain spaces.

	@staticmethod
	def _ParseNames(argument: Nullable[str]) -> list[str]:
		"""
		Convert the value of an option naming libraries: names separated by commas or white space.

		:param argument:    The option's value.
		:returns:           The names.
		:raises ValueError: If the value names nothing.
		"""
		if argument is None or len(names := argument.replace(",", " ").split()) == 0:
			raise ValueError("No name given.")

		return names

	@staticmethod
	def _ParseDirection(argument: Nullable[str]) -> LayoutDirection:
		"""
		Convert the value of option ``:direction:`` to a layout direction.

		:param argument:    The option's value.
		:returns:           The layout direction.
		:raises ValueError: If the value names no layout direction. |br|
		                    The note lists the allowed values.
		"""
		directions = GraphDirective._DIRECTIONS
		if argument is None or (direction := directions.get(argument.strip(), None)) is None:
			ex = ValueError(f"'{argument}' is not a layout direction.")
			ex.add_note(f"Allowed values: {', '.join(directions)}.")
			raise ex

		return direction

	option_spec = {
		"design":    directives.unchanged_required,
		"depth":     directives.nonnegative_int,
		"follow":    FollowEdges.Parse,
		"libraries": _ParseNames,
		"direction": _ParseDirection,
		"format":    ImageFormat.Parse,
		"alt":       directives.unchanged,
		"caption":   directives.unchanged,
		"name":      directives.unchanged,
	}  #: The design, if not the current one; the portion's depth and followed edges; the drawn libraries; the layout
	#: direction; the picture's format, alternative text and caption; a name to refer to the picture.

	def run(self) -> list[Node]:
		"""
		Select the vertices, lay them out and render the picture.

		:returns: The picture's node - in a figure, if it has a caption -, or nothing if there is nothing to draw.
		"""
		designName, design = self._CurrentDesign()
		if design is None:
			return []

		graph: Graph = getattr(design, self._GRAPH)
		if (candidates := self._Candidates(design, graph)) is None:
			return []

		start = None
		if len(self.arguments) == 1:
			if (start := self._Start(graph, candidates, self.arguments[0].strip())) is None:
				return []
		else:
			for option in ("depth", "follow"):
				if option in self.options:
					_logger.warning(
						f"{self.directiveName}: Option ':{option}:' without a start vertex is ignored.",
						location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
					)

		portion = selectPortion(
			candidates, start, self.options.get("depth", None), self.options.get("follow", FollowEdges.DEFAULT)
		)
		if len(portion) == 0:
			_logger.warning(
				f"{self.directiveName}: Nothing to draw.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
			)
			return []

		for document in design.Documents:
			self.env.note_dependency(str(document.Path))

		layout = LayeredLayout(
			direction=self.options.get("direction", self._DIRECTION),
			label=vertexLabel
		).Compute(graph, portion)
		node = self._Node(layout, designName)
		self.set_source_info(node)

		if (caption := self.options.get("caption", None)) is None:
			self.add_name(node)
			return [node]

		inlines, messages = self.parse_inline(caption, lineno=self.lineno)
		figure = nodes.figure("", node)
		figure += nodes.caption(caption, "", *inlines)
		self.set_source_info(figure)
		self.add_name(figure)

		return [figure, *messages]

	def _Candidates(self, design: Design, graph: Graph) -> Nullable[list[Vertex]]:
		"""
		Return the vertices the options let be drawn: those of the libraries of option ``:libraries:``.

		A library, which isn't in the design, is warned about.

		:param design: The design.
		:param graph:  The design's graph.
		:returns:      The vertices, in the graph's order, or ``None`` if a library isn't in the design.
		"""
		if (names := self.options.get("libraries", None)) is None:
			return list(graph.IterateVertices())

		libraries = set()
		for name in names:
			if (library := design.Libraries.get(name.lower(), None)) is None:
				_logger.warning(
					f"{self.directiveName}: Library '{name}' is not in the design.",
					location=self.get_location(), type=self._WARNING_TYPE, subtype="library"
				)
				return None

			libraries.add(library)

		candidates = []
		for vertex in graph.IterateVertices():
			value = vertex.Value
			if (value if vertex["kind"] is DependencyGraphVertexKind.Library else value.Library) in libraries:
				candidates.append(vertex)

		return candidates

	def _Start(self, graph: Graph, candidates: list[Vertex], name: str) -> Nullable[Vertex]:
		"""
		Find the vertex a portion starts at.

		A name matching no vertex or several vertices, and a vertex, which the options don't let be drawn, are warned
		about.

		:param graph:      The design's graph.
		:param candidates: The vertices the options let be drawn.
		:param name:       The argument naming the vertex.
		:returns:          The vertex, or ``None``.
		"""
		matches = self._FindVertices(graph, name)
		if len(matches) == 0:
			_logger.warning(
				f"{self.directiveName}: '{name}' is not in the {self._TITLE.lower()}.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
			)
			return None
		elif len(matches) > 1:
			_logger.warning(
				f"{self.directiveName}: '{name}' is ambiguous, candidates: "
				f"{', '.join(sorted(vertexLabel(vertex) for vertex in matches))}.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
			)
			return None
		elif (start := matches[0]) not in candidates:
			_logger.warning(
				f"{self.directiveName}: '{name}' is left out by the options.",
				location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
			)
			return None

		return start

	def _FindVertices(self, graph: Graph, name: str) -> list[Vertex]:
		"""
		Find the vertices a name names, by vertex ID: the name as given, and in the current library.

		pyVHDLModel's IDs are lower-case: a library ``lib_a``, a design unit ``lib_a.counter``, an architecture
		``lib_a.counter(rtl)``, a package body ``lib_a.utilities(body)``.

		:param graph: The design's graph.
		:param name:  The name.
		:returns:     The matching vertices.
		"""
		normalized = "".join(name.split()).lower()
		identifiers = [normalized]
		if (library := self.env.ref_context.get("vhdl:library", None)) is not None:
			identifiers.append(f"{library.lower()}.{normalized}")

		return [graph.GetVertexByID(identifier) for identifier in identifiers if graph.ContainsVertexByID(identifier)]

	def _Node(self, layout: GraphLayout, designName: Nullable[str]) -> GraphNode:
		"""
		Render the layout as SVG and TikZ picture - and as PNG image in format ``png`` -, and create the picture's node.

		Without matplotlib - the extra ``diagram`` -, a PNG image is warned about and replaced by the vector picture.

		:param layout:     The layout.
		:param designName: The design's name, for the alternative text.
		:returns:          The node.
		"""
		if (alt := self.options.get("alt", None)) is None:
			alt = f"{self._TITLE} of design {designName}"
			if len(self.arguments) == 1:
				alt += f", from {self.arguments[0].strip()}"

		canvas = DesignGraphBuilder().Build(layout)
		png = None
		if self.options.get("format", ImageFormat.DEFAULT) is ImageFormat.PNG:
			from pyTooling.Cartesian2D.Render.Matplotlib import MatplotlibRenderer

			try:
				png = MatplotlibRenderer(canvas).Render("png")
			except MissingDependencyError:
				_logger.warning(
					f"{self.directiveName}: Drawn as vector picture, as matplotlib isn't installed: install the extra "
					"'VHDLDomain[diagram]'.",
					location=self.get_location(), type=self._WARNING_TYPE, subtype="graph"
				)

		labels = {placement.Vertex: placement.Label for placement in layout.Placements}
		lines = []
		for placement in layout.Placements:
			lines.append(placement.Label)
			for edge in placement.Vertex.IterateOutboundEdges():
				if layout.ContainsVertex(destination := edge.Destination):
					lines.append(f"  -> {labels[destination]}")

		text = "\n".join(lines)
		return GraphNode(
			text, text,
			svg=SVGRenderer(canvas, title=alt).Render(),
			tikz=TikZRenderer(canvas).Render(),
			png=png,
			alt=alt,
			width=canvas.Size.Width,
			classes=["vhdl", "vhdl-graph"]
		)


@export
class DependenciesDirective(GraphDirective):
	"""
	The directive ``vhdl:dependencies``: a design's dependency graph, or a portion of it.

	.. code-block:: rst

	   .. vhdl:dependencies:: lib_StopWatch.toplevel(rtl)
	      :depth: 1

	The argument names a library, a design unit as ``[library.]unit``, an architecture as ``[library.]entity(name)``
	or a package body as ``[library.]package(body)``. An edge points from a design unit to what it references: a
	library, a package, a context, an entity it instantiates or implements. Option ``:kinds:`` selects the kinds of
	vertices drawn, by default the design units; the predefined libraries ``std`` and ``ieee`` are drawn with option
	``:predefined:`` only.
	"""

	directiveName: ClassVar[str] =             "vhdl:dependencies"  #: Name the directive is invoked by.
	_GRAPH:        ClassVar[str] =             "DependencyGraph"    #: The graph's property of the design.
	_TITLE:        ClassVar[str] =             "Dependency graph"   #: The graph's title.
	_DIRECTION:    ClassVar[LayoutDirection] = LayoutDirection.TopToBottom  #: Used units below their users.

	_KINDS: ClassVar[dict[str, DependencyGraphVertexKind]] = {
		"library":       DependencyGraphVertexKind.Library,
		"context":       DependencyGraphVertexKind.Context,
		"package":       DependencyGraphVertexKind.Package,
		"package-body":  DependencyGraphVertexKind.PackageBody,
		"entity":        DependencyGraphVertexKind.Entity,
		"architecture":  DependencyGraphVertexKind.Architecture,
		"configuration": DependencyGraphVertexKind.Configuration,
		"document":      DependencyGraphVertexKind.Document,
	}  #: The vertex kinds, by their name in option ``:kinds:``.

	_DEFAULT_KINDS: ClassVar[DependencyGraphVertexKind] = (
		DependencyGraphVertexKind.Context | DependencyGraphVertexKind.Package | DependencyGraphVertexKind.PackageBody |
		DependencyGraphVertexKind.Entity | DependencyGraphVertexKind.Architecture | DependencyGraphVertexKind.Configuration
	)  #: The vertex kinds drawn without option ``:kinds:``: the design units.

	@staticmethod
	def _ParseKinds(argument: Nullable[str]) -> DependencyGraphVertexKind:
		"""
		Convert the value of option ``:kinds:`` - kinds separated by commas or white space - to the combined kinds.

		:param argument:    The option's value.
		:returns:           The kinds.
		:raises ValueError: If the value names no kind.
		:raises ValueError: If a name is no vertex kind. |br|
		                    The note lists the allowed values.
		"""
		allowed = DependenciesDirective._KINDS
		kinds =   DependencyGraphVertexKind(0)
		for name in GraphDirective._ParseNames(argument):
			if (kind := allowed.get(name, None)) is None:
				ex = ValueError(f"'{name}' is not a vertex kind.")
				ex.add_note(f"Allowed values: {', '.join(allowed)}.")
				raise ex

			kinds |= kind

		return kinds

	option_spec = {
		**GraphDirective.option_spec,
		"kinds":      _ParseKinds,
		"predefined": directives.flag,
	}  #: The options of every graph directive, the kinds of vertices drawn, and whether ``std`` and ``ieee`` are drawn.

	def _Candidates(self, design: Design, graph: Graph) -> Nullable[list[Vertex]]:
		"""
		Return the vertices the options let be drawn: those of the libraries of option ``:libraries:``, of the kinds of
		option ``:kinds:``, and - without option ``:predefined:`` - not of a predefined library.

		:param design: The design.
		:param graph:  The design's dependency graph.
		:returns:      The vertices, in the graph's order, or ``None`` if a library isn't in the design.
		"""
		if (candidates := super()._Candidates(design, graph)) is None:
			return None

		kinds = self.options.get("kinds", self._DEFAULT_KINDS)
		if "predefined" in self.options:
			return [vertex for vertex in candidates if vertex["kind"] in kinds]

		return [
			vertex for vertex in candidates if vertex["kind"] in kinds and vertex.get("predefined", False) is False
		]


@export
class CompileOrderDirective(GraphDirective):
	"""
	The directive ``vhdl:compile-order``: a design's compile-order graph, or a portion of it.

	.. code-block:: rst

	   .. vhdl:compile-order:: StopWatch.vhdl
	      :follow: inbound

	A vertex is a source file. The argument names a file by its name or the end of its path, e.g. ``Counter.vhdl`` or
	``StopWatch/Counter.vhdl``. An edge points from a file to a file compiled before it. By default, the picture is laid
	out from bottom to top: a file is drawn below the files compiled before it.
	"""

	directiveName: ClassVar[str] =             "vhdl:compile-order"  #: Name the directive is invoked by.
	_GRAPH:        ClassVar[str] =             "CompileOrderGraph"   #: The graph's property of the design.
	_TITLE:        ClassVar[str] =             "Compile order"       #: The graph's title.
	_DIRECTION:    ClassVar[LayoutDirection] = LayoutDirection.BottomToTop  #: Files compiled first on top.

	def _FindVertices(self, graph: Graph, name: str) -> list[Vertex]:
		"""
		Find the source files a name names: those, whose path ends in the name's parts.

		:param graph: The design's compile-order graph.
		:param name:  The file's name, or the end of its path.
		:returns:     The matching vertices.
		"""
		parts = PurePath(name).parts
		return [vertex for vertex in graph.IterateVertices() if vertex.Value.Path.parts[-len(parts):] == parts]


@export
class HierarchyDirective(GraphDirective):
	"""
	The directive ``vhdl:hierarchy``: a design's hierarchy graph, or a portion of it.

	.. code-block:: rst

	   .. vhdl:hierarchy:: lib_StopWatch.toplevel

	A vertex is an entity or an architecture. The argument names an entity as ``[library.]entity``, or an architecture as
	``[library.]entity(name)``. An edge points from an entity to its architectures, and from an architecture to the
	entities it instantiates.
	"""

	directiveName: ClassVar[str] =             "vhdl:hierarchy"  #: Name the directive is invoked by.
	_GRAPH:        ClassVar[str] =             "HierarchyGraph"  #: The graph's property of the design.
	_TITLE:        ClassVar[str] =             "Hierarchy"       #: The graph's title.
	_DIRECTION:    ClassVar[LayoutDirection] = LayoutDirection.TopToBottom  #: The top-level on top.
