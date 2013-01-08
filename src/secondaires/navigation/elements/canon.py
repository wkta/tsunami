# -*-coding:Utf-8 -*

# Copyright (c) 2012 LE GOFF Vincent
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


"""Fichier contenant la classe Canon, détaillée plus bas."""

from datetime import datetime
from math import *

from bases.objet.attribut import Attribut
from primaires.perso.exceptions.stat import DepassementStat
from primaires.salle.salle import Salle
from primaires.vehicule.vecteur import Vecteur
from .base import BaseElement

# Charge minimum pour que le projectile part
CHARGE_MIN = 2

class Canon(BaseElement):
    
    """Classe représentant un canon fixe sur un navire.
    
    Les canons sont soit :
    *   Des éléments statiques (définis ici)
    *   Des objets amovibles.
    
    """
    
    nom_type = "canon"
    
    def __init__(self, cle=""):
        """Constructeur d'un type"""
        BaseElement.__init__(self, cle)
        # Attributs propres aux canons
        self.charge_max = 1
        self._attributs = {
            "h_angle": Attribut(lambda: 0),
            "v_angle": Attribut(lambda: 0),
            "projectile": Attribut(lambda: None),
            "charge": Attribut(lambda: 0),
            "en_cours": Attribut(lambda: False),
            "dernier_tir": Attribut(lambda: None),
        }
    
    def facteur_charge(self):
        """Retourne le facteur de charge, en pourcent."""
        if self.charge_max == 0:
            return 0
        
        return self.charge / self.charge_max * 100
    
    def message_charge(self):
        """Retourne le message correspondant à la charge du canon."""
        messages = [
            (5, "Une explosion assez discrète se fait entendre"),
            (20, "Une explosion assez sonore retentit"),
            (50, "Une explosion assez forte fait frémir le navire"),
            (75, "Une violente détonation fait trembler le navire"),
            (75, "Une violente détonation fait trembler le navire"),
            (95, "Une détonnation assourdissante fait trembler le " \
                    "bois sous vos pieds"),
        ]
        
        facteur = self.facteur_charge()
        for t_facteur, message in messages:
            if facteur < t_facteur:
                return message
        
        return messages[-1][1]
    
    def vecteur(self):
        """Retourne le vecteur anticipé de la direction du projectile.
        
        On se base sur la charge et le poids du projectile pour estimer
        la distance à laquelle le projectile peut être tiré. On se base
        sur l'alignement pour estimer la direction du projectile.
        
        Sans le nuancer avec la direction du navire et sa position, ce
        vecteur ne peut pas être utilisé.
        
        """
        # D'abord, on calcule la longueur du vecteur (sa norme)
        vec_nul = Vecteur(0, 0, 0)
        if self.charge == 0:
            return vec_nul
        
        if self.projectile is None:
            return vec_nul
        
        norme = self.charge * 15 / self.projectile.poids_unitaire
        
        # À présent, oriente le vecteur en fonction de l'angle du canon
        vecteur = Vecteur(1, 0, 0, self)
        vecteur = norme * vecteur
        vecteur.orienter(self.h_angle)
        return vecteur
    
    def cible(self):
        """Retourne la cible du canon.
        
        La cible est soit :
            Une salle (salle de navire ou non)
            Une côte d'une étendue
            None si rien n'est trouvé comme cible.
        
        """
        # On calcul le vecteur du boulet
        direction = self.vecteur()
        
        # On le nuance avec la direction du navire
        salle = self.parent
        if salle is None:
            return (direction, None)
        
        navire = salle.navire
        if navire is None:
            return (direction, None)
        
        direction.tourner_autour_z(navire.direction.direction)
        direction = direction + navire.position
        # On récupère toutes les salles avec coordonnées
        cibles = importeur.salle._coords
        if navire.etendue:
            etendue = navire.etendue
            for o_coords, obstacle in etendue.obstacles.items():
                cibles[(o_coords + etendue.altitude)] = obstacle
        
        # On cherche les salles entre origine et destination
        origine = navire.position.tuple
        destination = direction.tuple
        sensibilite = 0.5
        entre = []
        o_x, o_y, o_z = origine
        d_x, d_y, d_z = destination
        for coords, cible in cibles.items():
            x, y, z = coords
            if x <= max(o_x, d_x) and x >= min(o_x, d_x) \
                and y <= max(o_y, d_y) and y >= min(o_y, d_y) \
                and z <= max(o_z, d_z) and z >= min(o_z, d_z):
                entre.append((coords, cible))
        
        # On parcourt les cibles dans le rectangle
        trajectoire = []
        ab = Vecteur(d_x - o_x, d_y - o_y, d_z - o_z)
        for coords, cible in entre:
            if coords == origine:
                continue
            
            x, y, z = coords
            ac = Vecteur(x - o_x, y - o_y, z - o_z)
            d = 0
            # On détermine les angles horizontaux et verticaux entre ab et ac
            alpha = radians(ab.argument() - ac.argument())
            if ab.x or ab.y:
                # angle de ab avec (O, x, y) : arctan(z/sqrt(x² + y²))
                beta_ab = atan(ab.z / sqrt(ab.x ** 2 + ab.y ** 2))
            elif ab.z < 0:
                beta_ab = radians(-90)
            else:
                beta_ab = radians(90)
            if ac.x or ac.y:
                # angle de ac avec (O, x, y) idem
                beta_ac = atan(ac.z / sqrt(ac.x ** 2 + ac.y ** 2))
            elif ac.z < 0:
                beta_ac = radians(-90)
            else:
                beta_ac = radians(90)
            beta = beta_ab - beta_ac
            # Distances horizontale et verticale entre c et ab
            mc_x = ac.norme * sin(alpha)
            mc_z = ac.norme * sin(beta)
            d = sqrt(mc_x ** 2 + mc_z ** 2)
            
            if d <= sensibilite:
                trajectoire.append((coords, cible))
        
        # Fonction retournant la distance du tuple (coords, cible)
        def distance(couple):
            coords, cible = couple
            x, y, z = coords
            v_o_salle = Vecteur(x - o_x, y - o_y, z - o_z)
            return v_o_salle.norme
        
        trajectoire = sorted(trajectoire, key=distance)
        if trajectoire:
            return (direction, trajectoire[0][1])
        
        return (direction, None)
    
    def tirer(self, auteur=None):
        """Le canon tire son projectile."""
        if self.charge == 0:
            return
        
        if self.projectile is None:
            return
        
        vecteur, cible = self.cible()
        if self.parent and self.parent.navire:
            vecteur = self.parent.navire.position - vecteur
        
        distance = vecteur.norme
        temps = distance / 15
        msg = self.message_charge()
        if self.parent:
            self.parent.envoyer(msg)
        projectile = self.projectile
        self.projectile = None
        self.dernier_tir = datetime.now()
        if temps <= 0.5:
            self.endommager(projectile, cible, auteur=auteur)
        else:
            importeur.diffact.ajouter_action("canon_" + str(id(self)),
                    temps, self.endommager, projectile, cible, auteur=auteur)
            self.en_cours = True
    
    def endommager(self, projectile, cible, auteur=None):
        """Endommage la cible."""
        self.en_cours = False
        if isinstance(cible, Salle):
            titre = cible.titre
            cible.envoyer(
                    "|rg|" + projectile.nom_singulier.capitalize() + \
                    " détonne près de vous !|ff|")
            degats = projectile.degats
            for personnage in cible.personnages:
                try:
                    personnage.stats.vitalite -= degats
                except DepassementStat:
                    personnage.mourir()
        else:
            titre = cible.desc_survol
        
        if auteur:
            auteur << "{} atteint {} !".format(projectile.nom_singulier, titre)
        importeur.objet.supprimer_objet(projectile.identifiant)