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


"""Fichier contenant les constantes d'équipage."""

from primaires.format.fonctions import supprimer_accents

# Aptitudes de matelots
NOMS_APTITUDES = {
        "calfeutrage": "charpenterie",
        "escrimeur": "escrimeur",
}

CLES_APTITUDES = {}
for cle, nom in NOMS_APTITUDES.items():
    CLES_APTITUDES[supprimer_accents(nom).lower()] = cle

# Niveaux
NIVEAU_MEDIOCRE = 0
NIVEAU_FAIBLE = 1
NIVEAU_MOYEN = 2
NIVEAU_BON = 3
NIVEAU_TRES_BON = 4
NIVEAU_EXCELLENT = 5

# Noms des niveaux
NOMS_NIVEAUX = {
        NIVEAU_MEDIOCRE: "médiocre",
        NIVEAU_FAIBLE: "peu expérimenté",
        NIVEAU_MOYEN: "assez expérimenté",
        NIVEAU_BON: "plutôt expérimenté",
        NIVEAU_TRES_BON: "très expérimenté",
        NIVEAU_EXCELLENT: "excellent",
}

VALEURS_NIVEAUX = {}
for nom, niveau in NOMS_NIVEAUX.items():
    VALEURS_NIVEAUX[supprimer_accents(niveau).lower()] = nom

# Talents
TALENTS = {
        "calfeutrage": ["calfeutrage"],
        "escrimeur": ["maniement de l'épée", "parade"],
}

CONNAISSANCES = {
        NIVEAU_MEDIOCRE: 10,
        NIVEAU_FAIBLE: 17,
        NIVEAU_MOYEN: 30,
        NIVEAU_BON: 50,
        NIVEAU_TRES_BON: 70,
        NIVEAU_EXCELLENT: 95,
}
