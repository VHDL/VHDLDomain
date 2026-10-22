# ==================================================================================================================== #
# __     ___   _ ____  _     ____                        _                                                             #
# \ \   / / | | |  _ \| |   |  _ \  ___  _ __ ___   __ _(_)_ __                                                        #
#  \ \ / /| |_| | | | | |   | | | |/ _ \| '_ ` _ \ / _` | | '_ \                                                       #
#   \ V / |  _  | |_| | |___| |_| | (_) | | | | | | (_| | | | | |                                                      #
#    \_/  |_| |_|____/|_____|____/ \___/|_| |_| |_|\__,_|_|_| |_|                                                      #
#                                                                                                                      #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
**A Sphinx domain providing VHDL language support.**

The domain ``vhdl`` documents VHDL designs from their model, a :class:`pyVHDLModel.Design`. The designs are declared
in :file:`conf.py` (see :mod:`VHDLDomain.Frontend`) and read when the builder is initialized; a directive describes a
design, a library or a design unit from the model, and a role refers to what a directive described.

.. code-block:: rst

   .. vhdl:design:: StopWatch

   .. vhdl:library:: lib_StopWatch

   The entity :vhdl:ent:`Counter` counts clock cycles.

.. rubric:: What it registers

* Directives: ``vhdl:design``, ``vhdl:library``, ``vhdl:context``, ``vhdl:entity``, ``vhdl:package``,
  ``vhdl:configuration``
* Roles: ``:vhdl:design:``, ``:vhdl:lib:``, ``:vhdl:ctx:``, ``:vhdl:ent:``, ``:vhdl:arch:``, ``:vhdl:pack:``,
  ``:vhdl:config:``, ``:vhdl:type:``, ``:vhdl:const:``, ``:vhdl:func:``, ``:vhdl:proc:``, ``:vhdl:generic:``,
  ``:vhdl:port:``
* Indices: ``vhdl-entities``, ``vhdl-packages``, ``vhdl-subprograms``, ``vhdl-types``
* Configuration value ``vhdl_designs``

.. rubric:: Names

An object's qualified name starts with its design and library, e.g. ``StopWatch.lib_StopWatch.Counter``; a reference
names it by the qualified name, or by a part of it ending with the object's name, e.g. ``lib_StopWatch.Counter`` or
``Counter``. A subprogram's name may end in its signature, the type marks of its parameters, e.g.
``Utilities.to_index(natural, positive)``. A name matching several objects - also a subprogram's overloads without a
signature - is resolved in the design and library of the last ``vhdl:design`` and ``vhdl:library`` before the
reference, otherwise it is warned about. VHDL identifiers are case-insensitive, so are the names.

.. admonition:: Copyright Information

   :copyright: Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany
   :copyright: Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
   :license: Apache License, Version 2.0
