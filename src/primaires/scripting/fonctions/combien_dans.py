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


"""Fichier contenant la fonction combien_dans."""

from fractions import Fraction

from primaires.scripting.fonction import Fonction
from primaires.scripting.instruction import ErreurExecution

class ClasseFonction(Fonction):

    """Renvoie le nombre d'objets dans un conteneur."""

    @classmethod
    def init_types(cls):
        cls.ajouter_types(cls.cb_dans, "Objet")
        cls.ajouter_types(cls.cb_dans_proto, "Objet", "str")

    @staticmethod
    def cb_dans(conteneur):
        """Renvoie le nombre d'objets contenus dans le conteneur."""
        if conteneur.est_de_type("conteneur de potion"):
            return Fraction(1) if conteneur.potion else Fraction(0)
        if conteneur.est_de_type("conteneur de nourriture"):
            return Fraction(len(conteneur.nourriture))
        if conteneur.est_de_type("conteneur"):
            return Fraction(sum(nb for o, nb in \
                    conteneur.conteneur.iter_nombres))
        raise ErreurExecution("{} n'est pas un conteneur".format(conteneur))

    @staticmethod
    def cb_dans_proto(conteneur, prototype):
        """Renvoie la quantité d'objets du prototype dans le conteneur.

        Paramètres à préciser :

          * conteneur : l'objet conteneur [1] ;
          * prototype : la clé du prototype (chaîne de caractères).

        [1] Le conteneur passé en argument doit être de type conteneur de potion, conteneur de nourriture ou conteneur.

        Exemple d'utilisation :

          nb = contenus_dans(sac, "chausson_toile")
          # Vous pouvez tester avec des pièces aussi
          argent = contenus_dans(bourse, "piece_bronze")
          # Pour garder la compatibilité si plusieurs types de
          # monnaies existent, utilisez la fonction somme() à la place.

        """
        if not prototype in importeur.objet.prototypes:
            raise ErreurExecution("prototype {} introuvable".format(prototype))

        prototype = importeur.objet.prototypes[prototype]

        if conteneur.est_de_type("conteneur de potion"):
            if conteneur.potion and conteneur.potion.prototype is prototype:
                return Fraction(1)
            return Fraction(0)

        if conteneur.est_de_type("conteneur de nourriture"):
            return Fraction(len([o for o in conteneur.nourriture if \
                    o.prototype is prototype]))
        if conteneur.est_de_type("conteneur"):
            qtt = 0
            for o, nb in conteneur.conteneur.iter_nombres():
                o_prototype = getattr(o, "prototype", o)
                if prototype is o_prototype:
                    qtt += nb

            return Fraction(qtt)

        raise ErreurExecution("{} n'est pas un conteneur".format(conteneur))
