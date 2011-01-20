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


"""Ce fichier définit un conteneur de groupe. Il doit n'y voir qu'un conteneur
de groupes et c'est de ce fait à la fois une classe singleton implicite
dérivée de Unique.

"""

from abstraits.unique import Unique
from primaires.interpreteur.groupe.groupe import Groupe

class ConteneurGroupes(Unique):
    
    """Classe conteneur des groupes.
    Elle peut être soit créée directement par le système si le fichier
    n'existe pas, soit récupérée depuis son fichier de sauvegarde.
    
    """
    
    def __init__(self):
        """Constructeur du conteneur."""
        Unique.__init__(self, "groupes", "groupes")
        self._groupes = {} # nom_groupe:groupe
    
    def __getinitargs__(self):
        return ()
    
    def __contains__(self, nom_groupe):
        """Retourne True si le groupe est dans le dictionnaire, False sinon"""
        return nom_groupe in self._groupes.keys()
    
    def __getitem__(self, nom_groupe):
        """Retourne le groupe avec le nom spécifié"""
        return self._groupes[nom_groupe]
    
    def __len__(self):
        """Retourne le nombre de groupes"""
        return len(self._groupes)
    
    def ajouter_groupe(self, nom_groupe):
        """Méthode appelée pour ajouter un groupe.
        L'objet Groupe est créé "à la volée" et est retourné par la méthode si
        l'on désire le manipuler directement.
        
        """
        groupe = Groupe(nom_groupe)
        self._groupes[nom_groupe] = groupe
        self.enregistrer()
        return groupe
    
    def supprimer_groupe(self, nom_groupe):
        """Supprime le groupe nom_groupe"""
        del self._groupes[nom_groupe]
        self.enregistrer()