"""
from __future__            import annotations

__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2016-2026, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.2.0rc1"

from pathlib               import Path
from typing                import Any, ClassVar, Iterable, Iterator, Optional as Nullable

from docutils              import nodes
from docutils.nodes        import Element, Node
from sphinx                import addnodes
from sphinx.application    import Sphinx
from sphinx.builders       import Builder
from sphinx.domains        import Domain, Index, ObjType
from sphinx.environment    import BuildEnvironment
from sphinx.roles          import XRefRole
from sphinx.util.logging   import getLogger
from sphinx.util.nodes     import make_refnode

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError

from pyVHDLModel           import Design

from VHDLDomain.DesignUnit import ConfigurationDirective, ContextDirective, EntityDirective, PackageDirective
from VHDLDomain.Directive  import DesignDirective, LibraryDirective
from VHDLDomain.Frontend   import DesignConfiguration, VHDLDomainException
from VHDLDomain.Index      import EntityIndex, PackageIndex, SubprogramIndex, TypeIndex


__all__ = ["OBJECT_TYPES", "ROLES"]

_logger = getLogger(__name__)

#: The object types: their display names, by object type.
OBJECT_TYPES: dict[str, str] = {
	"design":        "design",
	"library":       "library",
	"context":       "context",
	"entity":        "entity",
	"architecture":  "architecture",
	"package":       "package",
	"configuration": "configuration",
	"type":          "type",
	"subtype":       "subtype",
	"constant":      "constant",
	"function":      "function",
	"procedure":     "procedure",
	"generic":       "generic",
	"port":          "port",
}

#: The roles: the object types each refers to, by role name.
ROLES: dict[str, tuple[str, ...]] = {
	"design":  ("design", ),
	"lib":     ("library", ),
	"ctx":     ("context", ),
	"ent":     ("entity", ),
	"arch":    ("architecture", ),
	"pack":    ("package", ),
	"config":  ("configuration", ),
	"type":    ("type", "subtype"),
	"const":   ("constant", ),
	"func":    ("function", ),
	"proc":    ("procedure", ),
	"generic": ("generic", ),
	"port":    ("port", ),
}


@export
def normalizeName(name: str) -> str:
	"""
	Normalize an object's name for comparison: lower case, without white space.

	VHDL identifiers are case-insensitive; white space may separate the type marks of a subprogram's signature.

	:param name: The name.
	:returns:    The normalized name.
	"""
	return "".join(name.split()).lower()


@export
class VHDLXRefRole(XRefRole):
	"""
	A role of domain ``vhdl``, referring to an object a directive described.

	The reference remembers the design and library current where it is written - set by ``vhdl:design`` and
	``vhdl:library`` -, so an ambiguous name is resolved in them. A leading ``~`` shows only the object's name, the last
	part of the target.
	"""

	def process_link(
		self,
		env:                BuildEnvironment,
		refnode:            Element,
		has_explicit_title: bool,
		title:              str,
		target:             str
	) -> tuple[str, str]:
		"""
		Remember the current design and library on the reference, and shorten the title for a leading ``~``.

		:param env:                The build environment.
		:param refnode:            The reference node.
		:param has_explicit_title: ``True``, if the role was written with a title, as ``text <target>``.
		:param title:              The title.
		:param target:             The target.
		:returns:                  The title and the target.
		"""
		refnode["vhdl:design"] =  env.ref_context.get("vhdl:design", None)
		refnode["vhdl:library"] = env.ref_context.get("vhdl:library", None)
		if not has_explicit_title and target.startswith("~"):
			target = target[1:]
			title = target.partition("(")[0].rpartition(".")[2]

		return title, target


@export
class VHDLDomain(Domain):
	"""
	The Sphinx domain ``vhdl``, documenting VHDL designs from their model.

	Its objects are keyed by object type and normalized qualified name - ``("entity", "stopwatch.lib_stopwatch.counter")``
	- and located by document and anchor. The designs are no domain data, as the environment pickles the data: they are
	read again by every build, and handed to the domain by :meth:`AddDesign`.
	"""

	name =         "vhdl"  #: Name of the domain, the prefix of its directives and roles.
	label =        "VHDL"  #: Name of the domain, as displayed.
	data_version = 1       #: Version of the data layout; a change discards pickled environments.

	object_types: ClassVar[dict[str, ObjType]] = {
		objectType: ObjType(displayName, *[roleName for roleName, types in ROLES.items() if objectType in types])
		for objectType, displayName in OBJECT_TYPES.items()
	}  #: The object types, each with the roles referring to it.

	directives: ClassVar[dict[str, type]] = {
		"design":        DesignDirective,
		"library":       LibraryDirective,
		"context":       ContextDirective,
		"entity":        EntityDirective,
		"package":       PackageDirective,
		"configuration": ConfigurationDirective,
	}  #: The directives, by name.

	roles: ClassVar[dict[str, XRefRole]] = {  # type: ignore[assignment]
		roleName: VHDLXRefRole(innernodeclass=nodes.literal, warn_dangling=True) for roleName in ROLES
	}  #: The roles, by name.

	indices: ClassVar[list[type[Index]]] = [
		EntityIndex,
		PackageIndex,
		SubprogramIndex,
		TypeIndex,
	]  #: The indices, each a page ``vhdl-<name>``, e.g. ``vhdl-entities``.

	dangling_warnings: ClassVar[dict[str, str]] = {
		roleName: f"VHDL {' or '.join(OBJECT_TYPES[objectType] for objectType in types)} '%(target)s' not found"
		for roleName, types in ROLES.items()
	}  #: The warning for a reference to an undocumented object, per role.

	initial_data: ClassVar[dict[str, Any]] = {
		"objects": {},
	}  #: The domain's data: ``objects`` maps (object type, normalized name) to (document, anchor, qualified name).

	#: The configuration values the domain adds to :file:`conf.py`, as ``name: (default, rebuild, types)``. Each is
	#: registered with the domain's name as prefix, e.g. ``vhdl_designs``.
	#:
	#: ``designs``
	#:    The designs to read, by name: the directory of the source files and the libraries' files, see
	#:    :mod:`VHDLDomain.Frontend`.
	configValues: ClassVar[dict[str, tuple[Any, str, Any]]] = {
		"designs": ({}, "env", dict),
	}

	_designs: dict[str, Design]                                     #: The designs read by this build, by name.
	_lookup:  Nullable[dict[tuple[str, str], list[tuple[str, str]]]]  #: Object keys by (object type, last name part).

	def __init__(self, env: BuildEnvironment) -> None:
		"""
		Initializes the domain.

		:param env: The build environment.
		"""
		super().__init__(env)

		self._designs = {}
		self._lookup =  None

	@readonly
	def Objects(self) -> dict[tuple[str, str], tuple[str, str, str]]:
		"""
		Read-only property to return the documented objects.

		:returns: A mapping of (object type, normalized qualified name) to (document, anchor, qualified name).
		"""
		return self.data["objects"]

	@readonly
	def Designs(self) -> dict[str, Design]:
		"""
		Read-only property to access the designs read by this build (:attr:`_designs`).

		:returns: Dictionary of the designs, indexed by design name.
		"""
		return self._designs

	def AddDesign(self, name: str, design: Design) -> None:
		"""
		Add a design, which the directives can describe.

		Besides the designs of ``vhdl_designs``, a design read by another frontend can be added, by a handler of Sphinx'
		``builder-inited`` event in :file:`conf.py`.

		:param name:                 The design's name, as directives and roles name it.
		:param design:               The design.
		:raises ValueError:          If parameter 'name' is ``None`` or empty.
		:raises TypeError:           If parameter 'name' is not of type :class:`str`.
		:raises ValueError:          If parameter 'design' is ``None``.
		:raises TypeError:           If parameter 'design' is not of type :class:`~pyVHDLModel.Design`.
		:raises VHDLDomainException: If a design of that name was added already.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if design is None:
			raise ValueError("Parameter 'design' is None.")
		elif not isinstance(design, Design):
			ex = TypeError("Parameter 'design' is not of type 'Design'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(design)}'.")
			raise ex

		if (normalizedName := name.lower()) in self._designs:
			raise VHDLDomainException(f"Design '{name}' was added already.")

		self._designs[normalizedName] = design

	def GetDesign(self, name: str) -> Nullable[Design]:
		"""
		Return a design by name.

		:param name: The design's name; case-insensitive.
		:returns:    The design, or ``None`` if no design of that name was added.
		"""
		return self._designs.get(name.lower(), None)

	def NoteObject(self, objectType: str, qualifiedName: str, nodeID: str, location: Nullable[Node] = None) -> None:
		"""
		Register a documented object.

		An object described twice - e.g. by two directives - is warned about; the later description wins.

		:param objectType:    The object type, as ``entity``.
		:param qualifiedName: The object's qualified name, as ``StopWatch.lib_StopWatch.Counter``.
		:param nodeID:        The anchor of the object's node.
		:param location:      Optional, the node a duplicate is reported at. Default: ``None``.
		:raises ValueError:   If parameter 'objectType' is not an object type of the domain.
		"""
		if objectType not in OBJECT_TYPES:
			ex = ValueError(f"Parameter 'objectType' is not an object type of domain '{self.name}'.")
			ex.add_note(f"Got value '{objectType}'.")
			ex.add_note(f"Object types: {', '.join(OBJECT_TYPES)}")
			raise ex

		objects = self.data["objects"]
		key = (objectType, normalizeName(qualifiedName))
		if (known := objects.get(key, None)) is not None:
			_logger.warning(
				f"Duplicate description of vhdl:{objectType} '{qualifiedName}', other instance in '{known[0]}'.",
				location=location, type=self.name, subtype="duplicate"
			)

		objects[key] = (self.env.docname, nodeID, qualifiedName)
		self._lookup = None

	def FindObjects(
		self,
		objectTypes: Iterable[str],
		target:      str,
		design:      Nullable[str] = None,
		library:     Nullable[str] = None
	) -> list[tuple[str, str]]:
		"""
		Find the objects a reference's target names.

		The target names an object by its qualified name or by a part of it ending with the object's name; it may end
		in a subprogram's signature, which must match then: the same number of type marks, each a type mark of the
		object's signature or a part of it ending with the type's name (``unsigned`` matches ``ieee.numeric_std.unsigned``).
		A qualified name equal to the target wins over the others. Of several matches, those in the given design - and
		then those in the given library - win.

		:param objectTypes: The object types the reference's role refers to.
		:param target:      The reference's target.
		:param design:      Optional, the design current at the reference. Default: ``None``.
		:param library:     Optional, the library current at the reference. Default: ``None``.
		:returns:           The keys of the matching objects: none, one, or several if the name is ambiguous.
		"""
		def signatureMatches(objectSignature: str, targetSignature: str) -> bool:
			"""
			Nested function checking whether a target's signature names an object's signature, type mark by type mark.

			:param objectSignature: The object's normalized signature, without the opening parenthesis.
			:param targetSignature: The target's normalized signature, without the opening parenthesis.
			:returns:               ``True``, if every type mark of the target names the object's type mark at its position.
			"""
			objectTypes = objectSignature.rstrip(")").split(",")
			targetTypes = targetSignature.rstrip(")").split(",")
			if len(objectTypes) != len(targetTypes):
				return False

			return all(
				objectType == targetType or objectType.endswith(f".{targetType}")
				for objectType, targetType in zip(objectTypes, targetTypes)
			)

		if self._lookup is None:
			self._lookup = {}
			for objectType, name in self.data["objects"]:
				lastPart = name.partition("(")[0].rpartition(".")[2]
				self._lookup.setdefault((objectType, lastPart), []).append((objectType, name))

		name = normalizeName(target)
		baseName, separator, signature = name.partition("(")
		lastPart = baseName.rpartition(".")[2]

		matches: list[tuple[str, str]] = []
		for objectType in objectTypes:
			for key in self._lookup.get((objectType, lastPart), []):
				keyBase, keySeparator, keySignature = key[1].partition("(")
				if keyBase != baseName and not keyBase.endswith(f".{baseName}"):
					continue
				elif separator != "" and (keySeparator == "" or not signatureMatches(keySignature, signature)):
					continue

				matches.append(key)

		if len(exact := [key for key in matches if key[1].partition("(")[0] == baseName]) > 0:
			matches = exact

		if len(matches) > 1 and design is not None:
			prefix = f"{design.lower()}."
			if len(inDesign := [key for key in matches if key[1].startswith(prefix)]) > 0:
				matches = inDesign

			if len(matches) > 1 and library is not None:
				prefix = f"{design.lower()}.{library.lower()}."
				if len(inLibrary := [key for key in matches if key[1].startswith(prefix)]) > 0:
					matches = inLibrary

		return matches

	def clear_doc(self, docname: str) -> None:
		"""
		Remove the objects of a document, before it is read again.

		:param docname: The document.
		"""
		objects = self.data["objects"]
		for key in [key for key, (document, _, _) in objects.items() if document == docname]:
			del objects[key]

		self._lookup = None

	def merge_domaindata(self, docnames: Iterable[str], otherdata: dict[str, Any]) -> None:
		"""
		Merge the objects a parallel reader collected for its documents.

		:param docnames:  The documents the other reader read.
		:param otherdata: The other reader's data.
		"""
		documents = set(docnames)
		objects = self.data["objects"]
		for key, location in otherdata["objects"].items():
			if location[0] in documents:
				objects[key] = location

		self._lookup = None

	def resolve_xref(
		self,
		env:         BuildEnvironment,
		fromdocname: str,
		builder:     Builder,
		typ:         str,
		target:      str,
		node:        addnodes.pending_xref,
		contnode:    Element
	) -> Nullable[Element]:
		"""
		Resolve a reference by one of the domain's roles.

		:param env:         The build environment.
		:param fromdocname: The document containing the reference.
		:param builder:     The builder.
		:param typ:         The role's name, as ``ent``.
		:param target:      The target, as ``lib_StopWatch.Counter``.
		:param node:        The pending reference.
		:param contnode:    The node rendering the reference's title.
		:returns:           The reference, the title if the name is ambiguous, or ``None`` if the target isn't documented.
		"""
		if typ not in ROLES:
			return None

		matches = self.FindObjects(ROLES[typ], target, node.get("vhdl:design", None), node.get("vhdl:library", None))
		if len(matches) == 0:
			return None
		elif len(matches) > 1:
			candidates = ", ".join(sorted(self.data["objects"][key][2] for key in matches))
			_logger.warning(
				f"VHDL {OBJECT_TYPES[matches[0][0]]} '{target}' is ambiguous, candidates: {candidates}",
				location=node, type=self.name, subtype="ref"
			)
			return contnode

		document, nodeID, qualifiedName = self.data["objects"][matches[0]]
		return make_refnode(builder, fromdocname, document, nodeID, contnode, qualifiedName)

	def resolve_any_xref(
		self,
		env:         BuildEnvironment,
		fromdocname: str,
		builder:     Builder,
		target:      str,
		node:        addnodes.pending_xref,
		contnode:    Element
	) -> list[tuple[str, nodes.reference]]:
		"""
		Resolve a reference by the ``:any:`` role, trying every role with an unambiguous match.

		:param env:         The build environment.
		:param fromdocname: The document containing the reference.
		:param builder:     The builder.
		:param target:      The target.
		:param node:        The pending reference.
		:param contnode:    The node rendering the reference's title.
		:returns:           A pair of role and reference per role the target resolves for.
		"""
		results = []
		for roleName, objectTypes in ROLES.items():
			matches = self.FindObjects(objectTypes, target, node.get("vhdl:design", None), node.get("vhdl:library", None))
			if len(matches) == 1:
				document, nodeID, qualifiedName = self.data["objects"][matches[0]]
				reference = make_refnode(builder, fromdocname, document, nodeID, contnode, qualifiedName)
				results.append((f"{self.name}:{roleName}", reference))

		return results

	def get_objects(self) -> Iterator[tuple[str, str, str, str, str, int]]:
		"""
		Iterate the documented objects, for the search index and the inventory.

		:returns: An iterator of (name, display name, type, document, anchor, priority).
		"""
		for (objectType, _), (document, nodeID, qualifiedName) in self.data["objects"].items():
			priority = 1 if objectType in ("design", "library", "context", "entity", "package", "configuration") else 2
			yield qualifiedName, qualifiedName, objectType, document, nodeID, priority


