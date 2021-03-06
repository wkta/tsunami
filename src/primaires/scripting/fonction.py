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


"""Fichier contenant la classe Fonction, détaillée plus bas."""

from fractions import Fraction
from time import time

from abstraits.obase import BaseObj
from .parser import expressions

class Fonction(BaseObj):

    """Classe définissant une fonction.

    Une fonction est un composant d'une instruction prenant plusieurs
    paramètres et en retournant. Une fonction n'a d'intérêt que si elle
    retourne quelque chose.

    Ainsi, ce sont les grandes différences avec une action :
    -   une action est une instruction, une fonction n'en est qu'une
        composante ;
    -   une action ne retourne rien, une fonction si ;
    -   une action modifie, une fonction consulte (principalement).

    NOTE IMPORTANTE : dans le package parser est défini un module fonction
    contenant une classe Fonction. Il ne faut pas confondre ces deux classes
    ayant un but très différent :
    -   la classe définie dans parser est utile pour parser une fonction,
        isoler son nom, ses paramètres. L'objet généré sera stocké dans
        l'instruction ;
    -   la classe définie ici existe comme classe-mère de toutes les
        fonctions définies dans le sous-package fonctions.

    """

    _parametres_possibles = None
    verifier = True
    def __init__(self, fonction):
        """Construction d'une fonction."""
        BaseObj.__init__(self)
        self.fonction = fonction

    def __getnewargs__(self):
        return (None, )

    def __str__(self):
        return str(self.fonction)

    @classmethod
    def executer(cls, evenement, *parametres):
        """Exécute la fonction selon l'évènement."""
        t1 = time()
        fonction = cls.quelle_fonction(parametres)
        retour = fonction(*parametres)
        t2 = time()
        cls.enregistrer_stats(t1, t2)
        return retour

    @classmethod
    def get_methode(self, numero):
        """Retourne la méthode correspondant au numéro d'ordre entré."""
        return list(self._parametres_possibles.values())[numero]

    @classmethod
    def ajouter_types(cls, methode, *parametres):
        """Ajoute une interprétation possible de la fonction.

        Les fonctions peuvent avoir plusieurs interprétations possibles
        en fonction du type de leurs paramètres.

        Les paramètres suplémentaires sont les types. Tous doivent être
        des chaînes de caractères.

        """
        if tuple((p for p in parametres if not isinstance(p, str))):
            raise TypeError("Les types doivent être de type 'str'.")

        if parametres in cls._parametres_possibles:
            raise ValueError("Les paramètres {} existent déjà pour " \
                    "cette fonction.".format(parametres))

        cls._parametres_possibles[parametres] = methode

    @classmethod
    def quelle_fonction(cls, parametres):
        """Retourne la fonction correspondant aux paramètres.

        Les paramètres se trouvent dans parametres.
        En fonction de leur type on doit savoir quelle fonction appeler.

        Si aucune interprétation des types n'est possible, on lève
        une exception ValueError.

        """
        if not cls.verifier and cls._parametres_possibles:
            return list(cls._parametres_possibles.values())[0]

        ty_p = [type(p) for p in parametres]
        for types, methode in cls._parametres_possibles.items():
            if len(types) == len(ty_p) and all(issubclass(p, t) for p, t in \
                    zip(ty_p, types)):
                return methode

        raise ValueError("Aucune interprétation de la fonction {} " \
                "avec les paramètres {} n'est possible (types {}).".format(
                cls.nom, parametres, ty_p))

    @classmethod
    def convertir_types(cls):
        """Convertit les types de _parametres_possibles.

        Ils sont à l'origine au format str, on va chercher à quel type
        ils correspondent.

        """
        for str_types, methode in tuple(cls._parametres_possibles.items()):
            types = __import__("primaires.scripting.types").scripting.types
            s_types = [types.get(t) for t in str_types]
            del cls._parametres_possibles[str_types]
            cls._parametres_possibles[tuple(s_types)] = methode

    @classmethod
    def enregistrer_stats(cls, t1, t2):
        """Enregistre le temps d'exécution de la fonction."""
        diff = t2 - t1
        module = importeur.scripting
        if diff <= module.tps_fonctions:
            if module.nb_moy_fonctions == 0:
                module.nb_moy_fonctions = 1
                module.moy_fonctions = diff
            else:
                module.moy_fonctions = (module.moy_fonctions * \
                        module.nb_moy_fonctions + diff) / (module.nb_moy_fonctions \
                        + 1)
                module.nb_moy_fonctions += 1
        else:
            module.nb_exc_fonctions += 1
            ancien_diff = module.exc_fonctions.get(cls.nom, -1)
            if ancien_diff < diff:
                module.exc_fonctions[cls.nom] = diff
