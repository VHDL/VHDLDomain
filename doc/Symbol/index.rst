.. _DATA/Symbol:

Interface Symbols
#################

An interface symbol is a picture of a design unit's interface: a box named as the unit, its parameters (VHDL generics)
in a dashed box on top, and its pins (VHDL ports) on the left and right edge. A pin's stub shows its type label, a bus
is drawn as a thick line, a clock input with a triangle and a low-active pin with an inversion circle.

The package :mod:`VHDLDomain.Symbol` describes a symbol in a data model, which knows nothing about VHDL and nothing
about the format drawing it. :class:`~VHDLDomain.Symbol.Layout.SymbolLayout` computes its geometry once; a renderer
translates the geometry into SVG, TikZ or - with :term:`matplotlib` - PNG.

.. contents:: Table of Contents
   :local:


.. _DATA/Symbol/Model:

Data Model
**********

A symbol has parameter groups holding parameters and pin groups holding pins. A group is a horizontal section of its
box: a named group starts with its name as a header line, a line separates two groups.

.. tree::

   - :class:`~VHDLDomain.Symbol.InterfaceSymbol`  | the symbol, e.g. an entity
     - :class:`~VHDLDomain.Symbol.ParameterGroup` | a section of the parameter box
       - :class:`~VHDLDomain.Symbol.Parameter`    | e.g. a generic
     - :class:`~VHDLDomain.Symbol.PinGroup`       | a section of the pin box
       - :class:`~VHDLDomain.Symbol.Pin`          | e.g. a port

Each element below the symbol derives from :class:`~VHDLDomain.Symbol.Element`, which holds its parent
(:attr:`~VHDLDomain.Symbol.Element.Parent`). An element is created with its parent (``parent=...``) and appends itself
to it, so groups and their elements keep the order they are created in.

.. inheritance-diagram:: VHDLDomain.Symbol.ParameterGroup
                         VHDLDomain.Symbol.Parameter
                         VHDLDomain.Symbol.PinGroup
                         VHDLDomain.Symbol.Pin
   :parts: 1


.. _DATA/Symbol/Model/InterfaceSymbol:

InterfaceSymbol
===============

The root of the model: the symbol's name, its parameter groups and its pin groups.

**Condensed definition of class** :class:`~VHDLDomain.Symbol.InterfaceSymbol`:

.. condensed-class:: VHDLDomain.Symbol.InterfaceSymbol


.. _DATA/Symbol/Model/Parameter:

ParameterGroup and Parameter
============================

A parameter group is a section of the parameter box, optionally named. A parameter is drawn as one line
``NAME : type := default``; the three parts of the parameters are aligned in columns. The type label and the default
value are text as written, e.g. ``log2(MODULO)``.

**Condensed definition of class** :class:`~VHDLDomain.Symbol.ParameterGroup`:

.. condensed-class:: VHDLDomain.Symbol.ParameterGroup

**Condensed definition of class** :class:`~VHDLDomain.Symbol.Parameter`:

.. condensed-class:: VHDLDomain.Symbol.Parameter


.. _DATA/Symbol/Model/Pin:

PinGroup and Pin
================

A pin group is a horizontal section of the pin box, optionally named; its pins sit on the left and right edge. A pin's
name is inside the box at the edge of its side, its type label outside, above its stub. How a pin is drawn follows from
its properties:

.. list-table::
   :header-rows: 1

   * - Property
     - Drawing
   * - :attr:`~VHDLDomain.Symbol.Pin.Side`
     - The edge of the box: :class:`~VHDLDomain.Symbol.PinSide`, e.g. ``Left`` for an input.
   * - :attr:`~VHDLDomain.Symbol.Pin.Kind`
     - The pin's role: :class:`~VHDLDomain.Symbol.PinKind`. A clock input has a triangle at the inner box edge.
   * - :attr:`~VHDLDomain.Symbol.Pin.IsBus`
     - A thick stub.
   * - :attr:`~VHDLDomain.Symbol.Pin.IsInverted`
     - An inversion circle between box edge and stub (low-active).