@export
def readDesigns(sphinx: Sphinx) -> None:
	"""
	Call-back for Sphinx' ``builder-inited`` event, reading the designs of ``vhdl_designs`` into the domain.

	A design, which can't be read, is logged as an error rather than stopping the build; a directive describing it warns
	on its own.

	:param sphinx: The Sphinx application.
	"""
	domain: VHDLDomain = sphinx.env.get_domain(VHDLDomain.name)  # type: ignore[assignment]
	for name, value in sphinx.config.vhdl_designs.items():
		try:
			configuration = DesignConfiguration.Parse(name, value, Path(sphinx.srcdir))
			domain.AddDesign(configuration.Name, configuration.Load())
		except (VHDLDomainException, MissingDependencyError) as ex:
			notes = "".join(f"\n  {note}" for note in getattr(ex, "__notes__", []))
			_logger.error(f"Design '{name}' not read: {ex}{notes}", type=VHDLDomain.name, subtype="design")


@export
def setup(sphinx: Sphinx) -> dict[str, Any]:
	"""
	Register the domain ``vhdl`` and its configuration values with Sphinx.

	:param sphinx: The Sphinx application to register with.
	:returns:      The extension's metadata.
	"""
	sphinx.add_domain(VHDLDomain)
	for configName, (default, rebuild, types) in VHDLDomain.configValues.items():
		sphinx.add_config_value(f"{VHDLDomain.name}_{configName}", default, rebuild, types)

	sphinx.connect("builder-inited", readDesigns)

	return {
		"version":             __version__,
		"env_version":         VHDLDomain.data_version,
		"parallel_read_safe":  True,
		"parallel_write_safe": True,
	}
