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


"""Ce fichier contient le module primaire supenr."""

import os
import pickle

from abstraits.module import *
from abstraits.id import ObjetID, est_objet_id
from abstraits.unique import Unique, est_unique

# Dossier d'enregistrement des fichiers-données
# Vous pouvez changer cette variable, ou bien spécifier l'option en
# ligne de commande
REP_ENRS = os.path.expanduser("~") + os.sep + "kassie" + os.sep + "enregistrements"

class Module(BaseModule):
    
    """Classe du module 'supenr'.
    
    Ce module gère l'enregistrement des données et leur récupération.
    Les objets enregistrés doivent dériver indirectement de
    'abstraits.id.ObjetID' (voir 'abstraits/id/__init__.py' pour plus
    d'informations) ou bien 'abstraits.unique.Unique' (voir
    'abstraits/unique/__init__.py' pour plus d'informations).
    
    Habituellement, il n'est pas nécessaire de manipuler directement
    ce module.
    Deux cas sont à distinguer :
    *   quand on manipule des ObjetID, on a juste à créer des nouveaux groupes
        d'identification.
        Lors de la configuration de 'supenr', il récupérera les différents
        fichiers-données enregistrés lors de la dernière session et les
        stockera dans l'attribut de classe 'objets' du groupe, sous la forme
        d'une liste d'objets.
    *   quand on manipule des objets Unique, le chargement des fichiers
        est à la charge des modules qui en ont besoin. Il faut pour ce faire
        utiliser la méthode 'charger' du module.
        Il est préférable d'utiliser cette méthode dans l'initialisation du
        module qui en a besoin, pas pendant la configuration.
    
    """
    
    def __init__(self, importeur):
        """Constructeur du module"""
        BaseModule.__init__(self, importeur, "supenr", "primaire")
        self.file_attente = set() # file d'attente des objets à enregistrer
        self.logger = type(self.importeur).man_logs.creer_logger("supenr", \
                "supenr")
    
    def config(self):
        """Méthode de configuration. On se base sur
        parser_cmd pour savoir si un dossier d'enregistrement
        des fichiers-données a été défini.
        Cette donnée peut également se trouver dans les données globales de
        configuration.
        
        """
        global REP_ENRS
        parser_cmd = type(self.importeur).parser_cmd
        config_globale = type(self.importeur).anaconf.get_config("globale")
        if config_globale.chemin_enregistrement:
            REP_ENRS = config_globale.chemin_enregistrement
        
        if "chemin-enregistrement" in parser_cmd.keys():
            REP_ENRS = parser_cmd["chemin-enregistrement"]
        
        # On construit le répertoire s'il n'existe pas
        if not os.path.exists(REP_ENRS):
            os.makedirs(REP_ENRS)
        
        BaseModule.config(self)
    
    def init(self):
        """Méthode d'initialisation du module.
        
        """
        global REP_ENRS
        for groupe in ObjetID.groupes.values():
            chemin = groupe.sous_rep
            chemin = REP_ENRS + os.sep + chemin
            if not os.path.exists(chemin):
                os.makedirs(chemin)
        
        BaseModule.init(self)
    
    def detruire(self):
        """Destruction du module"""
        self.file_attente.clear()
    
    def construire_rep(self, sous_rep):
        """Construit le chemin REP_ENRS / sous_rep s'il n'existe pas"""
        global REP_ENRS
        chemin = REP_ENRS + os.sep + sous_rep
        if not os.path.exists(chemin):
            os.makedirs(chemin)
    
    def enregistrer(self, objet):
        """Méthode appelée pour enregistrer un objet dans un fichier. Cette
        méthode est appelée par la méthode 'boucle' de ce module, ou par
        appel à la méthode 'enregistrer' de l'objet lui-même.
        
        """
        global REP_ENRS
        if est_objet_id(objet):
            chemin_dest = REP_ENRS + os.sep + type(objet).sous_rep
            nom_fichier = str(objet.id.id) + ".sav"
        elif est_unique(objet):
            self.construire_rep(objet._sous_rep)
            chemin_dest = REP_ENRS + os.sep + objet._sous_rep
            nom_fichier = objet._nom_fichier + ".sav"
        else:
            raise RuntimeError("L'objet {0} n'est pas un objet ID ou " \
                    "Unique. On ne peut l'enregistrer".format(objet))
        
        chemin_dest += os.sep + nom_fichier
        # On essaye d'ouvrir le fichier
        try:
            fichier_enr = open(chemin_dest, 'wb')
        except IOError as io_err:
            self.logger.warning("Le fichier {0} destiné à enregistrer {1} " \
                    "n'a pas pu être ouvert : {2}".format(chemin_dest, \
                    objet, io_err))
        else:
            pickler = pickle.Pickler(fichier_enr)
            pickler.dump(objet)
        finally:
            if "fichier_enr" in locals():
                fichier_enr.close()
    
    def detruire_fichier(self, objet):
        """Méthode appelée pour détruire le fichier contenant l'objet
        passé en paramètre.
        
        """
        global REP_ENRS
        if est_objet_id(objet):
            chemin_dest = REP_ENRS + os.sep + type(objet).sous_rep
            nom_fichier = str(objet.id.id) + ".sav"
        elif est_unique(objet):
            chemin_dest = REP_ENRS + os.sep + objet._sous_rep
            nom_fichier = objet._nom_fichier + ".sav"
        else:
            raise RuntimeError("L'objet {0} n'est pas un objet ID ou " \
                    "Unique. On ne peut l'enregistrer".format(objet))
        
        chemin_dest += os.sep + nom_fichier
        try:
            os.remove(chemin_dest)
        except OSError as os_err:
            self.logger.warning("Le fichier {0} censé enregistrer {1} " \
                    "n'a pas pu être supprimé : {2}".format(chemin_dest, \
                    objet, os_err))
    
    def vider_file_attente(self):
        """Méthode appelée pour vider la file d'attente des objets
        à enregistrer.
        
        """
        self.file_attente.clear()
    
    def boucle(self):
        """Méthode appelée à chaque tour de boucle synchro"""
        # On enregistre les objets en attente
        self.enregistrer_file_attente()
    
    def enregistrer_file_attente(self):
        """On enregistre la file d'attente. On appelle la méthode 'enregistrer'
        de chaque objet contenu dans le set 'self.file_attente'.
        
        """
        for objet in self.file_attente:
            if (est_objet_id(objet) and objet.est_initialise()) or \
                    est_unique(objet):
                self.enregistrer(objet)
        
        self.file_attente.clear()
    
    def charger(self, sous_rep, nom_fichier):
        """Charge le fichier indiqué et retourne l'objet dépicklé"""
        global REP_ENRS
        chemin_dest = REP_ENRS + os.sep + sous_rep + os.sep + nom_fichier
        objet = None
        try:
            fichier_enr = open(chemin_dest, 'rb')
        except IOError as io_err:
            self.logger.warning("Le fichier {0} n'a pas pu être ouvert " \
                    ": {1}".format(chemin_dest, io_err))
        else:
            unpickler = pickle.Unpickler(fichier_enr)
            objet = unpickler.load()
        finally:
            if "fichier_enr" in locals():
                fichier_enr.close()
        
        return objet
    
    def charger_groupe(self, groupe):
        """Cette fonction permet de charger tout un groupe d'un coup, d'un
        seul.
        Elle prend en paramètre la sous-classe d'ObjetID définissant le
        groupe.
        Elle retourne la liste des objets chargés.
        
        """
        global REP_ENRS
        chemin_dest = REP_ENRS + os.sep + groupe.sous_rep
        objets = [] # liste des objets récupérés
        if not os.path.exists(chemin_dest):
            self.logger.warning("Le dossier {0} devant contenir le groupe " \
                    "{1} n'existe pas".format(chemin_dest, groupe.groupe))
        else:
            liste_fichier = sorted(os.listdir(chemin_dest))
            for nom_fichier in liste_fichier:
                objet = self.charger(groupe.sous_rep, nom_fichier)
                if objet is not None:
                    objets.append(objet)
        
        return objets
