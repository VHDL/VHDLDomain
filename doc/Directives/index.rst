.. _DIR:

Directives
##########

A directive describes an object of a design read into the domain (see :ref:`CONFIG`): a design, a library, or a
design unit - entity, package, context, configuration. ``vhdl:design`` and ``vhdl:library`` also set the design and
library, which the following directives and references of the document are in, until the next one.

.. contents:: Table of Contents
   :local:


.. _DIR/design:

vhdl:design
***********

.. rst:directive:: .. vhdl:design:: name

   Describe a design: its target and index entry, and the content as the design's description.

   The argument is the design's name, a key of ``vhdl_designs``. Every directive and reference following it in the
   document is in this design. Placed above a page's title, its target is the title, as a label is.

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

   Describe an entity: its generics (name, type, default value, documentation), its ports (name, mode, type, default
   value, documentation) and its architectures.

   .. code-block:: rst

      .. vhdl:entity:: lib_Utilities.Counter

         The counter is used by the debouncer.

   Refer to its parts by ``:vhdl:generic:`Counter.BITS```, ``:vhdl:port:`Counter.Clock``` and
   ``:vhdl:arch:`Counter.rtl```.


.. _DIR/package:

vhdl:package
============

.. rst:directive:: .. vhdl:package:: [library.]name

   Describe a package: its generics, and - in declaration order - its types, subtypes, constants (also deferred ones),
   functions and procedures.

   .. code-block:: rst

      .. vhdl:package:: lib_Utilities.Utilities_pkg

   Refer to its declarations by ``:vhdl:type:`Utilities_pkg.freq```, ``:vhdl:const:`IS_SIMULATION``` or
   ``:vhdl:func:`to_index(natural, positive)```. A subprogram's qualified name ends in its signature, the type marks of
   its parameters, so overloads are told apart.


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
