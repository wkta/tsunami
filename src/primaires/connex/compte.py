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


"""Ce fichier définit la classe Compte."""

import hashlib

from bases.collections.liste_id import ListeID
from abstraits.id import ObjetID

class Compte(ObjetID):
    """Classe représentant un compte.
    On peut y trouver différentes informations :
    *   le nom (naturellement), identifiant du compte
    *   le mot de passe chiffré, protégeant le compte
    *   une adresse e-mail valide
    *   un encodage de sortie
    *   la liste des joueurs liés à ce compte
    
    """
    groupe = "comptes"
    sous_rep = "comptes"
    
    def __init__(self, nom_compte):
        """Constructeur d'un compte."""
        ObjetID.__init__(self)
        self.nom = nom_compte
        self.mot_de_passe = ""
        self.adresse_email = ""
        self.encodage = ""
        self.valide = False
        self.code_validation = ""
        self.msg_validation = False # à True si le message de validation a été envoyé
        self.tentatives_validation = 0 # tentatives de validation
        self.nb_essais = 0 # tentatives d'intrusion (mot de passe erroné)
        self.joueurs = ListeID()
        self.contexte = None # le contexte du compte
    
    def __getinitargs__(self):
        """Méthode retournant les valeurs par défaut du constructeur"""
        return ("", )
    
    def hash_mot_de_pass(self, clef_salage, type_chiffrement, mot_de_passe):
        """Méthode appelé pour hasher le mot de passe"""
        mot_de_passe = str(clef_salage + mot_de_passe).encode()
        h = hashlib.new(type_chiffrement)
        h.update(mot_de_passe)
        
        return h.digest()
    
    def get_joueur(self, nom_perso):
        """Retourne le joueur correspondant au nom"""
        joueur = None
        for perso in self.joueurs:
            if perso.nom == nom_perso:
                joueur = perso
                break
        
        return joueur
    
    def ajouter_joueur(self, joueur):
        """Ajoute le joueur passé en paramètre à la liste des joueurs"""
        self.joueurs.append(joueur)
        self.enregistrer()
    
    def supprimer_joueur(self, joueur):
        """Supprime le joueur passé en paramètre de la liste des joueurs"""
        self.joueurs.remove(joueur)
        self.enregistrer()
    
    def _get_contexte_actuel(self):
        """Retourne le contexte du compte"""
        return self.contexte
    
    def _set_contexte_actuel(self, nouveau_contexte):
        """Modifie le contexte actuel du compte"""
        self.contexte = nouveau_contexte
    
    contexte_actuel = property(_get_contexte_actuel, _set_contexte_actuel)

ObjetID.ajouter_groupe(Compte)
