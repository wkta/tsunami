# -*-coding:Utf-8 -*

# Copyright (c) 2013 LE GOFF Vincent
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


"""Fichier contenant la classe Equipage, détaillée plus bas."""

from random import choice

from abstraits.obase import BaseObj
from primaires.format.fonctions import supprimer_accents
from secondaires.navigation.equipage.ordre import ordres
from secondaires.navigation.equipage.matelot import Matelot
from secondaires.navigation.equipage.noms import NOMS_MATELOTS

class Equipage(BaseObj):

    """Classe représentant l'équipage d'un navire.

    Un équipage est le lien entre un navire et une liste de mâtelots.
    Il permet d'exécuter des ordres et de les décomposer si besoin en
    passant par la mini-intelligence.

    """

    def __init__(self, navire):
        """Constructeur du matelot."""
        BaseObj.__init__(self)
        self.navire = navire
        self.matelots = {}
        self._construire()

    def __getnewargs__(self):
        return (None, )

    def __repr__(self):
        navire = self.navire and self.navire.cle or "aucun"
        return "<Équipage du navire {}>".format(repr(navire))

    def ajouter_matelot(self, personnage, nom_poste="matelot"):
        """Ajoute un mâtelot à l'équipage."""
        matelot = Matelot(self, personnage)
        matelot.nom_poste = nom_poste
        matelot.nom = self.trouver_nom_matelot()
        self.matelots[supprimer_accents(matelot.nom.lower())] = matelot

    def trouver_nom_matelot(self):
        """Trouve un nom de mâtelot non utilisé."""
        noms = [matelot.nom for matelot in self.matelots]
        noms_disponibles = [nom for nom in NOMS_MATELOTS if nom not in noms]
        return choice(noms_disponibles)

    def ordonner_matelot(self, nom, ordre, *args, **kwargs):
        """Ordonne à un mâtelot en particulier.

        Le mâtelot est trouvé en fonction de son nom. Si le nom est trouvé
        dans l'équipage, alors cherche l'ordre.

        L'ordre est un nom d'ordre également. Les paramètres optionnels
        sont transmis au constructeur de l'ordre.

        """
        matelot = self.get_matelot(nom)
        classe_ordre = ordres[ordre]
        ordre = classe_ordre(matelot, self.navire, *args, **kwargs)
        matelot.ordonner(ordre)
        matelot.executer_ordre()
        return ordre

    def get_matelot(self, nom):
        """Retourne, si trouvé, le âtelot recherché.

        Si le mâtelot ne peut être trouvé, lève une exception KeyError.

        """
        nom = supprimer_accents(nom).lower()
        if nom not in self.matelots:
            raise KeyError("matelot {} introuvable".format(repr(nom)))

        return self.matelots[nom]