

Configuration
#############

The following configuration options can be set in :file:`conf.py`.

designs
*******

``designs`` is a dictionary of VHDL designs. The key defines the design name and the value is a
:py:class:`~pathlib.Path` object for the root directory of the design.

.. code-block:: Python

   vhdl_designs = {
     "StopWatch": Path("StopWatch/src"),
   }
