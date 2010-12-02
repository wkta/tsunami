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


"""Fichier contenant des fonctions utiles à la manipulation des noeuds"""

from primaires.interpreteur.masque.noeuds.embranchement import Embranchement
from primaires.interpreteur.masque.noeuds.noeud_masque import NoeudMasque
from primaires.interpreteur.masque.noeuds.noeud_optionnel import NoeudOptionnel

def creer_noeud(schema):
    """Fonction appelée pour créer un noeud.
    Elle prend en paramètre :
    schema -- le schéma, sous la forme d'une chaîne de caractère, qui va
              nous indiquer quel noeud créer
    
    """
    schema = schema.lstrip()
    if not schema:  # schema est vide
        return None
    caractere = schema[0]
    schema = schema[1:]
    if caractere == '(': # un noeud optionnel
        noeud_interne = creer_noeud(schema)
        noeud_suivant = creer_noeud(schema)
        nv_noeud = NoeudOptionnel(noeud_interne, noeud_suivant)
    elif caractere == '<':
        nv_noeud = NoeudMasque(schema)
        nv_noeud.suivant = creer_noeud(schema)
    elif caractere == ')':
        nv_noeud = None
    else:
        #Faudra voir pour le cas des mots-clés...
        pass
    
    return nv_noeud

def ajouter_fils(noeud_racine, noeud_fils):
    """Ajoute un fils au noeud racine spécifié.
    Si c'est un embranchement, on ajoute un fils.
    Sinon, on modifie tout simplement le noeud suivant.
    
    """
    if isinstance(noeud_racine, Embranchement):
        noeud_racine.suivant.append(noeud_fils)
    else:
        noeud_racine.suivant = noeud_fils
    
    return noeud_fils