**Condensed definition of class** :class:`~VHDLDomain.Symbol.PinGroup`:

.. condensed-class:: VHDLDomain.Symbol.PinGroup

**Condensed definition of class** :class:`~VHDLDomain.Symbol.Pin`:

.. condensed-class:: VHDLDomain.Symbol.Pin


.. _DATA/Symbol/Layout:

Layout
******

:class:`~VHDLDomain.Symbol.Layout.SymbolLayout` places the symbol's name, its parameter box and its pin box on a
:class:`~pyTooling.Cartesian2D.Groups.Canvas2D` of drawable elements: rectangles, line segments, circles, polygons and
texts. Coordinates are points (1/72 inch), and all texts are set in a monospace font, so the layout knows each text's
width. Every renderer draws the same canvas, so the three formats show the same picture.

**Condensed definition of class** :class:`~VHDLDomain.Symbol.Layout.SymbolLayout`:

.. condensed-class:: VHDLDomain.Symbol.Layout.SymbolLayout


.. _DATA/Symbol/Renderers:

Renderers
*********

A renderer's ``Render(symbol)`` method takes a symbol and returns the picture in its format:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Renderer
     - Output
     - Use
   * - :class:`~VHDLDomain.Symbol.SVG.SVGRenderer`
     - SVG 1.1 text
     - HTML pages; lines and texts in ``currentColor``, texts stay selectable.
   * - :class:`~VHDLDomain.Symbol.TikZ.TikZRenderer`
     - A ``tikzpicture`` environment as text
     - LaTeX documents; texts in the document's typewriter font.
   * - :class:`~VHDLDomain.Symbol.Matplotlib.MatplotlibRenderer`
     - PNG, SVG or PDF file content as bytes
     - Images; needs :term:`matplotlib`, installed by the extra ``diagram``.

.. code-block:: Python

   from VHDLDomain.Symbol.Matplotlib import MatplotlibRenderer
   from VHDLDomain.Symbol.SVG        import SVGRenderer
   from VHDLDomain.Symbol.TikZ       import TikZRenderer

   svg =  SVGRenderer().Render(symbol)
   tikz = TikZRenderer().Render(symbol)
   png =  MatplotlibRenderer(dpi=192).Render(symbol, "png")


.. _DATA/Symbol/Renderers/SVG:

SVGRenderer
===========

The image is self-contained SVG 1.1 text without an XML declaration, so it can be written to a file or embedded into an
HTML page. Its ``width`` and ``height`` are the layout's size in points; a ``viewBox`` lets it scale.

**Condensed definition of class** :class:`~VHDLDomain.Symbol.SVG.SVGRenderer`:

.. condensed-class:: VHDLDomain.Symbol.SVG.SVGRenderer


.. _DATA/Symbol/Renderers/TikZ:

TikZRenderer
============

The picture is a complete ``tikzpicture`` environment; a LaTeX document loads the package ``tikz`` and the TikZ
libraries of :attr:`~VHDLDomain.Symbol.TikZ.TikZRenderer.TIKZ_LIBRARIES` in its preamble:

.. code-block:: Python

   tikzLibraries = ",".join(TikZRenderer.TIKZ_LIBRARIES)
   latex_elements = {
     "preamble": dedent(f"""\
       \\usepackage{{tikz}}
       \\usetikzlibrary{{{tikzLibraries}}}
     """),
   }

**Condensed definition of class** :class:`~VHDLDomain.Symbol.TikZ.TikZRenderer`:

.. condensed-class:: VHDLDomain.Symbol.TikZ.TikZRenderer


.. _DATA/Symbol/Renderers/Matplotlib:

MatplotlibRenderer
==================

The figure is as large as the layout, black on white. A PNG image has the resolution given by ``dpi``; at 144 dpi, one
point of the layout is two pixels. matplotlib is imported when a symbol is rendered, so a missing installation raises
:exc:`~pyTooling.Exceptions.MissingDependencyError` then.

**Condensed definition of class** :class:`~VHDLDomain.Symbol.Matplotlib.MatplotlibRenderer`:

