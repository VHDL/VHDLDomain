.. _EX/StopWatch:

StopWatch
#########

.. vhdl:design:: StopWatch

   A stop watch counting seconds and minutes on a 7-segment display.

The example design :file:`examples/StopWatch` is read by pyGHDL.dom (see :ref:`CONFIG`); each of its design units is
described by a directive (see :ref:`DIR`). The entity :vhdl:ent:`Counter` shows a directive's output together with its
input: the VHDL source, whose comments document the entity, its generics and its ports, and the directive.

lib_Utilities
*************

.. vhdl:library:: lib_Utilities

.. vhdl:package:: Utilities_pkg

.. vhdl:context:: Utilities_ctx

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:entity:: Counter

   .. tab-item:: VHDL source

      .. literalinclude:: ../../examples/StopWatch/Counter.vhdl
         :language: VHDL
         :tab-width: 2
         :start-at: -- A generic implementation of an up-counting counter.
         :end-at: end entity;

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:library:: lib_Utilities

         .. vhdl:entity:: Counter

.. vhdl:entity:: Debouncer

.. vhdl:entity:: sync_Bits


lib_StopWatch
*************

.. vhdl:library:: lib_StopWatch

.. vhdl:package:: StopWatch_pkg

.. vhdl:context:: StopWatch_ctx

.. vhdl:entity:: seg7_Encoder

.. vhdl:entity:: seg7_Display

.. vhdl:configuration:: seg7_Display_cfg

.. vhdl:entity:: StopWatch

.. vhdl:entity:: toplevel
