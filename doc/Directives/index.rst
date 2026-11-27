.. _DIR:

Directives
##########

A directive describes an object of a design read into the domain (see :ref:`CONFIG`): a design, a library, or a
design unit - entity, package, context, configuration. ``vhdl:design`` and ``vhdl:library`` also set the design and
library, which the following directives and references of the document are in, until the next one. ``vhdl:symbol``
draws an entity's or a component's interface symbol; ``vhdl:dependencies``, ``vhdl:compile-order`` and
``vhdl:hierarchy`` draw a design's graphs (see :ref:`DIR/graphs`).

.. contents:: Table of Contents
   :local:


.. _DIR/design:

vhdl:design
***********

.. rst:directive:: .. vhdl:design:: name

   Describe a design: its target and index entry, and the content as the design's description.

   The argument is the design's name, a key of ``vhdl_designs``. Every directive and reference following it in the
   document is in this design. Placed above a page's title, its target is the title, as a label is. A design with
   generated pages lists its library pages in a hidden table of contents (see :ref:`CONFIG/pages`).

   .. rst:directive:option:: no-index

      Make the design the current one, without a target and index entry - e.g. on the other pages of a design.

   .. code-block:: rst

      .. vhdl:design:: StopWatch

         A stop watch with a 7-segment display.


.. _DIR/library:

vhdl:library
************

.. rst:directive:: .. vhdl:library:: name

   Describe a library: its target and index entry, its documentation, the content, and a table of the library's
   design units - each name referring to the unit's description, if there is one.

   The argument is the library's name. Every directive and reference following it in the document is in this library.

   .. rst:directive:option:: design: name

      The design the library is in. Default: the current design.

   .. rst:directive:option:: no-index

      Make the library the current one, without describing it.

   .. code-block:: rst

      .. vhdl:library:: lib_StopWatch
         :design: StopWatch


.. _DIR/units:

Design units
************

A design-unit directive's argument is the unit's name, optionally preceded by its library, e.g.
``lib_Utilities.Counter``; without a library, the unit is in the current one. The unit is described by its declaration,
its documentation comment - without the comment markers ``--``, parsed as reStructuredText or Markdown, see option
``doc-syntax`` below -, the directive's content, and its public interface. The interface's parts are objects of the
domain too, which the roles refer to. The declaration's signature names the library as well, if
:ref:`CONFIG/add-library-names` is set.

Types, default values and parameter subtypes are written as VHDL by pyVHDLModel's writer; an element the writer can't
write yet is written by its name and warned about (warning type ``vhdl.writer``). A type mark - e.g. ``T_BCD`` of
``array (natural range <>) of T_BCD``, or ``unsigned`` of ``unsigned(BITS - 1 downto 0)`` - refers to the type's
description, as :rst:role:`vhdl:type` does, in the unit's design and library - in HTML with the type's declaration as
popup (see :ref:`ROLE/popups`). A type mark of an undescribed type, e.g. ``std_logic``, or of several described types
stays text, without a warning.

Every design-unit directive takes these options:

.. rst:directive:option:: design: name
   :noindex:

   The design the unit is in. Default: the current design.

.. rst:directive:option:: no-index
   :noindex:

   Describe the unit without targets and index entries - e.g. a second description of the same unit.

.. rst:directive:option:: doc-syntax: rest | markdown | gfm
   :noindex:

   The syntax of the unit's documentation comments - and of its generics', ports' and declarations' comments -:
   reStructuredText, CommonMark or GitHub-flavoured Markdown. Default: :ref:`CONFIG/doc-syntax`.


.. _DIR/entity:

vhdl:entity
===========

