.. include:: shields.inc

.. image:: _static/logo.svg
   :height: 90 px
   :align: center
   :target: https://GitHub.com/vhdl/VHDLDomain

.. raw:: html

    <br>

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:VHDLDomain-github| |SHIELD:svg:VHDLDomain-src-license| |SHIELD:svg:VHDLDomain-ghp-doc| |SHIELD:svg:VHDLDomain-doc-license| |SHIELD:svg:VHDLDomain-gitter|
   |  |SHIELD:svg:VHDLDomain-pypi-tag| |SHIELD:svg:VHDLDomain-pypi-status| |SHIELD:svg:VHDLDomain-pypi-python|
   |  |SHIELD:svg:VHDLDomain-gha-test| |SHIELD:svg:VHDLDomain-lib-status| |SHIELD:svg:VHDLDomain-codacy-quality| |SHIELD:svg:VHDLDomain-codacy-coverage| |SHIELD:svg:VHDLDomain-codecov-coverage|

.. Disabled shields: |SHIELD:svg:VHDLDomain-lib-dep| |SHIELD:svg:VHDLDomain-lib-rank|

.. only:: latex

   |SHIELD:png:VHDLDomain-github| |SHIELD:png:VHDLDomain-src-license| |SHIELD:png:VHDLDomain-ghp-doc| |SHIELD:png:VHDLDomain-doc-license| |SHIELD:svg:VHDLDomain-gitter|
   |SHIELD:png:VHDLDomain-pypi-tag| |SHIELD:png:VHDLDomain-pypi-status| |SHIELD:png:VHDLDomain-pypi-python|
   |SHIELD:png:VHDLDomain-gha-test| |SHIELD:png:VHDLDomain-lib-status| |SHIELD:png:VHDLDomain-codacy-quality| |SHIELD:png:VHDLDomain-codacy-coverage| |SHIELD:png:VHDLDomain-codecov-coverage|

.. Disabled shields: |SHIELD:png:VHDLDomain-lib-dep| |SHIELD:png:VHDLDomain-lib-rank|

The VHDLDomain Documentation
############################

A Sphinx domain providing VHDL language support.


.. _goals:

Main Goals
**********

This sphinx extension adds a new language domain to Sphinx. It allows the documentation of VHDL source files.


.. _usecase:

Use Cases
*********

TBD


.. _news:

News
****

.. only:: html

   Jan. 2023 - Dependency, Hierarchy, Compile Order Analysis
   =========================================================

.. only:: latex

   .. rubric:: Dependency, Hierarchy, Compile Order Analysis

* Connecting pyGHDL.dom, pyVHDLModel and Sphinx with this extension.


.. _contributors:

Contributors
************

* `Patrick Lehmann <https://GitHub.com/Paebbels>`__ (Maintainer)
* `and more... <https://GitHub.com/VHDL/VHDLDomain/graphs/contributors>`__


License
*******

.. only:: html

   This Python package (source code) is licensed under `Apache License 2.0 <Code-License.html>`__. |br|
   The accompanying documentation is licensed under `Creative Commons - Attribution 4.0 (CC-BY 4.0) <Doc-License.html>`__.

.. only:: latex

   This Python package (source code) is licensed under **Apache License 2.0**. |br|
   The accompanying documentation is licensed under **Creative Commons - Attribution 4.0 (CC-BY 4.0)**.

------------------------------------

.. |docdate| date:: %d.%b %Y - %H:%M

.. only:: html

   This document was generated on |docdate|.


.. #toctree::
   :hidden:

   Used as a layer of EDA² ➚ <https://edaa-org.github.io/>


.. toctree::
   :caption: Introduction
   :hidden:

   GettingStarted
   Installation
   Dependency


.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Main Documentation
   :hidden:

   Directives/index
   Roles/index
   Indices/index

.. raw:: latex

   \part{Examples}

.. toctree::
   :caption: Examples
   :hidden:

   StopWatch/index
   Components <vhdl-compindex>
   Packages <vhdl-packindex>
   Subprograms <vhdl-subindex>
   Types <vhdl-typeindex>

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   VHDLDomain/VHDLDomain
   Unittest Report ➚ <unittests/index>
   Coverage Report ➚ <coverage/index>
   Static Type Check Report ➚ <typing/index>


.. raw:: latex


   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   ChangeLog/index
   License
   Doc-License
   Glossary
   genindex
   Python Module Index <modindex>
   TODO
