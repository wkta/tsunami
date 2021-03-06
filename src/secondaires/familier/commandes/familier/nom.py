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
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT master OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""Fichier contenant le paramètre 'nom' de la commande 'familier'."""

from primaires.interpreteur.masque.parametre import Parametre

class PrmNom(Parametre):

    """Commande 'familier nom'.

    """

    def __init__(self):
        """Constructeur du paramètre"""
        Parametre.__init__(self, "nom", "name")
        self.groupe = "administrateur"
        self.schema = "<cle> <texte_libre>"
        self.aide_courte = "change le nom du familier"
        self.aide_longue = \
            "Cette commande permet de changer le nom du familier. " \
            "Vous devez préciser d'abord l'identifiant du familier, " \
            "sous la forme |ent|cle_prototype_numero|ff| (par exemple " \
            "|ent|cheval_1|ff|), ensuite le nouveau nom du familier."

    def interpreter(self, personnage, dic_masques):
        """Interprétation du paramètre"""
        # On récupère le familier et le nom
        identifiant = dic_masques["cle"].cle
        nom = dic_masques["texte_libre"].texte

        try:
            familier = importeur.familier.familiers[identifiant]
        except KeyError:
            personnage << "|err|Le PNJ {} n'est pas un familier.|ff|".format(
                    repr(identifiant))
            return

        familier.nom = nom.capitalize()
        personnage << "Le nom du familier {} a bien été changé pour " \
                "{}.".format(familier.identifiant, familier.nom)