.. rst:directive:: .. vhdl:entity:: [library.]name

   Describe an entity: its generics, its ports and its architectures.

   The generics and ports are the fields *Generics* and *Ports*, as Sphinx writes a Python function's parameters: per
   declaration its names in bold, its subtype - a port's with the mode -, its default value, and its documentation
   comment after a dash. A declaration with several names, e.g. ``Q0, Q1 : out std_logic``, is one item. A generic
   type, package or subprogram shows its kind: ``type``, ``package``, ``function`` or ``procedure``.

   The architectures follow, each with its documentation comment - which and whether with documentation, set the
   options below.

   .. rst:directive:option:: architectures: always | multiple | never

      Which architectures to list: ``always`` all, ``multiple`` all if there are more than one - e.g. a testbench with
      an architecture per test -, ``never`` none. Default: :ref:`CONFIG/architectures`.

   .. rst:directive:option:: architecture-descriptions: show | hide

      Whether a listed architecture shows its documentation comment, or its declaration only. Default:
      :ref:`CONFIG/architecture-descriptions`.

   .. rst:directive:option:: style: auto | list | table

      The style of the generics and ports: ``list`` - fields, as described above -, ``auto`` - the domain chooses,
      ``list`` -, or ``table``, which isn't supported yet: it is warned about, and written as ``list``. Default:
      :ref:`CONFIG/style`.

   .. code-block:: rst

      .. vhdl:entity:: lib_Utilities.Counter
         :architectures: multiple

         The counter is used by the debouncer.

   Refer to its parts by ``:vhdl:generic:`Counter.BITS```, ``:vhdl:port:`Counter.Clock``` and
   ``:vhdl:arch:`Counter.rtl```; an architecture not listed is no object.


.. _DIR/package:

vhdl:package
============

.. rst:directive:: .. vhdl:package:: [library.]name

   Describe a package: its generics - the field *Generics*, as an entity's -, and - in declaration order - its
   declarations, each a description of its own with its documentation comment:

   .. list-table::
      :header-rows: 1
      :widths: 25 75

      * - Declaration
        - Description
      * - Type, subtype
        - The definition's first line, as pyVHDLModel's writer writes it, e.g. ``type T_BCD_Vector is array (natural
          range <>) of T_BCD``. A record type has the field *Elements*, a physical type the field *Units*. A protected
          type's methods are descriptions of their own in the type's description, as a Python class' methods; the
          protected type body isn't described.
      * - Constant, signal, shared variable
        - A description per name: the subtype and the value - a constant's, a signal's default value. A deferred
          constant has no value in the package; its signature starts with ``deferred constant``.
      * - Component
        - The field *Entity*, referring to the entity of the same name in the package's library, if pyVHDLModel bound
          the component to it, and the fields *Generics* and *Ports*, as an entity's.
      * - Function, procedure
        - The parameters - with their mode, if the declaration gives one, and their default values - and a function's
          return type. If a parameter is documented, the field *Parameters*. A generic subprogram (VHDL-2008) names its
          generics in brackets before the parameters, as Sphinx writes a Python function's type parameters, e.g.
          ``procedure swap[T_VALUE](A : inout T_VALUE, B : inout T_VALUE)``, and has the field *Generics*.

   .. rst:directive:option:: style: auto | list | table

      The style of the fields *Generics*, *Elements*, *Units*, *Ports* and *Parameters*, as
      :rst:dir:`vhdl:entity:style`. Default: :ref:`CONFIG/style`.

   .. rst:directive:option:: undoc-members

      Describe the declarations - and a protected type's methods - without documentation comment too. Default:
      :ref:`CONFIG/undoc-members`, on.

   .. rst:directive:option:: no-undoc-members

      Describe only the declarations - and methods - with a documentation comment.
      :rst:dir:`vhdl:package:undoc-members` wins over it, as in Sphinx' autodoc. The interface lists - generics, a
      record's elements, a physical type's units, a component's ports, a subprogram's parameters - are always complete.

   .. code-block:: rst

      .. vhdl:package:: lib_Utilities.Utilities_pkg

   Refer to its declarations by ``:vhdl:type:`Utilities_pkg.freq```, ``:vhdl:const:`IS_SIMULATION```,
   ``:vhdl:comp:`Debouncer``` or ``:vhdl:func:`to_index(natural, positive)```. A subprogram's qualified name ends in its
   signature, the type marks of its parameters, so overloads are told apart. A component's generics and ports are no
   objects of the domain: ``:vhdl:port:`Debouncer.Clock``` refers to the entity's port.