.. condensed-class:: VHDLDomain.Symbol.Matplotlib.MatplotlibRenderer


.. _DATA/Symbol/Examples:

Examples
********

The symbols of three entities of the StopWatch example design (:file:`examples/StopWatch`) are built with the data
model in :file:`doc/Symbol/StopWatch.py`. The documentation build renders them with all three renderers. This is the
symbol of the entity ``Counter``:

.. literalinclude:: StopWatch.py
   :language: Python
   :tab-width: 2
   :pyobject: Counter


.. _DATA/Symbol/Examples/Counter:

Counter
=======

Two generics - one with a default value -, a clock input, a reset input, and a bus output.

.. literalinclude:: ../../examples/StopWatch/Counter.vhdl
   :language: VHDL
   :tab-width: 2
   :start-at: entity Counter is
   :end-at: end entity;

.. only:: html

   .. tab-set::

      .. tab-item:: SVG

         .. image:: Renderings/Counter.svg
            :alt: Interface symbol of entity Counter as SVG image.

      .. tab-item:: PNG

         .. image:: Renderings/Counter.png
            :alt: Interface symbol of entity Counter as PNG image.
            :scale: 50 %

      .. tab-item:: TikZ

         .. literalinclude:: Renderings/Counter.tikz
            :language: LaTeX

.. only:: latex

   .. rubric:: PNG image

   .. image:: Renderings/Counter.png
      :alt: Interface symbol of entity Counter as PNG image.

   .. rubric:: TikZ picture

   .. raw:: latex

      \resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%

   .. raw:: latex
      :file: Renderings/Counter.tikz

   .. raw:: latex

      }


.. _DATA/Symbol/Examples/seg7_Display:

seg7_Display
============

Three generics, a clock input, bus inputs - one of a user-defined array type -, and bus outputs.

.. literalinclude:: ../../examples/StopWatch/seg7_Display.vhdl
   :language: VHDL
   :tab-width: 2
   :start-at: entity seg7_Display is
   :end-at: end entity;

.. only:: html

   .. tab-set::

      .. tab-item:: SVG

         .. image:: Renderings/seg7_Display.svg
            :alt: Interface symbol of entity seg7_Display as SVG image.

      .. tab-item:: PNG

         .. image:: Renderings/seg7_Display.png
            :alt: Interface symbol of entity seg7_Display as PNG image.
            :scale: 50 %

      .. tab-item:: TikZ

         .. literalinclude:: Renderings/seg7_Display.tikz
            :language: LaTeX

.. only:: latex

   .. rubric:: PNG image

   .. image:: Renderings/seg7_Display.png
      :alt: Interface symbol of entity seg7_Display as PNG image.

   .. rubric:: TikZ picture

   .. raw:: latex

      \resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%

   .. raw:: latex
      :file: Renderings/seg7_Display.tikz

   .. raw:: latex

      }


.. _DATA/Symbol/Examples/toplevel:

toplevel
========

The board-level entity: one generic, low-active pins (``_n``) - an input and two bus outputs -, and a one-bit bus input.

.. literalinclude:: ../../examples/StopWatch/toplevel.vhdl
   :language: VHDL
   :tab-width: 2
   :start-at: entity toplevel is
   :end-at: end entity;

.. only:: html

   .. tab-set::

      .. tab-item:: SVG

         .. image:: Renderings/toplevel.svg
            :alt: Interface symbol of entity toplevel as SVG image.

      .. tab-item:: PNG

         .. image:: Renderings/toplevel.png
            :alt: Interface symbol of entity toplevel as PNG image.
            :scale: 50 %

      .. tab-item:: TikZ

         .. literalinclude:: Renderings/toplevel.tikz
            :language: LaTeX

.. only:: latex

   .. rubric:: PNG image

   .. image:: Renderings/toplevel.png
      :alt: Interface symbol of entity toplevel as PNG image.

   .. rubric:: TikZ picture

   .. raw:: latex

      \resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%

   .. raw:: latex
      :file: Renderings/toplevel.tikz

   .. raw:: latex

      }
