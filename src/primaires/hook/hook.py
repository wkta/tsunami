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


"""Ce fichier définit la classe Hook, détaillée plus bas."""

from bases.fonction import Fonction

class Hook:

    """Classe définissant un Hook, c'est-à-dire un évènement.

    Les hooks sont des évènements appelés dans certaines situations.
    Un hook peut avoir plusieurs callback définis.
    Il les appelle tous au moment où il s'exécute.

    Pour ajouter un évènement (callback) à l'hook, utilisez la méthode
    ajouter_evenement.

    Pour exécuter un évènement, utilisez sa méthode executer.

    Regardez l'aide de ces deux méthodes pour plus d'information.

    """

    def __init__(self, nom, aide):
        """Constructeur de l'hook."""
        self.nom = nom
        self.aide = aide
        self.__evenements = []

    @property
    def evenements(self):
        """Retourne une liste déréférencée des évènements."""
        return list(self.__evenements)

    def ajouter_evenement(self, fonction, *args, **kwargs):
        """Crée une fonction callback liée à l'évènement.

        Elle prend en paramètre :
            fonction : la fonction à appeler
            les paramètres nommés ou non à passer à cette fonction

        Note : lors de l'exécution du hook, les paramètres passés à
        la fonction sont ajoutés à ceux passés à la méthode Hook.executer.

        """
        callback = Fonction(fonction, *args, **kwargs)
        self.__evenements.append(callback)

    def executer(self, *args, **kwargs):
        """Exécution de l'hook.

        On exécute toutes les callbacks enregistrées, dans l'ordre d'ajout.

        Les paramètres passés à la fonction, nommée ou non, sont transmis
        à chaque callback.

        Cette méthode retourne une liste des réponses (c'est-à-dire une
        liste des retours de chaque callback). Certains hooks traitent
        ces réponses : par exemple, on peut imaginer un hook qui est
        appelé pour vérifier qu'un joueur a le droit d'aller dans une
        salle. Cet hook est exécuté quand le joueur demande à se
        déplacer (qu'il entre un nom de sortie). Les évènements sont
        ajoutés par différents modules (par exemple, le module secondaire
        familier va interdire à un joueur de se déplacer si il est sur le
        dos d'une monture et veut aller en intérieur). Dans ce cas, il
        suffit pour l'évènement de retourner False si le joueur ne
        peut pas se déplacer et le résultat sera traité par la méthode
        appelant l'hook.

        Il s'agit juste d'un exemple, la remontée des retours d'évènements
        peut avoir de nombreuses utilités.

        """
        retours = []
        for fonction in self.__evenements:
            retours.append(fonction.executer(*args, **kwargs))

        # Retire les None des retours
        retours = [r for r in retours if r is not None]
        return retours