.. _DIR/context:

vhdl:context
============

.. rst:directive:: .. vhdl:context:: [library.]name

   Describe a context: its library clauses, use clauses and context references, in this order.

   .. code-block:: rst

      .. vhdl:context:: lib_Utilities.Utilities_ctx


.. _DIR/configuration:

vhdl:configuration
==================

.. rst:directive:: .. vhdl:configuration:: [library.]name

   Describe a configuration, and the entity it configures, referring to the entity's description.

   .. code-block:: rst

      .. vhdl:configuration:: lib_StopWatch.seg7_Display_cfg


.. _DIR/symbol:

vhdl:symbol
***********

.. rst:directive:: .. vhdl:symbol:: [library.]name

   Draw an entity's or a component's interface symbol: a box named as the unit, its generics as parameters in a box on
   top, and its ports as pins on the left and right edge.

   The argument names an entity as ``[library.]entity``, a component declared in a package as
   ``[library.]package.component``, or a component declared in an architecture as
   ``[library.]entity.architecture.component``. The name is looked up in the current library and - if its first part
   names a library - in that library; a name matching no unit or several units is warned about (warning type
   ``vhdl.symbol``). The symbol describes no object of the domain: it has no target and no index entry.

   .. rst:directive:option:: design: name

      The design the unit is in. Default: the current design.

   .. code-block:: rst

      .. vhdl:symbol:: lib_Utilities.Counter

      .. vhdl:symbol:: lib_StopWatch.StopWatch_pkg.seg7_Display


Parameters and pins
===================

