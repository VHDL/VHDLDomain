.. _DIR:

Directives
##########

A directive describes an object of a design read into the domain (see :ref:`CONFIG`). ``vhdl:design`` and
``vhdl:library`` also set the design and library, which the following directives and references of the document are
in, until the next one.

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
