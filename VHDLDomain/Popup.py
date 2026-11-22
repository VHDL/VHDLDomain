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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Popups of references: a reference to a declaration of a package shows the declaration, while the mouse is over it or
it has the keyboard focus.

A declaration is e.g. a type, a constant, a component or a subprogram. ``vhdl:package`` notes its popup in the domain:
the library and design unit declaring it, its signature, the first paragraph of its documentation, and a record's
elements, an enumeration's literals or a physical type's units. In HTML, a reference to the declaration is a
:class:`PopupReferenceNode`: the link and a :class:`PopupNode`, which the stylesheet :data:`STYLESHEET` shows, without
JavaScript. Other builders write the link only.
"""
from __future__           import annotations

from hashlib              import md5
from pathlib              import Path

from docutils             import nodes
from docutils.nodes       import Element, Node
from sphinx               import addnodes
from sphinx.application   import Sphinx
from sphinx.writers.html5 import HTML5Translator

from pyTooling.Common     import readResourceFile
from pyTooling.Decorators import export

from VHDLDomain           import Resources


__all__ = ["STYLESHEET"]

STYLESHEET = "VHDLDomain.css"
"""Name of the stylesheet showing the popups, in :mod:`VHDLDomain.Resources`."""


@export
class PopupNode(nodes.General, nodes.Inline, nodes.TextElement):
	"""
	The popup of a reference: the declaration of the object the reference refers to.

	Its children are spans with the classes ``vhdl-popup-location``, ``vhdl-popup-signature``,
	``vhdl-popup-documentation`` and ``vhdl-popup-members``.
	"""


@export
class PopupReferenceNode(nodes.General, nodes.Inline, nodes.TextElement):
	"""
	A reference with a popup: the reference node, followed by its :class:`PopupNode`.
	"""


@export
def popupContent(element: Element) -> list[Node]:
	"""
	Copy an element's content for a popup: text, emphasis, strong, literals and the parts of a signature keep their
	markup; every other node becomes its text.

	A reference or a parameter list, for example, becomes its text: a popup holds no targets and no links, so no ID and
	no reference is copied.

	:param element: The element, e.g. a signature or a paragraph.
	:returns:       The copied nodes.
	"""
	content: list[Node] = []
	for child in element.children:
		if isinstance(child, (
			nodes.emphasis, nodes.strong, nodes.literal, addnodes.desc_annotation, addnodes.desc_name, addnodes.desc_addname,
			addnodes.desc_returns, addnodes.desc_sig_element
		)):
			content.append(type(child)("", "", *popupContent(child)))
		else:
			content.append(nodes.Text(child.astext()))

	return content


@export
def html_visit_PopupReferenceNode(translator: HTML5Translator, node: PopupReferenceNode) -> None:
	"""
	Write a reference with a popup in HTML, completely: a ``span`` with the class ``vhdl-popup-anchor``, holding the
	link, which the popup describes (``aria-describedby``), and the popup.

	:param translator: The HTML translator writing the document.
	:param node:       The reference with its popup.
	:raises SkipNode:  Always, as the children are written here.
	"""
	reference: nodes.reference = node[0]  # type: ignore[assignment]
	popup:     PopupNode =       node[1]  # type: ignore[assignment]
	href =       reference["refuri"] if "refuri" in reference else f"#{reference['refid']}"
	attributes = {"aria-describedby": popup["ids"][0]}

	translator.body.append(translator.starttag(node, "span", ""))
	translator.body.append(translator.starttag(reference, "a", "", CLASS="reference internal", href=href, **attributes))
	for child in reference.children:
		child.walkabout(translator)

	translator.body.append("</a>")
	popup.walkabout(translator)
	translator.body.append("</span>")

	raise nodes.SkipNode


@export
def html_visit_PopupNode(translator: HTML5Translator, node: PopupNode) -> None:
	"""
	Open a popup in HTML: a ``span`` with the role ``tooltip``, which the stylesheet shows while the reference is hovered
	or focused.

	The popup's text wraps, also in a signature, whose text is protected from line wrapping.

	:param translator: The HTML translator writing the document.
	:param node:       The popup.
	"""
	translator.body.append(translator.starttag(node, "span", "", role="tooltip"))
	translator.context.append(translator.protect_literal_text)
	translator.protect_literal_text = 0


@export
def html_depart_PopupNode(translator: HTML5Translator, node: PopupNode) -> None:
	"""
	Close a popup in HTML.

	:param translator: The HTML translator writing the document.
	:param node:       The popup.
	"""
	translator.protect_literal_text = translator.context.pop()
	translator.body.append("</span>")


@export
def installStylesheet(sphinx: Sphinx) -> None:
	"""
	Call-back for Sphinx' ``builder-inited`` event, writing the stylesheet :data:`STYLESHEET` into the build of an HTML
	builder and linking it, unless ``vhdl_reference_popups`` is off.

	The file is named by the hash of its content, so a browser re-reads it when it changes; an older copy is removed.

	:param sphinx: The Sphinx application.
	"""
	if sphinx.builder.format != "html" or not sphinx.config.vhdl_reference_popups:
		return

	content =         readResourceFile(Resources, STYLESHEET)
	digest =          md5(content.encode("utf-8")).hexdigest()  # nosec B324 - a cache-busting name, not a signature
	stem =            STYLESHEET.removesuffix(".css")
	staticDirectory = (Path(sphinx.outdir) / "_vhdl_static").resolve()
	staticFile =      staticDirectory / f"{stem}.{digest}.css"

	staticDirectory.mkdir(exist_ok=True)
	sphinx.config.html_static_path.append(str(staticDirectory))
	sphinx.add_css_file(staticFile.name)
	if not staticFile.exists():
		for outdated in staticDirectory.glob(f"{stem}.*.css"):
			outdated.unlink()

		with staticFile.open("w", encoding="utf-8") as file:
			file.write(content)
