from flask import Flask, request, render_template
from pprint import pprint
import random
app = Flask(__name__)

# Definition des differents tableaus pour les instances de jeu (monstre, joueur, item, etc)
noms_par_difficulte = {
    1: ["Blob", "Rat Affamé", "Fourmi Géante", "Champignon Sauteur", "Limace Gluante"],
    2: ["Chauve-souris", "Crabe de Sable", "Slime Acide", "Souris Mutante", "Corbeau Noir"],
    3: ["Loup Affamé", "Araignée Rouge", "Chien Squelette", "Gobelin Farceur", "Troll des Bois"],
    4: ["Zombie", "Serpent des Marais", "Harpie", "Esprit Mineur", "Coffre Piégé"],
    5: ["Squelette Guerrier", "Orc", "Spectre", "Loup Fantôme", "Myconide"],
    6: ["Troll des Cavernes", "Goule", "Chimère Mineure", "Gardien de Pierre", "Mage Sombre"],
    7: ["Golem", "Chien Infernal", "Minotaure", "Vampire Novice", "Cyclope"],
    8: ["Garde Draconique", "Gargouille", "Nécromancien", "Basilic", "Golem de Fer"],
    9: ["Dragonnet", "Seigneur Vampire", "Titan d'Ébène", "Sphinx", "Béhémoth"],
    10: ["Seigneur Démon", "Dragon Ancestral", "Liche Immortelle", "Avatar du Chaos", "Garde du Néant"]
}


def generer_monstres():
    base_pv = 15
    base_force = 3
    base_def = 1
    base_xp = 2

    facteur_pv = 1.8
    facteur_force = 1.5
    facteur_def = 1.3
    facteur_xp = 2.0

    monstres = []

    for difficulte in range(1, 11):
        for nom in noms_par_difficulte[difficulte]:
            pv = int(base_pv * (facteur_pv ** difficulte) + random.randint(-5, 5))
            force = int(base_force * (facteur_force ** difficulte) + random.randint(-1, 1))
            defense = int(base_def * (facteur_def ** difficulte) + random.randint(-1, 1))
            xp = int(base_xp * (facteur_xp ** difficulte))

            monstres.append({
                "nom": nom,
                "pv": max(1, pv),
                "force": max(1, force),
                "defense": max(0, defense),
                "xp": xp,
                "difficulte": difficulte
            })

    return monstres


# Exemple d'utilisation


pprint(generer_monstres())


@app.route('/main_menu', methods=['GET', 'POST'])
def main_menu():  # put application's code here
    # Recuperer la données cookie "pseudo" , si elle n'existe pas, demander à l'utilisateur de la saisir et redirige vers la page de jeu
    pseudo = request.cookies.get('pseudo')
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        if pseudo:
            # Enregistrer le pseudo dans un cookie
            resp = app.make_response(render_template('main_game.html', pseudo=pseudo))
            resp.set_cookie('pseudo', pseudo)
            return resp
        else:
            return render_template('main_menu.html', error="Veuillez saisir un pseudo")

    return render_template('main_menu.html', pseudo=pseudo)


@app.route('/main_game', methods=['GET', 'POST'])
def main_game():
    # Récupérer le pseudo depuis le cookie
    pseudo = request.cookies.get('pseudo')
    if not pseudo:
        return render_template('main_menu.html', error="Veuillez saisir un pseudo")

    return render_template('main_game.html', pseudo=pseudo)


if __name__ == '__main__':
    app.run()
