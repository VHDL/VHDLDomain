.. _EX/StopWatch/graphs:

StopWatch Graphs
################

.. vhdl:design:: StopWatch
   :no-index:

The graphs of the :ref:`StopWatch example <EX/StopWatch>`, drawn by the graph directives (see :ref:`DIR/graphs`): each
picture next to the reStructuredText of its directive.


Hierarchy
*********

The whole hierarchy: the top-level ``toplevel``, its architecture, and the entities it instantiates, down to the
counters.

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:hierarchy::

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:hierarchy::

The entities below ``StopWatch``, as figure with a caption, from left to right:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:hierarchy:: lib_StopWatch.StopWatch
         :direction: left-to-right
         :caption: The entities below ``StopWatch``.

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:hierarchy:: lib_StopWatch.StopWatch
            :direction: left-to-right
            :caption: The entities below ``StopWatch``.

The entities using ``Counter``, as PNG image:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:hierarchy:: lib_Utilities.Counter
         :follow: inbound
         :format: png

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:hierarchy:: lib_Utilities.Counter
            :follow: inbound
            :format: png


Dependencies
************

The design units of ``lib_Utilities``:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:dependencies::
         :libraries: lib_Utilities

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:dependencies::
            :libraries: lib_Utilities

What the architecture of ``toplevel`` uses directly, from left to right:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:dependencies:: lib_StopWatch.toplevel(rtl)
         :depth: 1
         :direction: left-to-right

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:dependencies:: lib_StopWatch.toplevel(rtl)
            :depth: 1
            :direction: left-to-right

What the entity ``Counter`` references, with its library and the predefined libraries ``std`` and ``ieee``:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:dependencies:: lib_Utilities.Counter
         :depth: 1
         :kinds: library, package, entity
         :predefined:

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:dependencies:: lib_Utilities.Counter
            :depth: 1
            :kinds: library, package, entity
            :predefined:


Compile Order
*************

The source files in compile order: a file below the files compiled before it.

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:compile-order::

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:compile-order::

The files compiled before :file:`seg7_Display.vhdl`:

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:compile-order:: seg7_Display.vhdl

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:compile-order:: seg7_Display.vhdl
