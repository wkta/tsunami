# -*-coding:Utf-8 -*

# Copyright (c) 2010-2017 LE GOFF Vincent
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


"""Fichier contenant la classe Type, détaillée plus bas."""

from abstraits.obase import BaseObj
from primaires.objet.types import MetaType
from primaires.format.fonctions import supprimer_accents
from secondaires.crafting.extension import Extension

class Type(BaseObj):

    """Classe représentant un type d'objet."""

    def __init__(self, guilde, parent, nom):
        """Constructeur du type."""
        BaseObj.__init__(self)
        self.guilde = guilde
        self.parent = parent
        self.nom = nom
        self.attributs = []
        self.extensions = []
        self._construire()

    def __getnewargs__(self):
        return (None, "", "")

    @property
    def nom_complet(self):
        """Retourne le nom complet."""
        return "{} (parent : {})".format(self.nom, self.parent)

    def ajouter_attribut(self, attribut):
        """Ajout d'un attribut."""
        self.attributs.append(attribut)
        importeur.crafting.enregistrer_YML()
        classe = importeur.objet.get_type(self.nom)
        classe.attributs_crafting = list(self.attributs)

    def supprimer_attribut(self, attribut):
        """Supprime l'attribut précisé."""
        while attribut in self.attributs:
            self.attributs.remove(attribut)

        importeur.crafting.enregistrer_YML()
        classe = importeur.objet.get_type(self.nom)
        classe.attributs_crafting = list(self.attributs)

    def get_extension(self, nom, exception=True):
        """Retourne l'extension précisée."""
        nom = supprimer_accents(nom).lower()

        for extension in self.extensions:
            if supprimer_accents(extension.nom).lower() == nom:
                return extension

        if exception:
            raise ValueError("L'extension {} n'existe pas".format(repr(nom)))

    def ajouter_extension(self, nom, nom_type):
        """Ajout d'une extension."""
        if self.get_extension(nom, False):
            raise ValueError("L'extension {} existe déjà".format(repr(nom)))

        extension = Extension(self, None, nom)
        extension.type = nom_type
        self.extensions.append(extension)
        return extension

    def supprimer_extension(self, nom):
        """Supprime l'extension précisée."""
        extension = self.get_extension(nom)
        self.extensions.remove(extension)
        extension.detruire()

    def creer(self):
        """Création du type."""
        return self.creer_type(self.parent, self.nom, self.attributs)

    @classmethod
    def creer_type(cls, parent, nom, attributs):
        """Crée le type d'objet (la classe)."""
        parent = importeur.objet.types[parent]

        # Si la classe existe, on la modifie juste
        try:
            classe = importeur.objet.get_type(nom)
            importeur.crafting.logger.info("Extension du type {} (attributs {})".format(
                    repr(nom), list(attributs)))
        except KeyError:
            nom_classe = supprimer_accents(nom)
            nom_classe = "".join(mot.capitalize() for mot in nom_classe.split(
                    " "))

            # Création de la classe dynamiquement
            classe = MetaType(nom_classe, (parent, ), {"nom_type": nom})
            importeur.crafting.logger.info("Création du type {} (attributs {})".format(
                    repr(nom), list(attributs)))

        classe.attributs_crafting = list(attributs)

        return classe
