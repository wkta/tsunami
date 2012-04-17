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


"""Fichier contenant la classe Test détaillée plus bas."""

import re
import traceback
from fractions import Fraction

from abstraits.obase import BaseObj
from primaires.format.fonctions import echapper_accolades
from primaires.scripting.parser import expressions
from primaires.scripting.instruction import Instruction, ErreurExecution
from primaires.scripting.constantes.connecteurs import CONNECTEURS
from primaires.scripting.utile.fonctions import *
from .alerte import Alerte

class Test(BaseObj):
    
    """Classe contenant un ensemble de tests.
    
    """
    
    def __init__(self, evenement, chaine_test=""):
        """Constructeur d'une suite de tests.
        
        Il prend en paramètre :
            evenement -- l'évènement qui possède le test
            chaine_test -- la suite de tests sous la forme d'une chaîne
        
        """
        BaseObj.__init__(self)
        self.__evenement = evenement
        self.__tests = None
        self.__instructions = []
        self.dernier_niveau = 0
        self.etape = None
        self._construire()
        
        if chaine_test:
            self.construire(chaine_test)
    
    def __getnewargs__(self):
        return (None, )
    
    def __str__(self):
        return str(self.__tests)
    
    @property
    def evenement(self):
        return self.__evenement
    
    @property
    def instructions(self):
        """Retourne une liste déréférencée des instructions."""
        return list(self.__instructions)
    
    @property
    def appelant(self):
        """Retourne l'appelant, c'est-à-dire le parent du script."""
        return self.evenement.script.parent
    
    @property
    def acteur(self):
        """Retourne l'acteur de la quête.
        
        C'est la variable personnage. Elle doit donc exister.
        
        """
        return self.evenement.espaces.variables["personnage"]
    
    def construire(self, chaine_test):
        """Construit la suite de chaînes en fonction de la chaîne.
        
        """
        # On essaye d'interpréter la suite de tests
        self.__tests = expressions["tests"].parser(chaine_test)[0]
    
    def ajouter_instruction(self, message):
        """Construit et ajoute l'instruction."""
        type_instruction = Instruction.test_interpreter(message)
        instruction = type_instruction.construire(message)
        instruction.deduire_niveau(self.dernier_niveau)
        self.dernier_niveau = instruction.get_niveau_suivant()
        self.__instructions.append(instruction)
    
    def remplacer_instruction(self, ligne, message):
        """Remplace une instruction."""
        if ligne not in range(len(self.__instructions)):
            raise IndexError("La ligne {} n'existe pas.".format(ligne))
        
        ancienne_instruction = self.__instructions[ligne]
        type_instruction = Instruction.test_interpreter(message)
        instruction = type_instruction.construire(message)
        instruction.niveau = ancienne_instruction.niveau
        self.__instructions[ligne] = instruction
    
    def tester(self, evenement):
        """Teste le test."""
        # Si le test est relié à une quête, on teste le niveau dans la quête
        etape = self.etape
        if etape:
            if not self.acteur.quetes[etape.quete.cle].peut_faire(
                    etape.quete, etape.niveau):
                return False
        
        if not self.__tests:
            return True
        
        py_code = self.__tests.code_python
        globales = self.get_globales(evenement)
        return bool(eval(py_code, globales))
    
    def get_globales(self, evenement):
        """Retourne le dictionnaire des globales d'exécution."""
        # Constitution des globales
        return {
            "actions": type(self).importeur.scripting.actions,
            "fonctions": type(self).importeur.scripting.fonctions,
            "variables": evenement.espaces.variables,
            "evt": evenement,
            "Fraction": Fraction,
            "formatter": formatter,
            "get_variables": get_variables,
        }
    
    def erreur_execution(self, message):
        """Méthode remontant l'erreur aux immortels concernés.
        
        Une alerte est créée pour remonter l'information.
        
        """
        appelant = self.appelant
        evenement = str(self.evenement.nom)
        tests = self.__tests and "si " + str(self) or "sinon"
        pile = traceback.format_exc()
        
        # Extraction de la ligne d'erreur
        reg = re.search("File \"\<string\>\", line ([0-9]+)", pile)
        if reg:
            no_ligne = int(reg.groups()[-1]) - 1
            ligne = echapper_accolades(str(self.__instructions[no_ligne - 1]))
        else:
            no_ligne = "|err|inconnue|ff|"
            ligne = "Ligne inconnue."
        
        # Création de l'alerte
        alerte = Alerte(appelant, evenement, tests, no_ligne, ligne,
                message, pile)
        type(self).importeur.scripting.alertes[alerte.no] = alerte
        
        # On informe les immortels connectés
        for joueur in type(self).importeur.connex.joueurs_connectes:
            if joueur.est_immortel():
                joueur << "|err|Une erreur s'est produite lors de " \
                        "l'exécution d'un script.\nL'alerte {} a été " \
                        "créée pour en rendre compte.|ff|".format(alerte.no)
    
    def executer_code(self, evenement, code):
        """Exécute le code passé en paramètre.
        
        Le code est sous la forme d'un générateur. On appelle donc
        la fonction next et récupère le retour (la valeur suivant
        le yield).
            Si ce retour est 0, on continue l'exécution (appel récursif).
            Si le retour est un autre nombre, on diffère l'exécutçion
            Si le retour est None, ohn s'arrête.
        
        """
        # Exécution
        try:
            ret = next(code)
        except ErreurExecution as err:
            self.erreur_execution(str(err))
        except Exception as err:
            self.erreur_execution(str(err))
        else:
            if ret is None:
                return
            
            tps = 0
            try:
                tps = int(ret)
                assert tps >= 0
            except (ValueError, AssertionError):
                pass
            
            if tps == 0:
                self.executer_script(evenement, code)
            else:
                # On diffère l'exécution du script
                nom = "script_dif<" + str(id(code)) + ">"
                importeur.diffact.ajouter_action(nom, tps,
                        self.executer_code, evenement, code)
    
    def executer_instructions(self, evenement):
        """Convertit et exécute la suite d'instructions.
        
        Pour plus de facilité, on convertit le script en Python pour l'heure 
        avant l'exécution.
        
        """
        etape = self.etape
        if etape:
            self.acteur.quetes[etape.quete.cle].deverouiller()
        
        code = "def script():\n"
        lignes = []
        instructions = self.instructions
        for instruction in instructions:
            lignes.append((" " * 4 * (instruction.niveau + 1)) + \
                    instruction.code_python)
        
        code += "\n".join(lignes)
        code += "\n    yield None"
        print("Code :", code)
        
        # Constitution des globales
        globales = self.get_globales(evenement)
        
        __builtins__["ErreurExecution"] = ErreurExecution
        __builtins__["variables"] = evenement.espaces.variables
        __builtins__["get_variables"] = get_variables
        try:
            code = exec(code, globales)
        except Exception:
            self.erreur_execution(str(err))
        else:
            code = globales['script']()
            self.executer_code(evenement, code)
        finally:
            del __builtins__["ErreurExecution"]
            del __builtins__["variables"]
            del __builtins__["get_variables"]
        
        # Si le test est relié à une quête
        if etape:
            # Si aucun verrou n'a été posé
            if not self.acteur.quetes[etape.quete.cle].verrouille:
                self.acteur.quetes.valider(etape.quete, etape.niveau)
