.. _DIR:

Directives
##########

A directive describes an object of a design read into the domain (see :ref:`CONFIG`): a design, a library, or a
design unit - entity, package, context, configuration. ``vhdl:design`` and ``vhdl:library`` also set the design and
library, which the following directives and references of the document are in, until the next one. ``vhdl:symbol``
draws an entity's or a component's interface symbol.

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
its documentation comment - without the comment markers ``--``, parsed as reStructuredText -, the directive's content,
and its public interface. The interface's parts are objects of the domain too, which the roles refer to.

Types, default values and parameter subtypes are written as VHDL by pyVHDLModel's writer; an element the writer can't
write yet is written by its name and warned about (warning type ``vhdl.writer``).

Every design-unit directive takes these options:

.. rst:directive:option:: design: name
   :noindex:

   The design the unit is in. Default: the current design.

.. rst:directive:option:: no-index
   :noindex:

   Describe the unit without targets and index entries - e.g. a second description of the same unit.


.. _DIR/entity:

vhdl:entity
===========

.. rst:directive:: .. vhdl:entity:: [library.]name

   Describe an entity: its generics, its ports and its architectures.

   The generics and ports are the fields *Generics* and *Ports*, as Sphinx writes a Python function's parameters: per
   declaration its names in bold, its subtype - a port's with the mode -, its default value, and its documentation
   comment after a dash. A declaration with several names, e.g. ``Q0, Q1 : out std_logic``, is one item. A generic
   type, package or subprogram shows its kind: ``type``, ``package``, ``function`` or ``procedure``.

   .. code-block:: rst

      .. vhdl:entity:: lib_Utilities.Counter

         The counter is used by the debouncer.

   Refer to its parts by ``:vhdl:generic:`Counter.BITS```, ``:vhdl:port:`Counter.Clock``` and
   ``:vhdl:arch:`Counter.rtl```.


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
          range <>) of T_BCD``. A record type has the field *Elements*, a physical type the field *Units*.
      * - Constant, signal, shared variable
        - A description per name: the subtype and the value - a constant's, a signal's default value. A deferred
          constant has no value in the package; its signature starts with ``deferred constant``.
      * - Component
        - The field *Entity*, referring to the entity of the same name in the package's library, if pyVHDLModel bound
          the component to it, and the fields *Generics* and *Ports*, as an entity's.
      * - Function, procedure
        - The parameters - with their mode, if the declaration gives one, and their default values - and a function's
          return type. If a parameter is documented, the field *Parameters*.

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