Each identifier of a generic or port declaration becomes a parameter or pin of its own: ``a, b : in bit`` gives two
pins. A generic constant's parameter shows its subtype and default value, written as VHDL by pyVHDLModel's writer
(warning type ``vhdl.writer`` for what it can't write yet); a generic type, package, function or procedure shows its
VHDL keyword. A pin shows the port's subtype, or ``view`` and the name of the port's mode view. A pin's properties
follow from the port:

.. list-table::
   :header-rows: 1

   * - Property
     - Rule
   * - Side
     - Mode ``in`` - or no mode - on the left edge; ``out``, ``inout``, ``buffer``, ``linkage`` and a mode view on the
       right edge.
   * - Clock
     - The name is ``clk`` or ``clock``.
   * - Reset
     - The name is ``rst``, ``reset`` or ``reset_n``.
   * - Inverted (low-active)
     - The name ends in ``_n``.
   * - Bus
     - A constrained array or record subtype - as ``unsigned(BITS - 1 downto 0)`` -, a type mark of an array type of
       the libraries ``std`` and ``ieee`` - as ``std_logic_vector`` -, or a mode view.

Names are compared case-insensitively. The entity ``Counter`` of the StopWatch example gets the parameters ``MODULO``
and ``BITS``, the pins ``Clock`` (a clock), ``Reset`` (a reset) and ``Enable`` on the left edge, and ``Value`` (a bus)
and ``WrapAround`` on the right edge.


Output formats
==============

HTML
   An inline SVG picture.

LaTeX
   A TikZ picture; the LaTeX package ``tikz`` and the TikZ libraries the picture needs are loaded in the preamble.

Other builders, e.g. text
   A listing of the symbol: its name, a line per parameter and a line per pin with its side.


.. _DIR/graphs:

Graphs
******

pyVHDLModel analyzes a design into three graphs: the dependency graph of its libraries, design units and source files,
the compile-order graph of its source files, and the hierarchy graph of its entities and architectures. A graph
directive draws one of them - the whole graph, or a portion of it -, laid out in layers by pyTooling's
:class:`~pyTooling.Graph.Layout.Layered.LayeredLayout`: every edge points in the same direction, by default from top to
bottom. An edge points from a user to what it uses. A box is named as the design names its unit, e.g.
``lib_Utilities.Counter(rtl)``, and filled in the color of its kind:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Kind
     - Color
     - Name
   * - Library
     - grey
     - ``lib_Utilities``
   * - Context
     - violet
     - ``lib_StopWatch.StopWatch_ctx``
   * - Package
     - blue
     - ``lib_Utilities.Utilities_pkg``
   * - Package body
     - light blue
     - ``lib_Utilities.Utilities_pkg(body)``
   * - Entity
     - green
     - ``lib_Utilities.Counter``
   * - Architecture
     - orange
     - ``lib_Utilities.Counter(rtl)``
   * - Configuration
     - red
     - ``lib_StopWatch.seg7_Display_cfg``
   * - Source file
     - yellow
     - ``Counter.vhdl``

Lines, box outlines and the labels of boxes without color are drawn in the text color of the page, so a picture fits a
light and a dark theme alike. A picture describes no object of the domain: it has no target and no index entry. The
:ref:`StopWatch example <EX/StopWatch/graphs>` shows each directive's pictures.


.. _DIR/graphs/portion:

Portions
========

Without argument, a graph directive draws the whole graph. Its argument names the vertex a portion starts at: the
portion holds this vertex and the vertices reached from it, by following the edges up to ``depth`` times. An edge to a
vertex, which isn't drawn, is left out of the picture; the options select the vertices before the edges are followed,
so a portion doesn't reach through a left-out vertex. A name matching no vertex or several vertices, and a start vertex
left out by the options, are warned about (warning type ``vhdl.graph``).

Every graph directive takes these options:

.. rst:directive:option:: design: name
   :noindex:

   The design, whose graph is drawn. Default: the current design.

.. rst:directive:option:: depth: number
   :noindex:

   The number of edges followed from the start vertex; ``0`` draws the start vertex only. Default: as many as there
   are.

.. rst:directive:option:: follow: outbound | inbound | both
   :noindex:

   The edges followed from the start vertex: ``outbound`` to what the start uses, ``inbound`` back to what uses the
   start, or both. Default: ``outbound``.

.. rst:directive:option:: libraries: names
   :noindex:

   The libraries, whose vertices are drawn, separated by commas or spaces. A library, which isn't in the design, is
   warned about (warning type ``vhdl.library``). Default: every library.

.. rst:directive:option:: direction: top-to-bottom | bottom-to-top | left-to-right | right-to-left
   :noindex:

   The direction the edges point in, from layer to layer. Default: ``top-to-bottom``; ``bottom-to-top`` for
   ``vhdl:compile-order``.

.. rst:directive:option:: format: svg | png
   :noindex:

   The picture's format: ``svg`` is a vector picture, inline SVG in HTML and a TikZ picture in LaTeX; ``png`` is a PNG
   image in both, drawn by :term:`matplotlib` - installed by the extra ``diagram``; without it, the picture is a vector
   picture and warned about. Default: ``svg``.

.. rst:directive:option:: alt: text
   :noindex:

   The picture's alternative text: the SVG image's title, or the PNG image's ``alt`` text. Default: the graph's title
   and the design's name, e.g. ``Hierarchy of design StopWatch, from lib_StopWatch.toplevel``.

.. rst:directive:option:: caption: text
   :noindex:

   A caption: the picture becomes a figure with this caption.

.. rst:directive:option:: name: label
   :noindex:

   A label to refer to the picture - or to its figure - by :rst:role:`ref` or :rst:role:`numref`.


.. _DIR/dependencies:

vhdl:dependencies
=================

.. rst:directive:: .. vhdl:dependencies:: [name]

   Draw a design's dependency graph: an edge points from a design unit to what it references - a library, a package, a
   context, an entity it instantiates or implements.

   The argument names a library, a design unit as ``[library.]unit``, an architecture as ``[library.]entity(name)`` or
   a package body as ``[library.]package(body)``; without library, the unit is looked up in the current library too.

   .. rst:directive:option:: kinds: kinds

      The kinds of vertices drawn, separated by commas or spaces: ``library``, ``context``, ``package``,
      ``package-body``, ``entity``, ``architecture``, ``configuration`` and ``document`` (a source file). Default: the
      design units, every kind but ``library`` and ``document``.

   .. rst:directive:option:: predefined

      Draw the vertices of the predefined libraries ``std`` and ``ieee`` too.

   .. code-block:: rst

      .. vhdl:dependencies:: lib_StopWatch.toplevel(rtl)
         :depth: 1
         :direction: left-to-right


.. _DIR/compile-order:

vhdl:compile-order
==================

.. rst:directive:: .. vhdl:compile-order:: [file]

   Draw a design's compile-order graph: an edge points from a source file to a file compiled before it. Laid out from
   bottom to top by default, a file is drawn below the files compiled before it.

   The argument names a source file by its name or by the end of its path, e.g. ``Counter.vhdl`` or
   ``StopWatch/Counter.vhdl``.

   .. code-block:: rst

      .. vhdl:compile-order::
         :libraries: lib_Utilities


.. _DIR/hierarchy:

vhdl:hierarchy
==============

.. rst:directive:: .. vhdl:hierarchy:: [name]

   Draw a design's hierarchy graph: an edge points from an entity to its architectures, and from an architecture to the
   entities it instantiates.

   The argument names an entity as ``[library.]entity`` or an architecture as ``[library.]entity(name)``; without
   library, it is looked up in the current library too.

   .. code-block:: rst

      .. vhdl:hierarchy:: lib_StopWatch.toplevel
         :caption: The design hierarchy of the StopWatch.


Output formats
==============

HTML
   An inline SVG picture in a ``div`` of the classes ``vhdl`` and ``vhdl-graph``, or an ``img`` of the PNG image. A
   picture wider than the page's content scrolls horizontally.

LaTeX
   A TikZ picture, or the PNG image; a picture wider than the line is scaled down to the line width.

Other builders, e.g. text
   A listing of the graph: a line per vertex, followed by a line per edge to a vertex drawn.

A PNG image is named by a hash of its content, e.g. :file:`_images/vhdl-graph-<hash>.png`, and written only if no file
of that name exists: an unchanged picture is written once.


.. _DIR/css:

CSS classes
***********

A description is written as Sphinx writes a Python object's: an HTML ``dl`` with the classes ``vhdl`` and the object
type, e.g. ``<dl class="vhdl entity">``; its ``dt`` is the signature, its ``dd`` the content. A variant of the object
type adds a class ``vhdl-<variant>``, so a theme can shade each kind of object:

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Object type
     - Variant classes
     - Description of
   * - ``type``
     - ``vhdl-enumeration``, ``vhdl-integer``, ``vhdl-real``, ``vhdl-physical``, ``vhdl-array``, ``vhdl-record``,
       ``vhdl-access``, ``vhdl-file``, ``vhdl-protected``
     - The kind of type, e.g. ``<dl class="vhdl type vhdl-protected">``.
   * - ``constant``
     - ``vhdl-deferred``
     - A deferred constant.
   * - ``function``, ``procedure``
     - ``vhdl-generic``, ``vhdl-method``, ``vhdl-impure``
     - A generic subprogram, a method of a protected type, an impure function.

The other object types - ``entity``, ``architecture``, ``package``, ``context``, ``configuration``, ``subtype``,
``signal``, ``variable``, ``component`` - have no variants. The fields *Generics*, *Ports*, *Parameters*, *Elements* and
*Units* are a field list with the classes ``vhdl-interface`` and ``vhdl-<style>`` of the style of the interface lists,
e.g. ``vhdl-list`` (see :rst:dir:`vhdl:entity:style`); a library's table of design units has the classes ``vhdl``
and ``vhdl-library-units``. The classes of a reference's popup: see :ref:`ROLE/popups`.

This documentation adds the style sheet :file:`_static/css/vhdl.css` (``html_css_files`` in :file:`conf.py`) for the
theme ``sphinx_rtd_theme``; the examples (see :ref:`EX`) show it:

.. literalinclude:: ../_static/css/vhdl.css
   :language: CSS
