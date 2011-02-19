# -*-coding:Utf-8 -*

# Copyright (c) 2010 LE GOFF Vincent
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


"""Fichier contenant la classe Sorties, détaillée plus bas;"""

from collections import OrderedDict

from abstraits.obase import *
from .sortie import Sortie

NOMS_SORTIES = OrderedDict()
NOMS_SORTIES["sud"] = None
NOMS_SORTIES["sud-ouest"] = None
NOMS_SORTIES["ouest"] = None
NOMS_SORTIES["nord-ouest"] = None
NOMS_SORTIES["nord"] = None
NOMS_SORTIES["nord-est"] = None
NOMS_SORTIES["est"] = None
NOMS_SORTIES["sud-est"] = None
NOMS_SORTIES["bas"] = None
NOMS_SORTIES["haut"] = None

class Sorties(BaseObj):
    
    """Conteneur des sorties.
    Elle contient l'ensemble des sorties d'une salle, sous la forme de X (maximum
    10) objets Sortie.
    
    Voir : ./sortie.py
    
    """
    
    def __init__(self, parent=None):
        """Constructeur du conteneur"""
        BaseObj.__init__(self)
        self.parent = parent
        self._sorties = OrderedDict(NOMS_SORTIES)
        # On passe le statut en CONSTRUIT
        self._statut = CONSTRUIT
    
    def __getinitargs__(self):
        return ()
    
    def __getitem__(self, nom):
        """Retourne la sortie correspondante"""
        return self._sorties[nom]
    
    def __setitem__(self, nom, sortie):
        """Se charge principalement de lever une exception si
        'nom' n'est pas dans 'NOMS_SORTIES'.
        
        """
        if nom not in NOMS_SORTIES.keys():
            raise ValueError("le nom {} n'est pas accepté en identifiant " \
                    "de sortie".format(repr(nom)))
        
        self._sorties[nom] = sortie
        
        if self.construit and self.parent:
            self.parent.enregistrer()
    
    def ajouter_sortie(self, nom, *args, **kwargs):
        """Ajoute une sortie.
        Le nom doit être un des noms sorties prévu et caractérise une direction.
        Les paramètres *args seront transmis au constructeur de Sortie
        
        ATTENTION : si une sortie existe déjà dans la direction spécifiée,
        elle sera écrasée par la nouvelle.
        
        """
        sortie = Sortie(*args, parent=self.parent, **kwargs)
        self[nom] = sortie
    
    def supprimer_sortie(self, nom):
        """Supprime la sortie"""
        self[nom] = None
    
    def iter_couple(self):
        """Retourne un générateur parcourant les couples nom:sortie"""
        for nom, sortie in self._sorties.items():
            yield (nom, sortie)
