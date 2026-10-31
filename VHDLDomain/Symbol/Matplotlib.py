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
Render an interface symbol as an image with :term:`matplotlib`.

matplotlib is an optional dependency, installed by the extra ``diagram``. It is imported when a symbol is rendered,
so this module imports without it.

.. code-block:: python

   from VHDLDomain.Symbol.Matplotlib import MatplotlibRenderer

   png = MatplotlibRenderer().Render(symbol)
   svg = MatplotlibRenderer().Render(symbol, "svg")
"""
from __future__               import annotations

from io                       import BytesIO
from typing                   import ClassVar

from pyTooling.Common         import getFullyQualifiedName
from pyTooling.Decorators     import export, readonly
from pyTooling.Exceptions     import MissingDependencyError
from pyTooling.MetaClasses    import ExtendedType

from VHDLDomain.Symbol        import InterfaceSymbol
from VHDLDomain.Symbol.Layout import BUS_LINE_WIDTH, DASH_PATTERN, FONT_SIZE, LINE_WIDTH, LineStyle, SymbolLayout, \
                                     TextAnchor, TextStyle


@export
class MatplotlibRenderer(metaclass=ExtendedType, slots=True):
	"""
	Renders an interface symbol with :term:`matplotlib` as PNG, SVG or PDF.

	The figure is as large as the layout: one point of the layout is one point (1/72 inch) of the figure. Lines and
	texts are black on a white background. Texts use matplotlib's ``monospace`` family; in an SVG file they stay text.

	matplotlib's object API is used, so no global :mod:`~matplotlib.pyplot` state is touched and no display is needed.
	"""

	FORMATS: ClassVar[tuple[str, ...]] = ("png", "svg", "pdf")  #: The image formats this renderer writes.

	_dpi: int  #: Resolution of a PNG image in dots per inch.

	def __init__(self, *, dpi: int = 144) -> None:
		"""
		Initializes a matplotlib renderer.

		:param dpi:         Optional, resolution of a PNG image in dots per inch. Default: ``144`` (two pixels per point).
		:raises ValueError: If parameter 'dpi' is None.
		:raises TypeError:  If parameter 'dpi' is not of type :class:`int`.
		:raises ValueError: If parameter 'dpi' isn't positive.
		"""
		if dpi is None:
			raise ValueError("Parameter 'dpi' is None.")
		elif not isinstance(dpi, int):
			ex = TypeError("Parameter 'dpi' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(dpi)}'.")
			raise ex
		elif dpi <= 0:
			ex = ValueError("Parameter 'dpi' isn't positive.")
			ex.add_note(f"Got value '{dpi}'.")
			raise ex

		self._dpi = dpi

	@readonly
	def DPI(self) -> int:
		"""
		Read-only property to access the resolution of a PNG image (:attr:`_dpi`).

		:returns: Resolution in dots per inch.
		"""
		return self._dpi

	def Render(self, symbol: InterfaceSymbol, format: str = "png") -> bytes:
		"""
		Render an interface symbol as an image.

		:param symbol:                  The symbol to render.
		:param format:                  Optional, the image format, one of :attr:`FORMATS`. Default: ``"png"``.
		:returns:                       The image file's content.
		:raises ValueError:             If parameter 'symbol' is None.
		:raises TypeError:              If parameter 'symbol' is not of type :class:`~VHDLDomain.Symbol.InterfaceSymbol`.
		:raises ValueError:             If parameter 'format' is None.
		:raises TypeError:              If parameter 'format' is not of type :class:`str`.
		:raises ValueError:             If parameter 'format' is not a format of :attr:`FORMATS`.
		:raises MissingDependencyError: If matplotlib isn't installed.
		"""
		if symbol is None:
			raise ValueError("Parameter 'symbol' is None.")
		elif not isinstance(symbol, InterfaceSymbol):
			ex = TypeError("Parameter 'symbol' is not of type 'InterfaceSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(symbol)}'.")
			raise ex

		if format is None:
			raise ValueError("Parameter 'format' is None.")
		elif not isinstance(format, str):
			ex = TypeError("Parameter 'format' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(format)}'.")
			raise ex
		elif format not in self.FORMATS:
			ex = ValueError("Parameter 'format' is not a supported image format.")
			ex.add_note(f"Got value '{format}'.")
			ex.add_note(f"Supported formats: {', '.join(self.FORMATS)}")
			raise ex

		try:
			from matplotlib         import rc_context
			from matplotlib.figure  import Figure
			from matplotlib.lines   import Line2D
			from matplotlib.patches import Circle, Polygon, Rectangle
		except ImportError as ex:
			raise MissingDependencyError(dependency="matplotlib") from ex

		layout =     SymbolLayout(symbol)
		lineWidths = {
			LineStyle.Normal: LINE_WIDTH,
			LineStyle.Thick:  BUS_LINE_WIDTH,
			LineStyle.Dashed: LINE_WIDTH
		}
		lineStyles = {
			LineStyle.Normal: "solid",
			LineStyle.Thick:  "solid",
			LineStyle.Dashed: (0.0, DASH_PATTERN)
		}
		alignments = {
			TextAnchor.Start:  "left",
			TextAnchor.Middle: "center",
			TextAnchor.End:    "right"
		}
		fontWeights = {
			TextStyle.Regular: "normal",
			TextStyle.Bold:    "bold",
			TextStyle.Italic:  "normal"
		}
		fontStyles = {
			TextStyle.Regular: "normal",
			TextStyle.Bold:    "normal",
			TextStyle.Italic:  "italic"
		}

		figure = Figure(figsize=(layout.Width / 72, layout.Height / 72), facecolor="white")
		axes =   figure.add_axes((0.0, 0.0, 1.0, 1.0))
		axes.set_xlim(0.0, layout.Width)
		axes.set_ylim(layout.Height, 0.0)
		axes.set_axis_off()

		for rectangle in layout.Rectangles:
			position = rectangle.Position
			axes.add_patch(Rectangle(
				(position.X, position.Y), rectangle.Width, rectangle.Height, fill=False, edgecolor="black",
				linewidth=lineWidths[rectangle.Style], linestyle=lineStyles[rectangle.Style], capstyle="butt"
			))

		for line in layout.Lines:
			start = line.Start
			end =   line.End
			axes.add_line(Line2D(
				(start.X, end.X), (start.Y, end.Y), color="black", linewidth=lineWidths[line.Style],
				linestyle=lineStyles[line.Style], solid_capstyle="butt"
			))

		for circle in layout.Circles:
			center = circle.Center
			axes.add_patch(Circle((center.X, center.Y), circle.Radius, fill=False, edgecolor="black", linewidth=LINE_WIDTH))

		for polygon in layout.Polygons:
			axes.add_patch(Polygon(
				[(point.X, point.Y) for point in polygon.Points],
				closed=True, fill=False, edgecolor="black", linewidth=LINE_WIDTH
			))

		for text in layout.Texts:
			position = text.Position
			axes.text(
				position.X, position.Y, text.Content,
				horizontalalignment=alignments[text.Anchor], verticalalignment="baseline", family="monospace",
				fontsize=FONT_SIZE, fontweight=fontWeights[text.Style], fontstyle=fontStyles[text.Style], color="black",
				parse_math=False
			)

		buffer = BytesIO()
		with rc_context({"svg.fonttype": "none", "text.hinting": "none"}):
			figure.savefig(buffer, format=format, dpi=self._dpi, facecolor="white")

		return buffer.getvalue()
