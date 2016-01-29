# -*-coding:Utf-8 -*

# Copyright (c) 2010-2016 LE GOFF Vincent
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""Fichier contenant le module secondaire tags."""

from abstraits.module import *
from corps.fonctions import valider_cle
from primaires.format.fonctions import format_nb
#from secondaires.tags import commandes
from secondaires.tags.tag import Tag
#from secondaires.tags import editeurs

class Module(BaseModule):

    """Module gérant les tags de différentes natures.

    Un tag représente une fonctionnalité que l'on peut appliquer, par exemple, sur un objet ou un PNJ. Les tags facilitent aussi la copie de scripts.

    Par exemple, ce module permettrait de créer un tag 'marchand'
    pour les PNJ. Les PNJ vendeurs de magasin pourraient avoir ce
    tag, ce qui simplifierait la recherche dans plusieurs cas. En
    outre, les scripts sélectionnés seraient copiés, permettant
    d'avoir une réplique des fonctionnalités sur plusieurs PNJ. Bien
    que les types de tag soient définis dans le code, créer et appliquer
    un tag peut se faire dans l'univers sans difficulté.

    """

    def __init__(self, importeur):
        """Constructeur du module"""
        BaseModule.__init__(self, importeur, "tags", "secondaire")
        self.tags = {}
        self.types = ["objet", "pnj"]
        self.logger = self.importeur.man_logs.creer_logger("tags", "tags")

    def init(self):
        """Chargement des objets du module."""
        tags = self.importeur.supenr.charger_groupe(Tag)
        groupes = {}
        for tag in tags:
            self.ajouter_tag(tag)
            if tag.type not in groupes:
                groupes[tag.type] = []

            groupe = groupes[tag.type]
            groupe.append(tag)

        self.logger.info(format_nb(len(tags),
                "{nb} tag{s} récupérée{s}"))

        for type, groupe in groupes.items():
            self.logger.info(format_nb(len(groupe),
                    "  Dont {nb} tag{s} du type " + type))
    def ajouter_commandes(self):
        """Ajout des commandes dans l'interpréteur"""
        self.commandes = [
    #        commandes.tag.Cmdtag(),
        ]

        for cmd in self.commandes:
            self.importeur.interpreteur.ajouter_commande(cmd)

        # Ajout des éditeurs
        #self.importeur.interpreteur.ajouter_editeur(
        #        editeurs.gldedit.GldEdit)

    def creer_tag(self, cle, type):
        """Crée un nouveau tag."""
        valider_cle(cle)

        if type not in self.types:
            raise ValueError("le type de tag {} n'existe pas".format(
                    repr(type)))

        if cle in self.tags:
            raise ValueError("le tag {} existe déjà".format(
                    repr(cle)))

        tag = Tag(cle, type)
        self.ajouter_tag(tag)
        return tag

    def ajouter_tag(self, tag):
        """Ajoute le tag."""
        if tag.cle in self.tags:
            raise ValueError("le tag de clé {} est " \
                    "déjà défini".format(repr(tag.cle)))

        self.tags[tag.cle] = tag

    def supprimer_tag(self, cle):
        """Supprime un tag."""
        if cle not in self.tags:
            raise ValueError("le tag {} n'existe pas".format(
                    repr(cle)))

        self.tags.pop(cle).detruire()
