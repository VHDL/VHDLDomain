.. _CONFIG:

Configuration
#############

The following configuration values can be set in :file:`conf.py`.

.. contents:: Table of Contents
   :local:


.. _CONFIG/designs:

vhdl_designs
************

The designs the documentation describes, by name. A design is read when the builder is initialized: its source files
are parsed by `pyGHDL.dom <https://ghdl.github.io/ghdl/pyGHDL/pyGHDL.dom.html>`__ - the frontend keeping the comments
a documentation is extracted from - into a :class:`pyVHDLModel.Design`, which is analyzed then.

``directory``
  The directory of the source files, relative to the Sphinx source directory. Default: ``.``.
``libraries``
  The source files by library name, in the order they are parsed; a file is relative to ``directory``, and may be a
  glob pattern, whose matches are added sorted.

.. code-block:: Python

   vhdl_designs = {
     "StopWatch": {
       "directory": "../examples/StopWatch",
       "libraries": {
         "lib_Utilities": ["Utilities.pkg.vhdl", "Utilities.ctx.vhdl", "Counter.vhdl", "*_Bits.vhdl", "Debouncer.vhdl"],
         "lib_StopWatch": ["StopWatch.pkg.vhdl", "StopWatch.ctx.vhdl", "seg7_*.vhdl", "StopWatch.vhdl"],
       },
     },
   }

A design, which can't be read - a malformed entry, a missing file, pyGHDL not installed -, is logged as an error;
the build goes on, and a directive describing the design warns on its own.

.. rubric:: Designs read by another frontend

A design built by other means - another frontend, or by hand - is added by a handler of Sphinx' ``builder-inited``
event in :file:`conf.py`, with :meth:`~VHDLDomain.VHDLDomain.AddDesign`:

.. code-block:: Python

   def addDesigns(app):
     app.env.get_domain("vhdl").AddDesign("Demo", buildDemoDesign())

   def setup(app):
     app.connect("builder-inited", addDesigns)
