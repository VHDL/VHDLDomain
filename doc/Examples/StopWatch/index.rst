.. _EX/StopWatch:

StopWatch
#########

.. vhdl:design:: StopWatch

   A stop watch counting seconds and minutes on a 7-segment display.

The example design :file:`examples/StopWatch` is read by pyGHDL.dom (see :ref:`CONFIG`); each of its design units is
described by a directive (see :ref:`DIR`). The packages :vhdl:pack:`Utilities_pkg` and :vhdl:pack:`StopWatch_pkg`,
the context :vhdl:ctx:`Utilities_ctx` and the entity :vhdl:ent:`Counter` show a directive's output together with its
input: the VHDL source, whose comments document the unit and its declarations, generics and ports, and the directive.
A documentation comment is reStructuredText: :vhdl:pack:`Utilities_pkg`, :vhdl:ent:`Counter` and the contexts use
emphasis, literals, a bullet list and a ``.. seealso::`` referring to other units by the roles of the domain.

The documentation's :file:`conf.py` sets :ref:`vhdl_architectures = "multiple" <CONFIG/architectures>`: only
:vhdl:ent:`Counter` - with an architecture for synthesis and one for simulation - lists its architectures.

lib_Utilities
*************

.. vhdl:library:: lib_Utilities

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:package:: Utilities_pkg

   .. tab-item:: VHDL source

      .. literalinclude:: ../../../examples/StopWatch/Utilities.pkg.vhdl
         :language: VHDL
         :tab-width: 2
         :start-at: -- Useful utility functions and types.
         :end-at: end package;

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:library:: lib_Utilities

         .. vhdl:package:: Utilities_pkg

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:context:: Utilities_ctx

   .. tab-item:: VHDL source

      .. literalinclude:: ../../../examples/StopWatch/Utilities.ctx.vhdl
         :language: VHDL
         :tab-width: 2
         :start-at: -- A context for the users of ``lib_Utilities``.
         :end-at: end context;

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:library:: lib_Utilities

         .. vhdl:context:: Utilities_ctx

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:entity:: Counter

   .. tab-item:: VHDL source

      .. literalinclude:: ../../../examples/StopWatch/Counter.vhdl
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

.. tab-set::

   .. tab-item:: Rendering

      .. vhdl:package:: StopWatch_pkg

   .. tab-item:: VHDL source

      .. literalinclude:: ../../../examples/StopWatch/StopWatch.pkg.vhdl
         :language: VHDL
         :tab-width: 2
         :start-at: -- Package with stop watch specific types.
         :end-at: end package;

   .. tab-item:: reStructuredText

      .. code-block:: rst

         .. vhdl:library:: lib_StopWatch

         .. vhdl:package:: StopWatch_pkg

.. vhdl:context:: StopWatch_ctx

.. vhdl:entity:: seg7_Encoder

.. vhdl:entity:: seg7_Display

.. vhdl:configuration:: seg7_Display_cfg

.. vhdl:entity:: StopWatch

.. vhdl:entity:: toplevel
