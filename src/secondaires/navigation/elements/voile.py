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


"""Fichier contenant la classe Voile, détaillée plus bas."""

from math import fabs, degrees

from bases.objet.attribut import Attribut
from primaires.vehicule.vecteur import get_direction
from secondaires.navigation.constantes import *
from .base import BaseElement

class Voile(BaseElement):

    """Classe représentant une voile.

    """

    nom_type = "voile"

    def __init__(self, cle=""):
        """Constructeur d'un type"""
        BaseElement.__init__(self, cle)
        # Attributs propres aux voiles
        self._attributs = {
            "orientation": Attribut(lambda: 5),
            "hissee": Attribut(lambda: False),
        }

    @staticmethod
    def get_nom_orientation(voile):
        """Retourne le nom de l'orientation de la voile."""
        or_voile = voile.orientation
        if -ANGLE_GRAND_LARGUE > or_voile:
            return "orientée vent arrière sur bâbord amure"
        elif or_voile > ANGLE_GRAND_LARGUE:
            return "orientée vent arrière sur tribord amure"
        elif -ANGLE_LARGUE > or_voile:
            return "orientée grand largue sur bâbord amure"
        elif or_voile > ANGLE_LARGUE:
            return "orientée grand largue sur tribord amure"
        elif -ANGLE_BON_PLEIN > or_voile:
            return "orientée au largue sur bâbord amure"
        elif or_voile > ANGLE_BON_PLEIN:
            return "orientée au largue sur tribord amure"
        elif -ANGLE_PRES > or_voile:
            return "orientée au bon plein sur bâbord amure"
        elif or_voile > ANGLE_PRES:
            return "orientée au bon plein sur tribord amure"
        elif -2 > or_voile:
            return "serrée au plus près sur bâbord amure"
        elif or_voile > 2:
            return "serrée au plus près sur tribord amure"
        else:
            return "parfaitement parallèle au pont"

    def get_description_ligne(self, personnage):
        """Retourne une description d'une ligne de l'élément."""
        if self.hissee:
            message = self.get_nom_orientation() + "."
        else:
            message = "repliée contre le mât."

        return self.nom.capitalize() + " est " + message

    def regarder(self, personnage):
        """personnage regarde self."""
        msg = BaseElement.regarder(self, personnage)
        or_voile = self.orientation
        cote = "tribord"
        if or_voile < 0:
            cote = "bâbord"
            or_voile = -or_voile

        or_voile = round(or_voile / 5) * 5
        if self.hissee:
            msg += "\nCette voile est " + self.get_nom_orientation()
            msg += " ({orientation}° {cote}).".format(
                    orientation=or_voile, cote=cote)
        else:
            msg += "\nCette voile est repliée contre le mât."

        return msg

    def facteur_orientation(self, navire, vent):
        """Retourne le facteur d'orientation de la voile."""
        allure = (navire.direction.direction - get_direction(vent)) % 360
        or_voile = -self.orientation
        if ALL_DEBOUT < allure < (360 - ALL_DEBOUT):
            angle = ANGLE_DEBOUT
        elif ALL_PRES < allure < (360 - ALL_PRES):
            angle = ANGLE_PRES
        elif ALL_BON_PLEIN < allure < (360 - ALL_BON_PLEIN):
            angle = ANGLE_BON_PLEIN
        elif ALL_LARGUE < allure < (360 - ALL_LARGUE):
            angle = ANGLE_LARGUE
        elif ALL_GRAND_LARGUE < allure < (360 - ALL_GRAND_LARGUE):
            angle = ANGLE_GRAND_LARGUE
        else:
            angle = ANGLE_ARRIERE
        if allure < 180:
            angle = -angle
        if angle == 90 and or_voile < 0:
            angle = -90

        facteur = 1 - fabs((angle - or_voile) / 20)
        if facteur < 0:
            facteur = 0

        return facteur

    def orienter(self, navire, vent):
        """Oriente la voile (meilleur angle de propulsion)."""
        vent_direction = get_direction(vent)
        allure = (navire.direction.direction - vent_direction) % 360
        or_voile = -self.orientation
        if ALL_DEBOUT < allure < (360 - ALL_DEBOUT):
            angle = ANGLE_DEBOUT
        elif ALL_PRES < allure < (360 - ALL_PRES):
            angle = ANGLE_PRES
        elif ALL_BON_PLEIN < allure < (360 - ALL_BON_PLEIN):
            angle = ANGLE_BON_PLEIN
        elif ALL_LARGUE < allure < (360 - ALL_LARGUE):
            angle = ANGLE_LARGUE
        elif ALL_GRAND_LARGUE < allure < (360 - ALL_GRAND_LARGUE):
            angle = ANGLE_GRAND_LARGUE
        else:
            angle = ANGLE_ARRIERE
        if allure < 180:
            angle = -angle
        if angle == 90 and or_voile < 0:
            angle = -90

        # On oriente la voile
        if angle < 0 and self.orientation >= 0 or \
                angle > 0 and self.orientation <= 0:
            self.orientation -= self.orientation

        if -5 < angle < 5:
            angle = 5 if angle >= 0 else -5

        self.orientation = -angle

    def pre_hisser(self, personnage):
        """Demande au personnage de pré-hisser la voile.

        Cette méthode doit être appelée avant post_hisser. Il y a
        généralement un temps (retourné par cette méthode) entre les
        deux.

        """
        salle = personnage.salle
        personnage << "Vous commencez de hisser la voile, aux prises " \
                "avec les cordages."
        personnage.etats.ajouter("hisser_voile")
        salle.envoyer("{} commence à hisser la voile, aux prises " \
                "avec les cordages", personnage)
        return 7

    def post_hisser(self, personnage):
        """Post-hisse la voile."""
        salle = personnage.salle
        if "hisser_voile" not in personnage.etats:
            return

        personnage.etats.retirer("hisser_voile")
        self.hissee = True
        personnage << "Vous hissez {}.".format(self.nom.lower())
        salle.envoyer("{{}} hisse {}.".format(self.nom.lower()),
                personnage)

    def pre_plier(self, personnage):
        """Commence à plier une voile."""
        salle = personnage.salle
        personnage << "Vous commencez de replier la voile."
        personnage.etats.ajouter("plier_voile")
        salle.envoyer("{} commence de replier la voile.", personnage)
        return 7

    def post_plier(self, personnage):
        """Post-plie la voile."""
        salle = personnage.salle
        if "plier_voile" not in personnage.etats:
            return

        personnage.etats.retirer("plier_voile")
        self.hissee = False
        personnage << "Vous pliez {}.".format(self.nom.lower())
        salle.envoyer("{{}} plie {}.".format(self.nom.lower()),
                personnage)
