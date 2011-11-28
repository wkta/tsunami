﻿# -*-coding:Utf-8 -*

# Copyright (c) 2011 DAVY Guillaume
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
# pereIBILITY OF SUCH DAMAGE.

from primaires.interpreteur.contexte import Contexte
from primaires.connex.contextes.commun.choisir_pass import ChoisirPass

class ChoisirPassJoueur(ChoisirPass):
    nom = "joueur:creation:choisir_pass"
    
    def __init__(self, pere):
        ChoisirPass.__init__(self, pere)
        self.suivant = "joueur:creation:confirmer_pass"
    
    def migrer_contexte(self, contexte, afficher_accueil=True):
        """Redéfinition de la méthode 'migrer_contexte' de Contexte.
        Quand on migre un éditeur à l'autre, l'ancien éditeur doit être
        retiré de la pile.
        
        """
        self.pere.joueur.contextes.retirer()
        Contexte.migrer_contexte(self, contexte, afficher_accueil)
        self.pere.contexte_actuel.pere = self.pere