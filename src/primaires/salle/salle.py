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


"""Fichier contenant la classe Salle, détaillée plus bas."""

from collections import OrderedDict
from fractions import Fraction

from abstraits.obase import BaseObj
from bases.collections.flags import Flags
from primaires.affection.affection import Affection
from primaires.format.description import Description
from primaires.format.fonctions import supprimer_accents
from primaires.scripting.structure import StructureSimple
from primaires.vehicule.vecteur import Vecteur
from .bonhomme_neige import *
from .chemin import Chemin
from .chemins import Chemins
from .coordonnees import Coordonnees
from .decor import Decor
from .details import Details
from .objets_sol import ObjetsSol
from .sortie import Sortie
from .sorties import Sorties, NOMS_SORTIES
from .script import ScriptSalle

# Constantes
ZONE_VALIDE = r"^[a-z0-9_]{3,20}$"
MNEMONIC_VALIDE = r"^[a-z0-9_]{1,15}$"

FLAGS = Flags()
FLAGS.ajouter("anti combat", 1)
FLAGS.ajouter("anti magie", 2)
FLAGS.ajouter("invisible à distance", 4)
FLAGS.ajouter("peut boire", 64)
FLAGS.ajouter("ne peut pas boire", 128)

class Salle(BaseObj):

    """Classe représentant une salle de l'univers.

    Une salle est un élément détaillant la géographie locale d'une petite
    portion de l'univers. Bien que cela dépende des MUDs, les salles décrivent
    généralement un espace d'environ 5 mètres sur 5.

    Ces salles comportent une description détaillant les alentours proches.
    Cette description est envoyée à chaque fois qu'un personnage se déplace
    dans l'univers, pour lui donner une idée de son nouvel environnement.

    Note sur le positionnement des salles :
        Les salles peuvent être caractérisées par des coordonnées. Ces
        coordonnées sont en soi facultatives. Il est possible de créer un
        univers sans aucune coordonnée. Il s'agit d'une facilité
        lors de la constitution de votre univers qui permet à certains
        modules, comme 'vehicule', de fonctionner. Si votre salle n'a pas de
        coordonnées, vous devrez créer chaque sortie "à la main".
        Les salles ne sont donc pas identifiées par leurs coordonnées, sauf
        dans certains cas, mais bien par leur zone et mnémonique. Ce couple
        caractérise de façon unique une salle dans l'univers.
        Exemple : une salle ayant pour zone 'picte' et pour mnémonique '1'
        sera accessible depuis la clé 'picte:1' ; aucune autre salle de
        l'univers ne pourra posséder cette clé 'picte:1'.

    """

    nom_scripting = "la salle"
    _nom = "salle"
    _version = 4
    enregistrer = True

    def __init__(self, zone, mnemonic, x=0, y=0, z=0, valide=True):
        """Constructeur de la salle"""
        BaseObj.__init__(self)
        self._nom_zone = zone
        self._mnemonic = mnemonic
        self.coords = Coordonnees(x, y, z, valide, self)
        self.nom_terrain = "ville"
        self.titre = ""
        self.description = Description(parent=self)
        self.sorties = Sorties(parent=self)
        self.details = Details(parent=self)
        self._personnages = []
        self.objets_sol = ObjetsSol(parent=self)
        self.script = ScriptSalle(self)
        self.interieur = False
        self.illuminee = False
        self.magasin = None
        self.flags = 0
        self.mod_temperature = 0

        # Repop
        self.pnj_repop = {}

        # Etendue
        self.etendue = None

        # Affections
        self.affections = {}

        # Décors
        self.decors = []

        # Propriétaires de la salle (maison, cabine de bateau, etc)
        self._proprietaires = []

        self._construire()

    def __getnewargs__(self):
        return ("", "")

    def __repr__(self):
        """Affichage de la salle en mode debug"""
        return self._nom_zone + ":" + self._mnemonic

    def __str__(self):
        """Retourne l'identifiant 'zone:mnemonic'"""
        return self._nom_zone + ":" + self._mnemonic

    def _get_nom_zone(self):
        return self._nom_zone
    def _set_nom_zone(self, zone):
        prochain_ident = zone.lower() + ":" + self._mnemonic
        autre = importeur.salle.salles.get(prochain_ident)
        if autre is not None and autre is not self:
            raise ValueError("L'identifiant {} est déjà utilisé".format(
                    repr(prochain_ident)))

        ident = self.ident
        self._nom_zone = zone.lower()
        type(self).importeur.salle.changer_ident(ident, self.ident)

    def _get_mnemonic(self):
        return self._mnemonic
    def _set_mnemonic(self, mnemonic):
        prochain_ident = self._nom_zone + ":" + mnemonic.lower()
        autre = importeur.salle.salles.get(prochain_ident)
        if autre is not None and autre is not self:
            raise ValueError("L'identifiant {} est déjà utilisé".format(
                    repr(prochain_ident)))

        ident = self.ident
        self._mnemonic = mnemonic.lower()
        type(self).importeur.salle.changer_ident(ident, self.ident)

    nom_zone = property(_get_nom_zone, _set_nom_zone)
    mnemonic = property(_get_mnemonic, _set_mnemonic)

    @property
    def zone(self):
        """Retourne la zone  correspondante."""
        return type(self).importeur.salle.get_zone(self._nom_zone)

    @property
    def ident(self):
        """Retourne l'identifiant, c'est-à-dire une chaîne 'zone:mnemonic'"""
        return "{}:{}".format(self._nom_zone, self._mnemonic)

    @property
    def personnages(self):
        """Retourne une liste déférencée des personnages"""
        return list(self._personnages)

    @property
    def PNJ(self):
        """Retourne une liste déférencée des PNJ présents."""
        return [p for p in self._personnages if hasattr(p, "prototype")]

    @property
    def joueurs(self):
        """Retourne une liste déférencée des joueurs présents."""
        return [p for p in self._personnages if not hasattr(p, "prototype")]

    @property
    def exterieur(self):
        """Retourne True si la salle est extérieure, False sinon."""
        return not self.interieur

    @property
    def terrain(self):
        """Retourne l'objet terrain."""
        return importeur.salle.terrains[self.nom_terrain]

    @property
    def desc_survol(self):
        return self.terrain.desc_survol

    @property
    def str_coords(self):
        x, y, z = self.coords.tuple()
        if self.coords.valide:
            return "{}.{}.{}".format(x, y, z)

        return "Aucune"

    def get_etendue(self):
        return self.etendue

    @property
    def nom_unique(self):
        return self.ident

    @property
    def objets_uniques(self):
        """Retourne les objets uniques posés dans la salle."""
        objets = []
        for objet in self.objets_sol._objets:
            objets.append(objet)
            objets.extend(objet.prototype.objets_contenus(objet))

        return objets

    @property
    def a_magasin(self):
        """Y a-t-il un magasin dans cette salle ?"""
        return self.magasin is not None

    @property
    def nb_sorties(self):
        """Retourne le mombre de sorties."""
        sorties = [s for s in self.sorties if s and s.salle_dest]
        return len(sorties)

    @property
    def details_etendus(self):
        """Retourne la liste des détails étendus.

        Cette méthode retourne les détails de la salle et ceux des
        flottantes contenus dans la description.

        """
        details = self.details._details.copy()
        description = self.description
        for paragraphe in description.paragraphes:
            p, flottantes = description.charger_descriptions_flottantes(
                    paragraphe)
            for flottante in flottantes:
                for d in flottante.details:
                    if d.nom not in details:
                        details[d.nom] = d

        return tuple(details.values())

    @property
    def proprietaires(self):
        """Retourne les propriétaires."""
        return self._proprietaires

    @property
    def temperature(self):
        """Retourne la température de la salle."""
        zone = self.zone
        if self.interieur:
            temperature = 18
        else:
            temperature = zone.temperature

        feu = importeur.salle.feux.get(self.ident)
        if feu:
            if feu.puissance < 8:
                temperature += feu.puissance
            elif feu.puissance < 15:
                temperature = 20
            elif feu.puissance < 40:
                temperature = 25
            elif feu.puissance < 55:
                temperature = 30
            else:
                temperature = 50

        # Modification singulière de la salle
        temperature += self.mod_temperature

        # Bonus temporaires
        temperature += importeur.bonus.get(self, "temperature")

        return temperature

    def changer_terrain(self, nouveau_terrain):
        """Change le terrain de la salle."""
        nouveau_terrain = supprimer_accents(nouveau_terrain).lower()
        for terrain in importeur.salle.terrains.keys():
            sa_terrain = supprimer_accents(terrain).lower()
            if sa_terrain == nouveau_terrain:
                self.nom_terrain = terrain
                return

        raise ValueError("terrain {} inconnu".format(repr(nouveau_terrain)))

    def voit_ici(self, personnage):
        """Retourne True si le personnage peut voir ici, False sinon.

        Un personnage peut voir dans la salle si :
            Il est immortel
            La salle est illuminée
            Le personnage est un PNJ nyctalope
            Le personnage est un PNJ contrôlé par un immortel
            Il y a un feu dans la salle
            La race du personnage est nyctalope
            Le personnage a une affection qui lui permet de voir dans le noir
            La salle est en extérieure et :
                Il fait jour ou
                Le ciel est dégagé
            Une lumière est posée sur le sol
            Le personnage a une lumière

        """
        if personnage.est_immortel():
            return True

        if self.illuminee:
            return True

        if hasattr(personnage, "prototype") and \
                (personnage.prototype.a_flag("nyctalope") or \
                personnage.controle_par):
            return True

        if self.ident in importeur.salle.feux:
            return True

        # Vérification de la race
        if personnage.race and personnage.race.a_flag("nyctalope"):
            return True

        # Vérification de l'affection
        for affection in personnage.affections.values():
            if affection.affection.a_flag("voit dans le noir"):
                return True

        if not self.interieur:
            if importeur.temps.temps.il_fait_jour:
                return True

            perturbation = importeur.meteo.salles.get(self)
            if perturbation is None or not perturbation.est_opaque():
                return True

        # Vérification des lumières au sol
        for objet in self.objets_sol:
            if objet.est_de_type("lumière") and objet.allumee_depuis:
                return True

        # Vérification des lumières équipées
        for objet in personnage.equipement.equipes:
            if objet.est_de_type("lumière") and objet.allumee_depuis:
                return True

        return False

    def a_detail_flag(self, flag):
        """Retourne True si la salle a un détail du flag indiqué."""
        for detail in self.details:
            if detail.a_flag(flag):
                return True

        description = self.description
        for paragraphe in description.paragraphes:
            p, flottantes = description.charger_descriptions_flottantes(
                    paragraphe)
            for flottante in flottantes:
                for d in flottante.details:
                    if d.a_flag(flag):
                        return True

        return False

    def personnage_est_present(self, personnage):
        """Si le personnage est présent, retourne True, False sinon."""
        return personnage in self._personnages

    def a_flag(self, nom_flag):
        """Retourne True si la salle a le flag, False sinon."""
        valeur = FLAGS[nom_flag]
        return self.flags & valeur != 0

    def ajouter_personnage(self, personnage):
        """Ajoute le personnage dans la salle"""
        if personnage not in self._personnages:
            self._personnages.append(personnage)

    def retirer_personnage(self, personnage):
        """Retire le personnage des personnages présents"""
        if personnage in self.personnages:
            self._personnages.remove(personnage)

    def salles_autour(self, rayon=5):
        """Retourne les chemins autour de self dans le rayon précisé.

        Si la salle a des coordonnées valide, ajoute également
        les salles semblant proches. Cependant, pour celles-ci,
        presque aucune vérification de chemin n'est faite,
        c'est-à-dire qu'elles peuvent être entièrement inaccessible.

        """
        if self.accepte_discontinu():
            empruntable = False
        else:
            empruntable = True

        return Chemins.salles_autour(self, rayon, empruntable=empruntable)

    def trouver_chemin_absolu(self, destination, rayon=5,
            explicite=False):
        """Retourne, si trouvé, le chemin menant à destination ou None.

        Le rayon passé en argument est celui de recherche. Plus il est
        élevé, plus le temps de calcul risque d'être important.

        """
        chemins = Chemins.salles_autour(self, rayon, absolu=True)
        chemin = chemins.get(destination)
        if chemin is None and explicite:
            raise ValueError("le chemin absolu est introuvable")

        return chemin

    def trouver_chemin(self, destination, explicite=False):
        """Recherche et retourne le chemin entre deux salles.

        Plusieurs algorithmes de recherche sont utilisés en fonction
        des situations. Pour des raisons de performance, certains sont
        plus efficaces que d'autres.

        Avant tout, plusieurs chemins peuvent être retournés :
        *   Un chemin continue (toutes les salles entre deux points)
        *   Un chemin discontinu (ou brisé).

        La grande différence est qu'un personnage peut emprunter
        un chemin continu pour aller d'une salle à une autre, mais
        ne peut pas emprunter un chemin discontinu. Les chemins
        discontinus ne sont pas tolérés par défaut (ceci est réglable).

        La recherche du chemin (continu ou discontinu) fait ensuite
        appel à deux algorithmes :
        *   Si les coordonnées des deux salles sont valides, cherche le
            chemin relatifs (Chemin.salles_entre)
        *   Sinon, cherche le chemin absolu (toutes les salles
            autour de la première salle dans un rayon d'estime).

        Si explicite est mis à True, lève une exception ValueError
        décrivant pourquoi la recherche a échouée.

        """
        # Si l'une des salles n'a pas de coordonnées valide
        if self.coords.invalide or destination.coords.invalide:
            return self.trouver_chemin_absolu(destination, 4,
                    explicite=explicite)

        # Les deux salles ont des coordonnées valides
        # On vérifie que le rayon n'es tpas trop important
        v_origine = Vecteur(*self.coords.tuple())
        v_destination = Vecteur(*destination.coords.tuple())
        distance = (v_destination - v_origine).norme
        if distance > 25:
            if explicite:
                raise ValueError("la distance entre les deux salles " \
                        "est supérieure à 25")

            return None

        salles = Chemins.get_salles_entre(self, destination)

        # On détermine, si possible, le chemin entre chaque salle
        chemin = Chemin()
        a_salle = None
        continu = True
        for d_salle in salles:
            if a_salle is None:
                a_salle = d_salle
                continue

            d_chemin = a_salle.trouver_chemin_absolu(d_salle, 2)
            if d_chemin is None:
                continu = False
                vecteur = Vecteur(*d_salle.coords.tuple()) - \
                        Vecteur(*a_salle.coords.tuple())
                sortie = a_salle.get_sortie(vecteur, d_salle)
                chemin.sorties.append(sortie)
            else:
                chemin.sorties.extend(d_chemin.sorties)

            a_salle = d_salle

        if chemin.origine is not self or chemin.destination is not destination:
            if explicite:
                raise ValueError("le chemin retourné ne commence ou " \
                        "ne finit pas au bon endroit")

            return None

        if not continu and (not self.accepte_discontinu() or not \
                destination.accepte_discontinu()):
            if explicite:
                raise ValueError("un chemin non continu a été retourné")

            return None

        chemin.raccourcir()
        return chemin

    def accepte_discontinu(self):
        """Retourne True si cette salle supporte les chemins discontinu.

        Tsunami supporte ce type de chemin si la salle est une côte
        de l'étendue.

        """
        return self.etendue is not None

    def trouver_chemins_droits(self, rayon, dir_sortie=None, chemins=None,
            chemin=None, hook=True):
        """Cherche les chemins droits d'une salle.

        La recherche de salle peut être étendue par un hook.
        Les chemins droits veulent dire que l'on vérifie les sorties
        initiales. Par exemple, si la salle A a la sortie est menant vers
        B, on demande à la salle B ses sorties... mais on ne sélectionnera
        que les sorties de même direcition que la salle A (c'est-à-dire est
        ici).

        """
        chemins = chemins or Chemins()
        chemin = chemin or Chemin()

        # On parcourt les sorties de la salle
        for sortie in self.sorties:
            if dir_sortie is None or sortie.direction == dir_sortie:
                n_chemin = Chemin()
                n_chemin.sorties.extend(chemin.sorties)
                n_chemin.sorties.append(sortie)
                origine = n_chemin.origine
                destination = n_chemin.destination
                ancien_chemin = chemins.get(destination)
                if origine is not destination and (ancien_chemin is None or \
                        len(ancien_chemin) > len(n_chemin)):
                    # On retire l'ancien chemin si besoin
                    if ancien_chemin:
                        chemins.chemins.remove(ancien_chemin)
                    chemins.chemins.append(n_chemin)
                    if rayon > 1:
                        destination.trouver_chemins_droits(rayon - 1,
                                sortie.direction, chemins, n_chemin, False)

        if hook:
            importeur.hook["salle:trouver_chemins_droits"].executer(self,
                    chemins, rayon)
        return chemins

    def get_sortie(self, vecteur, destination):
        """Retourne une sortie en fonction du vecteur donné."""
        sortie = Sortie(vecteur.nom_direction, vecteur.nom_direction,
                        "le", destination, "", self)
        sortie.longueur = vecteur.norme
        return sortie

    def sortie_empruntable(self, sortie):
        """Retourne True si la sortie est empruntable, False sinon.

        Pour une salle standard, une sortie est empruntable si elle existe
        réellement.

        """
        return sortie.direction in self.sorties

    def envoyer(self, message, *personnages, prompt=True, mort=False,
            ignore=True, lisser=False, **kw_personnages):
        """Envoie le message aux personnages présents dans la salle.

        Les personnages dans les paramètres supplémentaires (nommés ou non)
        sont utilisés pour formatter le message et font figure d'exceptions.
        Ils ne recevront pas le message.

        """
        exceptions = personnages + tuple(kw_personnages.values()) if ignore \
                else ()
        for personnage in self.personnages:
            if personnage not in exceptions:
                if personnage.est_mort() and not mort:
                    continue

                if hasattr(personnage, "instance_connexion") and \
                        personnage.instance_connexion and not prompt:
                    personnage.instance_connexion.sans_prompt()
                personnage.envoyer(message, *personnages, lisser=lisser,
                        **kw_personnages)

    def envoyer_lisser(self, chaine, *personnages, **kw_personnages):
        """Méthode redirigeant vers envoyer mais lissant la chaîne."""
        self.envoyer(chaine, *personnages, lisser=True, **kw_personnages)

    def get_elements_observables(self, personnage):
        """Retourne une liste des éléments observables dans cette salle."""
        liste = []
        for methode in importeur.salle.details_dynamiques:
            liste.extend(methode(self, personnage))

        return liste

    def regarder(self, personnage):
        """Le personnage regarde la salle"""
        if personnage.est_mort():
            personnage << "|err|Vous êtes inconscient et ne voyez pas " \
                    "grand chose...|ff|"
            return

        if not self.voit_ici(personnage):
            personnage << "Il y fait trop sombre pour vos sens, " \
                    "l'obscurité vous environne."
            return

        res = ""
        if personnage.est_immortel():
            res += "# |rgc|" + self.nom_zone + "|ff|:|vrc|" + self.mnemonic
            res += "|ff| ({})".format(self.coords)
            res += "\n\n"
        res += "   |tit|" + (self.titre or "Une salle sans titre") + "|ff|\n"
        description = self.description.regarder(personnage, self)
        if not description:
            description = "   Vous êtes au milieu de nulle part."
        res += description + "\n"

        res_decors = []
        for nom in self.regrouper_decors():
            res_decors.append(nom.capitalize() + ".")

        if res_decors:
            res += "\n".join(res_decors) + "\n"

        plus = self.decrire_plus(personnage)
        if plus:
            res += plus + "\n"

        res_affections = []
        for affection in self.affections.values():
            message = affection.affection.message(affection)
            if message:
                res_affections.append(message)

        if res_affections:
            res += "\n".join(res_affections) + "\n"

        liste_messages = []
        flags = 0
        type(self).importeur.hook["salle:regarder"].executer(self,
                liste_messages, flags)
        if liste_messages:
            res += "\n".join(liste_messages) + "\n"

        res += "\nSorties : "
        res += self.afficher_sorties(personnage)

        # Personnages
        personnages = OrderedDict()
        # Si le personnage est un joueur, il se retrouve avec un nombre de 1
        # Si le personnage est un PNJ, on conserve son prototype avec
        # le nombre d'occurences de prototypes apparaissant
        etats = {}
        for personne in self.personnages:
            if personne is not personnage:
                if not hasattr(personne, "prototype"):
                    if personnage.peut_voir(personne):
                        personnages[personne] = 1
                else:
                    doit = importeur.hook["pnj:doit_afficher"].executer(personne)
                    if any(not flag for flag in doit):
                        continue

                    nom = personne.get_nom_etat(personnage)
                    if nom in etats:
                        prototype = etats[nom]
                        personnages[prototype] = \
                                personnages[prototype] + 1
                    else:
                        etats[nom] = personne
                        personnages[personne] = 1

        if len(personnages):
            res += "\n"

            for personne, nombre in personnages.items():
                res += "\n- {}".format(personne.get_nom_etat(
                            personnage, nombre))

        # Objets
        noms_objets = self.afficher_noms_objets()
        if len(noms_objets):
            res += "\n"
            for nom_objet in noms_objets:
                res += "\n+ {}".format(nom_objet)

        return res

    def afficher_sorties(self, personnage):
        """Affiche les sorties de la salle"""
        noms = []
        for nom in NOMS_SORTIES.keys():
            sortie = self.sorties[nom]
            if sortie:
                nom = sortie.nom

            nom_aff = self.sorties.get_nom_abrege(nom)
            if self.sorties.sortie_existe(nom):
                if sortie.porte and sortie.porte.fermee:
                    res = "[|rgc|" + nom_aff + "|ff|]"
                else:
                    res = "|vr|" + nom_aff + "|ff|"
                if sortie.cachee:
                    if personnage.est_immortel():
                        res = "|rg|(I)|ff|" + res
                    else:
                        res = " ".ljust(len(self.sorties.get_nom_abrege(
                                sortie.direction)))
            else:
                res = " ".ljust(len(nom_aff))

            noms.append(res)

        return ", ".join(noms) + "."

    def afficher_noms_objets(self):
        """Retourne les noms et états des objets sur le sol de la salle"""
        objets = []
        for o, nb in self.objets_sol.get_objets_par_nom():
            objets.append(o.get_nom_etat(nb))

        return objets

    def decrire_plus(self, personnage):
        """Ajoute un message au-dessous de la description.

        Si cette méthode retourne une chaîne non vide, alors cette chaîne
        sera ajoutée sous la description quand un personnage regardera
        la salle.

        """
        pass

    def pop_pnj(self, pnj):
        """Méthode appelée quand un PNJ pop dans la salle."""
        pro = pnj.prototype
        if pro in self.pnj_repop:
            self.pnj_repop[pro] = self.pnj_repop[pro] - 1

    def det_pnj(self, pnj):
        """Méthode appelée quand un PNJ disparaît.."""
        pro = pnj.prototype
        if pro in self.pnj_repop:
            self.pnj_repop[pro] = self.pnj_repop[pro] + 1

    def repop(self):
        """Méthode appelée à chaque repop."""
        for pro, nb in self.pnj_repop.items():
            if nb > 0:
                for i in range(nb):
                    pnj = importeur.pnj.creer_PNJ(pro, self)
                    pnj.script["repop"].executer(pnj=pnj)


    def affecte(self, cle, duree, force):
        """Affecte la salle avec une affection.

        Si l'affection est déjà présente, la force est modulée.

        """
        affection = importeur.affection.get_affection("salle", cle)
        if cle in self.affections:
            concrete = self.affections[cle]
            affection.moduler(concrete, duree, force)
        else:
            concrete = Affection(affection, self, duree, force)
            self.affections[cle] = concrete
            concrete.affection.executer_script("cree", concrete)
            concrete.prevoir_tick()

    def peut_affecter(self, cle_affection):
        """La salle self peut-elle être affectée par l'affection ?"""
        if cle_affection == "neige":
            if self.interieur:
                return False
            elif self.nom_terrain in ["aquatique", "subaquatique"]:
                return False

            sortie = self.sorties["bas"]
            if sortie:
                return False

        return True

    def tick(self):
        """Méthode appelée à chaque tick de la salle."""
        for affection in self.affections.values():
            affection.affection.dec_duree(affection)

        for cle, affection in list(self.affections.items()):
            if not affection.e_existe or affection.duree <= 0:
                del self.affections[cle]

        self.script["tick"].executer(salle=self)

    def regrouper_decors(self):
        """Regroupe les décors par nom."""
        decors = OrderedDict()
        nombres = OrderedDict()
        res = OrderedDict()
        for decor in self.decors:
            nom = decor.get_nom()
            decors[nom] = decor
            nb = nombres.get(nom, 0)
            nb += 1
            nombres[nom] = nb

        for nom, nb in nombres.items():
            decor = decors[nom]
            nom = decor.get_nom_etat(nb)
            res[nom] = decor

        return res

    def ajouter_decor(self, prototype):
        """Ajoute un décor dans la salle."""
        if isinstance(prototype, PrototypeBonhommeNeige):
            decor = BonhommeNeige(prototype, self)
        else:
            decor = Decor(prototype, self)

        self.decors.append(decor)
        return decor

    def get_decors(self, cle):
        """Retourne tous les décors ayant la clé indiquée."""
        return [d for d in self.decors if d.prototype and \
                d.prototype.cle == cle]

    def supprimer_decor(self, decor):
        """Supprime les décors indiqués."""
        self.decors.remove(decor)
        decor.detruire()

    def supprimer_decors(self, cle):
        """Supprime les décors de clé indiquée."""
        for decor in self.get_decors(cle):
            self.supprimer_decor(decor)

    def supprimer_bonhommes_neige(self):
        """Supprime les bonhommes de neige présents."""
        for decor in list(self.decors):
            if isinstance(decor, BonhommeNeige):
                self.supprimer_decor(decor)
                self.envoyer("{} se met à fondre rapidement.".format(
                        decor.get_nom().capitalize()))

    def get_structure(self):
        """Retourne la structure de la salle."""
        structure = StructureSimple()
        structure.zone = self._nom_zone
        structure.mnemonique = self._mnemonic
        structure.terrain = self.nom_terrain
        structure.titre = self.titre
        structure.interieur = Fraction(self.interieur)
        structure.illuminee = Fraction(self.illuminee)
        structure.proprietaires = list(self.proprietaires)

        # Coordonnées
        structure.coordonnees = Fraction(self.coords.valide)
        structure.x = Fraction(self.coords.x)
        structure.y = Fraction(self.coords.y)
        structure.z = Fraction(self.coords.z)
        structure.temperature = Fraction(self.temperature)
        structure.mod_temperature = Fraction(self.mod_temperature)
        structure.bonus_temperature = Fraction(importeur.bonus.get(
                self, "temperature", precision=1))
        # Flags
        flags = []
        for nom, valeur in FLAGS.items():
            if self.flags & valeur != 0:
                flags.append(nom)

        structure.flags = flags
        return structure

    def appliquer_structure(self, structure):
        """Applique la structure passée en paramètre."""
        for cle, valeur in structure.donnees.items():
            if cle == "zone":
                self.nom_zone = str(valeur)
            elif cle == "mnemonique":
                self.mnemonic = str(valeur)
            elif cle == "terrain":
                self.changer_terrain(str(valeur))
            elif cle == "titre":
                self.titre = str(valeur)
            elif cle == "interieur":
                self.interieur = bool(valeur)
            elif cle == "illuminee":
                self.illuminee = bool(valeur)
            elif cle == "proprietaires":
                proprietaires = [p for p in valeur if p]
                self.proprietaires[:] = proprietaires
            elif cle == "coordonnees":
                self.coords.valide = bool(valeur)
            elif cle == "x":
                self.coords.x = int(valeur)
            elif cle == "y":
                self.coords.y = int(valeur)
            elif cle == "z":
                self.coords.z = int(valeur)
            elif cle == "mod_temperature":
                self.mod_temperature = int(valeur)
            elif cle == "flags":
                self.flags = 0
                for nom, val in FLAGS.items():
                    if nom in valeur:
                        self.flags += val
