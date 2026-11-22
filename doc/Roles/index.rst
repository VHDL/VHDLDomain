.. _ROLE:

Roles
#####

A role refers to an object a directive described, by the object's qualified name or by a part of it ending with the
object's name:

* An object's qualified name starts with its design and library, e.g. ``StopWatch.lib_StopWatch.Counter``.
* ``lib_StopWatch.Counter`` and ``Counter`` name the same entity, as long as no other entity has that name.
* A name matching several objects is resolved in the design and library current where the reference is written -
  set by :rst:dir:`vhdl:design` and :rst:dir:`vhdl:library` -; otherwise it is warned about, and the reference is
  shown as text.
* A subprogram's name may end in its signature, the type marks of its parameters: ``to_index(natural, positive)``.
  Without a signature, a subprogram with overloads is ambiguous.
* VHDL identifiers are case-insensitive, so are the names.
* A leading ``~`` shows only the object's name: ``:vhdl:ent:`~lib_StopWatch.Counter``` shows ``Counter``.

.. code-block:: rst

   The entity :vhdl:ent:`Counter` counts clock cycles, see :vhdl:func:`Utilities.to_index(natural, positive)`.

.. contents:: Table of Contents
   :local:


Design and library
******************

.. rst:role:: vhdl:design

   Refer to a design.

.. rst:role:: vhdl:lib

   Refer to a library.


Design units
************

.. rst:role:: vhdl:ctx

   Refer to a context.

.. rst:role:: vhdl:ent

   Refer to an entity.

.. rst:role:: vhdl:arch

   Refer to an architecture, by the entity's name and the architecture's: ``Counter.rtl``.

.. rst:role:: vhdl:pack

   Refer to a package.

.. rst:role:: vhdl:config

   Refer to a configuration.


Declarations
************

.. rst:role:: vhdl:type

   Refer to a type or subtype, e.g. ``StopWatch_pkg.T_STATE``.

.. rst:role:: vhdl:const

   Refer to a constant.

.. rst:role:: vhdl:sig

   Refer to a signal.

.. rst:role:: vhdl:var

   Refer to a shared variable.

.. rst:role:: vhdl:comp

   Refer to a component, e.g. ``StopWatch_pkg.seg7_Encoder``.

.. rst:role:: vhdl:func

   Refer to a function, optionally with its signature. A method of a protected type is named after the type, e.g.
   ``T_ERROR_COUNTER.Errors``.

.. rst:role:: vhdl:proc

   Refer to a procedure, optionally with its signature, e.g. ``T_ERROR_COUNTER.Increment``.

.. rst:role:: vhdl:generic

   Refer to a generic, by the entity's or package's name and the generic's: ``Counter.BITS``.

.. rst:role:: vhdl:port

   Refer to a port, by the entity's name and the port's: ``Counter.Clock``.
