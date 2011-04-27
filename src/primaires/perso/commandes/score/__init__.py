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


"""Package contenant la commande 'score'.

"""

from primaires.interpreteur.commande.commande import Commande

# Chaîne représentant le score
chn_score = \
"/----------------------------------------------\\\n" \
"| {nom: <15}                              |\n" \
"|                                              |\n" \
"|    Vitalité   |     Mana    |   Endurance    |\n" \
"|   {v: >5}/{vm: <5} | {m: >5}/{mm: <5} | {e: >5}/{em: <5}    |\n" \
"|                                              |\n" \
"|      For - Agi - Rob - Int - Cha - Sen       |\n" \
"|      {f: >3} | {a: >3} | {r: >3} | {i: >3} | {c: >3} | {s: >3}       |\n" \
"|                                              |\n" \
"\\----------------------------------------------/"

class CmdScore(Commande):
    
    """Commande 'score'.
    
    """
    
    def __init__(self):
        """Constructeur de la commande"""
        Commande.__init__(self, "score", "score")
        self.schema = ""
        self.aide_courte = "affiche votre feuille de personnage"
        self.aide_longue = \
            "Cette commande vous donne des informations générales sur " \
            "votre personnage. Considérez ces informations comme une " \
            "fiche de personnage, vous donnant des informations sur vos " \
            "stats actuelles, vos états, votre race..."
    
    def interpreter(self, personnage, dic_masques):
        """Interprétation de la commande"""
        personnage << chn_score.format(
            nom=personnage.nom,
            v=personnage.vitalite,
            vm=personnage.vitalite_max,
            m=personnage.mana,
            mm=personnage.mana_max,
            e=personnage.endurance,
            em=personnage.endurance_max,
            f=personnage.force,
            a=personnage.agilite,
            r=personnage.robustesse,
            i=personnage.intelligence,
            c=personnage.charisme,
            s=personnage.sensibilite,
        )
