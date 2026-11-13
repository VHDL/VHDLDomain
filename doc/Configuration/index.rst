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
``pages``
  Optional, the document name the design's pages are generated below, e.g. ``"designs/StopWatch"``: a page per
  library and per design unit (see :ref:`CONFIG/pages`).

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

.. _CONFIG/pages:

.. rubric:: Generated pages

A design declared with ``pages`` gets a generated page per library - e.g. ``designs/StopWatch/lib_Utilities`` - and
per context, entity, package and configuration - e.g. ``designs/StopWatch/lib_Utilities/Counter``. A page has no
source file: it is written as reStructuredText, a title and the directive describing the object, so it shows the same
description, objects and index entries as a hand-written directive. A directive describing an object of a generated
page again is warned about as a duplicate. The predefined libraries ``std`` and ``ieee`` get no pages.

The design's :rst:dir:`vhdl:design` lists the library pages in a hidden table of contents, and a library page its
units' pages, so the pages are below the design's document in the navigation:

.. code-block:: rst

   StopWatch
   #########

   .. vhdl:design:: StopWatch

      A stop watch counting seconds and minutes on a 7-segment display.


.. rubric:: Designs read by another frontend

A design built by other means - another frontend, or by hand - is added by a handler of Sphinx' ``builder-inited``
event in :file:`conf.py`, with :meth:`~VHDLDomain.VHDLDomain.AddDesign`:

.. code-block:: Python

   def addDesigns(app):
     app.env.get_domain("vhdl").AddDesign("Demo", buildDemoDesign(), pages="designs/Demo")

   def setup(app):
     app.connect("builder-inited", addDesigns)


.. _CONFIG/architectures:

vhdl_architectures
******************

Which entities :rst:dir:`vhdl:entity` lists the architectures of; option :rst:dir:`vhdl:entity:architectures`
overrides it per entity.

``"always"``
  Every entity lists its architectures. Default.
``"multiple"``
  Only an entity with more than one architecture lists them, e.g. a testbench with an architecture per test.
``"never"``
  No entity lists its architectures.

An architecture which isn't listed is no object of the domain: :rst:role:`vhdl:arch` can't refer to it. Another value
ends the build with a configuration error.

.. code-block:: Python

   vhdl_architectures = "multiple"


.. _CONFIG/architecture-descriptions:

vhdl_architecture_descriptions
******************************

Whether a listed architecture shows its documentation comment: ``"show"`` (default) or ``"hide"`` - the
architecture's declaration only, e.g. ``architecture rtl of Counter``. Option
:rst:dir:`vhdl:entity:architecture-descriptions` overrides it per entity. Another value ends the build with a
configuration error.

.. code-block:: Python

   vhdl_architecture_descriptions = "hide"


.. _CONFIG/style:

vhdl_style
**********

The style of the interface lists - an entity's generics and ports, a record's elements, a subprogram's parameters -
of :rst:dir:`vhdl:entity` and :rst:dir:`vhdl:package`; option :rst:dir:`vhdl:entity:style` overrides it per unit.

``"auto"``
  The domain chooses the style: ``"list"``. Default.
``"list"``
  A field per list, an item per declaration, as Sphinx writes a Python function's parameters.
``"table"``
  A table per list - not supported yet: a unit is written as ``"list"``, and warned about.

Another value ends the build with a configuration error.

.. code-block:: Python

   vhdl_style = "list"


.. _CONFIG/add-library-names:

vhdl_add_library_names
**********************

Whether a design unit's signature names its library, as Sphinx' ``add_module_names`` names a Python class' module:
``False`` (default) - ``entity Counter`` - or ``True`` - ``entity lib_Utilities.Counter``. The declarations of a
package and the architectures of an entity are named without library and unit, as a Python class' methods.

.. code-block:: Python

   vhdl_add_library_names = True


.. _CONFIG/undoc-members:

vhdl_undoc_members
******************

Whether :rst:dir:`vhdl:package` describes the declarations - and a protected type's methods - without documentation
comment too: ``True`` (default) or ``False`` - only documented declarations are described, as Sphinx' autodoc does
without ``undoc-members``. Options :rst:dir:`vhdl:package:undoc-members` and :rst:dir:`vhdl:package:no-undoc-members`
override it per package. A declaration not described is no object of the domain: a role can't refer to it, and a type
mark naming it isn't linked.

.. code-block:: Python

   vhdl_undoc_members = False


.. _CONFIG/reference-popups:

vhdl_reference_popups
*********************

Whether a reference to a declaration of a package shows the declaration in a popup, in HTML (see :ref:`ROLE/popups`):
``True`` (default) or ``False`` - the reference's title is the declaration's signature then, and the domain adds no
style sheet to the pages.

.. code-block:: Python

   vhdl_reference_popups = False
