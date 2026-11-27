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
Unit tests for the pictures of a design's graphs: labels, portions and the canvas builder.

The design is built by hand - no frontend needed - and analyzed by pyVHDLModel, which creates its graphs.
"""
from pathlib                        import Path

from pyTooling.Cartesian2D.Drawing  import CurrentColor, Fill, RGBAColor
from pyTooling.Graph                import Graph, Vertex
from pyTooling.Graph.Layout.Layered import LayeredLayout
from pyTooling.Testing              import Testcase

from pyVHDLModel                    import Design, DependencyGraphVertexKind, Document
from pyVHDLModel.Concurrent         import EntityInstantiation
from pyVHDLModel.DesignUnit         import Architecture, DesignUnit, Entity, LibraryClause, Package, PackageBody, \
                                           UseClause
from pyVHDLModel.Name               import AllName, SelectedName, SimpleName
from pyVHDLModel.Symbol             import AllPackageMembersReferenceSymbol, EntityInstantiationSymbol, EntitySymbol, \
                                           LibraryReferenceSymbol, PackageSymbol

from VHDLDomain.Graph               import DesignGraphBuilder, FollowEdges, ImageFormat, selectPortion, vertexLabel


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def demo() -> Design:
	"""
	Build and analyze design ``Demo``.

	* :file:`pkg.vhdl` in ``lib_A``: package ``Types`` and its body.
	* :file:`leaf.vhdl` in ``lib_A``: entity ``Leaf``, using ``Types``, and its architecture ``rtl``.
	* :file:`top.vhdl` in ``lib_B``: entity ``Top`` and its architecture ``rtl``, instantiating ``lib_A.Leaf``.
	* :file:`lib_B/pkg.vhdl` in ``lib_B``: package ``Types``.

	:returns: The design.
	"""
	def addDocument(library: str, path: str, *units: DesignUnit) -> None:
		"""
		Nested function adding a document with design units to a library.

		:param library: The library's name.
		:param path:    The document's path.
		:param units:   The design units.
		"""
		document = Document(Path(path))
		for unit in units:
			document._AddDesignUnit(unit)

		design.AddDocument(document, design.GetLibrary(library))

	design = Design("Demo")
	design.LoadStdLibrary()
	design.LoadIEEELibrary()

	addDocument("lib_A", "pkg.vhdl", Package("Types"), PackageBody(PackageSymbol(SimpleName("Types"))))
	addDocument(
		"lib_A", "leaf.vhdl",
		Entity(
			"Leaf",
			contextItems=[UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName("Types", SimpleName("work"))))])]
		),
		Architecture("rtl", EntitySymbol(SimpleName("Leaf")))
	)
	addDocument(
		"lib_B", "top.vhdl",
		Entity("Top", contextItems=[LibraryClause([LibraryReferenceSymbol(SimpleName("lib_A"))])]),
		Architecture(
			"rtl", EntitySymbol(SimpleName("Top")),
			statements=[EntityInstantiation("leaf", EntityInstantiationSymbol(SelectedName("Leaf", SimpleName("lib_A"))))]
		)
	)
	addDocument("lib_B", "lib_B/pkg.vhdl", Package("Types"))
	design.Analyze()

	return design


class Labels(Testcase):
	def test_DesignUnits(self) -> None:
		graph = demo().DependencyGraph

		self.assertEqual("lib_A", vertexLabel(graph.GetVertexByID("lib_a")))
		self.assertEqual("lib_A.Types", vertexLabel(graph.GetVertexByID("lib_a.types")))
		self.assertEqual("lib_A.Types(body)", vertexLabel(graph.GetVertexByID("lib_a.types(body)")))
		self.assertEqual("lib_A.Leaf", vertexLabel(graph.GetVertexByID("lib_a.leaf")))
		self.assertEqual("lib_A.Leaf(rtl)", vertexLabel(graph.GetVertexByID("lib_a.leaf(rtl)")))
		self.assertEqual("Std.Standard", vertexLabel(graph.GetVertexByID("std.standard")))

	def test_Documents(self) -> None:
		graph = demo().CompileOrderGraph

		self.assertEqual(
			["pkg.vhdl", "leaf.vhdl", "top.vhdl", "pkg.vhdl"], [vertexLabel(vertex) for vertex in graph.IterateVertices()]
		)

	def test_NoKind(self) -> None:
		"""A vertex without key ``kind`` is named by its ID."""
		self.assertEqual("A", vertexLabel(Vertex(vertexID="A", graph=Graph())))


class Portions(Testcase):
	def test_All(self) -> None:
		vertices = list(demo().HierarchyGraph.IterateVertices())

		self.assertEqual(vertices, selectPortion(vertices))

	def test_Outbound(self) -> None:
		graph = demo().HierarchyGraph

		portion = selectPortion(graph.IterateVertices(), graph.GetVertexByID("lib_b.top(rtl)"))

		self.assertEqual(["lib_a.leaf", "lib_a.leaf(rtl)", "lib_b.top(rtl)"], [vertex.ID for vertex in portion])

	def test_Depth(self) -> None:
		graph = demo().HierarchyGraph

		portion = selectPortion(graph.IterateVertices(), graph.GetVertexByID("lib_b.top"), 2)

		self.assertEqual(["lib_a.leaf", "lib_b.top", "lib_b.top(rtl)"], [vertex.ID for vertex in portion])

	def test_Depth_Zero(self) -> None:
		graph = demo().HierarchyGraph

		portion = selectPortion(graph.IterateVertices(), graph.GetVertexByID("lib_b.top"), 0)

		self.assertEqual(["lib_b.top"], [vertex.ID for vertex in portion])

	def test_Inbound(self) -> None:
		graph = demo().HierarchyGraph

		portion = selectPortion(graph.IterateVertices(), graph.GetVertexByID("lib_a.leaf"), follow=FollowEdges.Inbound)

		self.assertEqual(["lib_a.leaf", "lib_b.top", "lib_b.top(rtl)"], [vertex.ID for vertex in portion])

	def test_Both(self) -> None:
		graph = demo().HierarchyGraph

		portion = selectPortion(graph.IterateVertices(), graph.GetVertexByID("lib_a.leaf"), 1, FollowEdges.Both)

		self.assertEqual(["lib_a.leaf", "lib_a.leaf(rtl)", "lib_b.top(rtl)"], [vertex.ID for vertex in portion])

	def test_Restricted(self) -> None:
		"""An edge to a vertex not given isn't followed."""
		graph = demo().HierarchyGraph
		vertices = [vertex for vertex in graph.IterateVertices() if vertex.ID != "lib_a.leaf"]

		portion = selectPortion(vertices, graph.GetVertexByID("lib_b.top"))

		self.assertEqual(["lib_b.top", "lib_b.top(rtl)"], [vertex.ID for vertex in portion])

	def test_Vertices_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			selectPortion(None)

		self.assertEqual("Parameter 'vertices' is None.", str(context.exception))

	def test_Vertices_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			selectPortion(1)

		self.assertEqual("Parameter 'vertices' is not iterable.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Vertices_Element(self) -> None:
		with self.assertRaises(TypeError) as context:
			selectPortion(["A"])

		self.assertEqual("Element of parameter 'vertices' is not of type 'Vertex'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Start_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			selectPortion([], "A")

		self.assertEqual("Parameter 'start' is not of type 'Vertex'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Start_NotGiven(self) -> None:
		with self.assertRaises(ValueError) as context:
			selectPortion([], Vertex(vertexID="A", graph=Graph()))

		self.assertEqual("Parameter 'start' is not an element of parameter 'vertices'.", str(context.exception))
		self.assertEqual(["Got vertex 'A'."], context.exception.__notes__)

	def test_Depth_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			selectPortion([], depth=1.0)

		self.assertEqual("Parameter 'depth' is not of type 'int'.", str(context.exception))
		self.assertEqual(["Got type 'float'."], context.exception.__notes__)

	def test_Depth_Negative(self) -> None:
		with self.assertRaises(ValueError) as context:
			selectPortion([], depth=-1)

		self.assertEqual("Parameter 'depth' is negative.", str(context.exception))
		self.assertEqual(["Got value '-1'."], context.exception.__notes__)

	def test_Follow_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			selectPortion([], follow=None)

		self.assertEqual("Parameter 'follow' is None.", str(context.exception))

	def test_Follow_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			selectPortion([], follow="both")

		self.assertEqual("Parameter 'follow' is not of type 'FollowEdges'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class Options(Testcase):
	def test_FollowEdges(self) -> None:
		self.assertIs(FollowEdges.Outbound, FollowEdges.Parse(None))
		self.assertIs(FollowEdges.Inbound, FollowEdges.Parse("inbound"))
		self.assertIs(FollowEdges.Both, FollowEdges.Parse("both"))

	def test_ImageFormat(self) -> None:
		self.assertIs(ImageFormat.SVG, ImageFormat.Parse(None))
		self.assertIs(ImageFormat.PNG, ImageFormat.Parse("png"))


class Builder(Testcase):
	def test_Fills(self) -> None:
		"""Each box is filled in the color of its kind, its label is black; lines are in the current color."""
		design = demo()
		layout = LayeredLayout(label=vertexLabel).Compute(design.HierarchyGraph)

		canvas = DesignGraphBuilder().Build(layout)

		fills = {}
		for group in canvas.Children[-layout.PlacementCount:]:
			rectangle, text = group.Children
			fills[text.Content] = rectangle.Fill.Color.ToHex()
			self.assertIs(CurrentColor(), rectangle.Stroke.Color)
			self.assertEqual(RGBAColor(0, 0, 0), text.Fill.Color)

		self.assertEqual(
			{
				"lib_A.Leaf":      "#dcffdc",
				"lib_A.Leaf(rtl)": "#fff0d2",
				"lib_B.Top":       "#dcffdc",
				"lib_B.Top(rtl)":  "#fff0d2",
			},
			fills
		)
		for group in canvas.Children[:layout.RouteCount]:
			line, arrowhead = group.Children
			self.assertIs(CurrentColor(), line.Stroke.Color)

	def test_NoKind(self) -> None:
		"""A box without kind is transparent, its label in the current color."""
		graph = Graph()
		Vertex(vertexID="A", graph=graph)
		layout = LayeredLayout().Compute(graph)

		rectangle, text = DesignGraphBuilder().Build(layout).Children[0].Children

		self.assertIsNone(rectangle.Fill)
		self.assertEqual(Fill(CurrentColor()).Color, text.Fill.Color)
