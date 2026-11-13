.. _NEWS:

News
####

See :gh:`VHDLDomain Release Pages <VHDL/VHDLDomain/releases>` for detail release notes on every release.


Version 0.3.0 (2026)
********************

.. topic:: :gh:`v0.3.0 - unreleased <VHDL/VHDLDomain/releases/v0.3.0>`

   .. rubric:: Changes

   * New package ``VHDLDomain.Symbol``: a format-independent interface symbol (parameters, pin groups, clock/reset
     pins, buses, low-active pins) with renderers for SVG, TikZ and - with the new extra ``diagram`` (matplotlib) - PNG.
   * New directive ``vhdl:symbol``: an entity's or a component's interface symbol, as SVG in HTML and TikZ in LaTeX.
   * ``vhdl:entity`` and ``vhdl:package`` write generics and ports as fields, as Sphinx writes a Python function's
     parameters, instead of tables.
   * ``vhdl:package`` describes signals, shared variables and components (roles ``:vhdl:sig:``, ``:vhdl:var:``,
     ``:vhdl:comp:``); a type's or subtype's definition as pyVHDLModel's writer writes it, a record's elements, a
     physical type's units, a constant's value, and a subprogram's parameter modes, default values and documentation.
     A deferred constant is marked ``deferred constant``; a component refers to the entity it is bound to.
   * A generic subprogram's signature names its generics, as Python's type parameters; its description has the field
     *Generics*.
   * ``vhdl:package`` describes a protected type's methods, in the type's description.
   * New configuration values ``vhdl_architectures`` and ``vhdl_architecture_descriptions``, and options
     ``:architectures:`` and ``:architecture-descriptions:`` of ``vhdl:entity``: which architectures an entity lists -
     always, only several, never -, with or without their documentation.

   .. rubric:: Documentation

   * The StopWatch example is documented again, where pyGHDL is installed; the entity ``Counter`` and the packages
     show their VHDL source and the directive next to the output.


Version 0.2.0 (2026)
********************

.. topic:: :gh:`v0.2.0 - 30.10.2026 <VHDL/VHDLDomain/releases/v0.2.0>`

   .. rubric:: Changes

   * The domain ``vhdl`` is rebuilt on pyVHDLModel: objects, references by qualified name or a part of it, the
     directives ``vhdl:design`` and ``vhdl:library``, and design-unit directives for entities, packages, contexts and
     configurations.
   * Indices of the described entities, packages, subprograms and types.
   * Generated pages: a page per library and design unit of a design.
   * pyTooling 10.1, pyTooling.Sphinx 1.0 and pyVHDLModel 0.40 are required; Python 3.12 to 3.15 are supported.

   .. rubric:: Documentation

   * The documentation is built with the ReadTheDocs theme and pyTooling.Sphinx.


Version 0.x (2023)
******************

.. topic:: Initial Implementation of a VHDL Domain (Jan. 2023)

   * Connecting pyGHDL.dom, pyVHDLModel and Sphinx with this extension.
