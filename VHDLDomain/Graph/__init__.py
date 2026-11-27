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
Pictures of a design's graphs: the dependency graph, the compile-order graph and the hierarchy graph of pyVHDLModel.

A design analyzed by pyVHDLModel holds three graphs of :mod:`pyTooling.Graph`, whose vertices carry a key-value-pair
``kind``, a :class:`~pyVHDLModel.DependencyGraphVertexKind`. :func:`selectPortion` selects a part of a graph: the
vertices reached from a start vertex, optionally only up to a depth. :func:`vertexLabel` names a vertex as a design
names its unit, e.g. ``lib_Utilities.Counter(rtl)``. pyTooling's :class:`~pyTooling.Graph.Layout.Layered.LayeredLayout`
lays the vertices out, and :class:`DesignGraphBuilder` draws the layout on a canvas, each box filled in the color of
its kind.

.. code-block:: python

   from pyTooling.Graph.Layout.Layered import LayeredLayout
   from VHDLDomain.Graph               import DesignGraphBuilder, vertexLabel

   layout = LayeredLayout(label=vertexLabel).Compute(design.HierarchyGraph)
   canvas = DesignGraphBuilder().Build(layout)
"""
from __future__                     import annotations

from typing                         import ClassVar, Iterable, Optional as Nullable

from pyTooling.Cartesian2D.Drawing  import CurrentColor, Fill, RGBAColor, Stroke
from pyTooling.Common               import StringEnum, getFullyQualifiedName
from pyTooling.Decorators           import export
from pyTooling.Graph                import Vertex
from pyTooling.Graph.Layout         import VertexPlacement
from pyTooling.Graph.Layout.Drawing import CanvasBuilder

from pyVHDLModel                    import DependencyGraphVertexKind


@export
class FollowEdges(StringEnum):
	"""
	The edges followed from a portion's start vertex, as option ``:follow:`` states it.

	pyVHDLModel's edges point from a user to what it uses: from a design unit to the units it references, from an
	architecture to the entities it instantiates, from a source file to the files compiled before it.
	"""

	Outbound = "outbound"  #: Along the edges: what the start uses.
	Inbound =  "inbound"   #: Against the edges: what uses the start.
	Both =     "both"      #: Both directions.

	DEFAULT =  Outbound    #: Without a value, the edges are followed to what the start uses.


@export
class ImageFormat(StringEnum):
	"""
	The format of a graph's picture, as option ``:format:`` states it.
	"""

	SVG = "svg"  #: A vector picture: inline SVG in HTML, a TikZ picture in LaTeX.
	PNG = "png"  #: A PNG image, drawn by matplotlib.

	DEFAULT = SVG  #: Without a value, the picture is a vector picture.


@export
def vertexLabel(vertex: Vertex) -> str:
	"""
	Return the label of a vertex of a design's graph: the name of the library, design unit or source file it represents.

	A design unit is named with its library, e.g. ``lib_Utilities.Counter``; an architecture adds its name to the
	entity's, e.g. ``lib_Utilities.Counter(rtl)``, a package body ``(body)`` to the package's. A source file is named by
	its file name, e.g. ``Counter.vhdl``. A vertex of another kind is named by its ID.

	:param vertex: The vertex, whose value is a :class:`~pyVHDLModel.Library`, a design unit or a
	               :class:`~pyVHDLModel.Document`.
	:returns:      The label.
	"""
	kind =  vertex.get("kind", None)
	value = vertex.Value
	if kind is DependencyGraphVertexKind.Document:
		return value.Path.name
	elif kind is DependencyGraphVertexKind.Library:
		return value.Identifier
	elif kind is DependencyGraphVertexKind.Architecture:
		return f"{value.Library.Identifier}.{value.Entity.Name.Identifier}({value.Identifier})"
	elif kind is DependencyGraphVertexKind.PackageBody:
		return f"{value.Library.Identifier}.{value.Package.Name.Identifier}(body)"
	elif kind is None or kind is DependencyGraphVertexKind.Component:
		return str(vertex.ID)

	return f"{value.Library.Identifier}.{value.Identifier}"


@export
def selectPortion(
	vertices: Iterable[Vertex],
	start:    Nullable[Vertex] = None,
	depth:    Nullable[int] = None,
	follow:   FollowEdges = FollowEdges.Outbound
) -> list[Vertex]:
	"""
	Select a portion of a graph: the vertices reached from a start vertex, following edges up to a depth.

	The search runs on the given vertices only: an edge to a vertex not given isn't followed, so a portion of the
	vertices of a library doesn't reach into another library. Without a start vertex, the portion is every given vertex.

	:param vertices:    The vertices to select from, e.g. a graph's vertices of a library.
	:param start:       Optional, the vertex the portion starts at. Default: ``None``, every given vertex.
	:param depth:       Optional, the number of edges followed from the start vertex. Default: ``None``, as many as
	                    there are.
	:param follow:      Optional, the edges followed from the start vertex. Default: ``FollowEdges.Outbound``.
	:returns:           The selected vertices, in the order of parameter 'vertices'.
	:raises ValueError: If parameter 'vertices' is None.
	:raises TypeError:  If parameter 'vertices' is not iterable.
	:raises TypeError:  If an element of parameter 'vertices' is not of type :class:`~pyTooling.Graph.Vertex`.
	:raises TypeError:  If parameter 'start' is not of type :class:`~pyTooling.Graph.Vertex`.
	:raises ValueError: If parameter 'start' is not an element of parameter 'vertices'.
	:raises TypeError:  If parameter 'depth' is not of type :class:`int`.
	:raises ValueError: If parameter 'depth' is negative.
	:raises ValueError: If parameter 'follow' is None.
	:raises TypeError:  If parameter 'follow' is not of type :class:`FollowEdges`.
	"""
	if vertices is None:
		raise ValueError("Parameter 'vertices' is None.")
	elif not isinstance(vertices, Iterable):
		ex = TypeError("Parameter 'vertices' is not iterable.")
		ex.add_note(f"Got type '{getFullyQualifiedName(vertices)}'.")
		raise ex

	candidates = []
	for vertex in vertices:
		if not isinstance(vertex, Vertex):
			ex = TypeError("Element of parameter 'vertices' is not of type 'Vertex'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(vertex)}'.")
			raise ex

		candidates.append(vertex)

	allowed = set(candidates)
	if start is not None:
		if not isinstance(start, Vertex):
			ex = TypeError("Parameter 'start' is not of type 'Vertex'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif start not in allowed:
			ex = ValueError("Parameter 'start' is not an element of parameter 'vertices'.")
			ex.add_note(f"Got vertex '{start.ID}'.")
			raise ex

	if depth is not None:
		if not isinstance(depth, int):
			ex = TypeError("Parameter 'depth' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex
		elif depth < 0:
			ex = ValueError("Parameter 'depth' is negative.")
			ex.add_note(f"Got value '{depth}'.")
			raise ex

	if follow is None:
		raise ValueError("Parameter 'follow' is None.")
	elif not isinstance(follow, FollowEdges):
		ex = TypeError("Parameter 'follow' is not of type 'FollowEdges'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(follow)}'.")
		raise ex

	if start is None:
		return candidates

	outbound = follow is not FollowEdges.Inbound
	inbound =  follow is not FollowEdges.Outbound
	reached =  {start}
	frontier = [start]
	steps =    len(candidates) if depth is None else depth
	while steps > 0 and len(frontier) > 0:
		steps -= 1
		neighbours = []
		for vertex in frontier:
			if outbound:
				for edge in vertex.IterateOutboundEdges():
					if (destination := edge.Destination) in allowed and destination not in reached:
						reached.add(destination)
						neighbours.append(destination)

			if inbound:
				for edge in vertex.IterateInboundEdges():
					if (source := edge.Source) in allowed and source not in reached:
						reached.add(source)
						neighbours.append(source)

		frontier = neighbours

	return [vertex for vertex in candidates if vertex in reached]


@export
class DesignGraphBuilder(CanvasBuilder):
	"""
	Builds the canvas of a design's graph: each box filled in the color of its vertex' kind.

	Lines and box outlines are drawn in :class:`~pyTooling.Cartesian2D.Drawing.CurrentColor`, so an SVG picture takes
	the text color of the page it is embedded in, also of a dark page. A label in a filled box is black, as the fills are
	light colors; a box of a kind without color is transparent, its label in the current color.
	"""

	_FILLS: ClassVar[dict[DependencyGraphVertexKind, Fill]] = {
		DependencyGraphVertexKind.Document:      Fill(RGBAColor(255, 255, 210)),
		DependencyGraphVertexKind.Library:       Fill(RGBAColor(230, 230, 230)),
		DependencyGraphVertexKind.Context:       Fill(RGBAColor(250, 220, 250)),
		DependencyGraphVertexKind.Package:       Fill(RGBAColor(210, 230, 255)),
		DependencyGraphVertexKind.PackageBody:   Fill(RGBAColor(230, 240, 255)),
		DependencyGraphVertexKind.Entity:        Fill(RGBAColor(220, 255, 220)),
		DependencyGraphVertexKind.Architecture:  Fill(RGBAColor(255, 240, 210)),
		DependencyGraphVertexKind.Component:     Fill(RGBAColor(220, 245, 245)),
		DependencyGraphVertexKind.Configuration: Fill(RGBAColor(255, 220, 220)),
	}  #: The fill of a box, by the kind of its vertex.
	_FILLED_LABEL: ClassVar[Fill] = Fill(RGBAColor(0, 0, 0))  #: The fill of a label in a filled box.

	def __init__(self) -> None:
		"""
		Initializes a canvas builder drawing lines and labels in the current color.
		"""
		super().__init__(
			vertexStroke=Stroke(1, CurrentColor()),
			labelFill=Fill(CurrentColor()),
			edgeStroke=Stroke(1, CurrentColor())
		)

	def _VertexFill(self, placement: VertexPlacement) -> Nullable[Fill]:
		"""
		Return the fill of a vertex' box: the color of its kind.

		:param placement: The vertex' placement.
		:returns:         The fill of the vertex' kind, or ``None`` for a vertex without a kind of :attr:`_FILLS`.
		"""
		return self._FILLS.get(placement.Vertex.get("kind", None), None)

	def _LabelFill(self, placement: VertexPlacement) -> Fill:
		"""
		Return the fill of a vertex' label: black in a filled box, otherwise the current color.

		:param placement: The vertex' placement.
		:returns:         The fill of the label.
		"""
		if placement.Vertex.get("kind", None) in self._FILLS:
			return self._FILLED_LABEL

		return self._labelFill
