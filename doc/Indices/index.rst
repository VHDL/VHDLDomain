.. _INDEX:

Indices
#######

The domain creates an index page per kind of object: it lists the described objects - not every object of the
designs -, grouped by the first letter of their name, each linking to its description. An entry names where the object
is: the library of a design unit, the library and design unit of a declaration - preceded by the design, if the
documentation describes several. A subprogram's entry shows its signature, so its overloads are told apart.

.. list-table::
   :header-rows: 1

   * - Index
     - Lists
     - Reference
   * - Entity Index
     - entities
     - ``:ref:`vhdl-entities```
   * - Package Index
     - packages
     - ``:ref:`vhdl-packages```
   * - Subprogram Index
     - functions and procedures
     - ``:ref:`vhdl-subprograms```
   * - Type Index
     - types and subtypes
     - ``:ref:`vhdl-types```

An index can be listed in a table of contents by its name, e.g. ``vhdl-entities``:

.. code-block:: rst

   .. toctree::

      Entities <vhdl-entities>
      Subprograms <vhdl-subprograms>
