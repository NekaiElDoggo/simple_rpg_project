from flask import Flask, request, render_template, make_response, redirect, json, jsonify
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

loot_tables = {
    1: [
        {"type": "gold", "min": 5, "max": 15, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.20},
        {"type": "item", "categorie": "Plastron", "chance": 0.12},
        {"type": "item", "categorie": "Casque", "chance": 0.10},
        {"type": "item", "categorie": "Bottes", "chance": 0.10}
    ],
    2: [
        {"type": "gold", "min": 10, "max": 25, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.22},
        {"type": "item", "categorie": "Plastron", "chance": 0.14},
        {"type": "item", "categorie": "Casque", "chance": 0.12},
        {"type": "item", "categorie": "Bottes", "chance": 0.12}
    ],
    3: [
        {"type": "gold", "min": 15, "max": 35, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.24},
        {"type": "item", "categorie": "Plastron", "chance": 0.16},
        {"type": "item", "categorie": "Casque", "chance": 0.14},
        {"type": "item", "categorie": "Bottes", "chance": 0.14}
    ],
    4: [
        {"type": "gold", "min": 20, "max": 45, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.26},
        {"type": "item", "categorie": "Plastron", "chance": 0.18},
        {"type": "item", "categorie": "Casque", "chance": 0.15},
        {"type": "item", "categorie": "Bottes", "chance": 0.15}
    ],
    5: [
        {"type": "gold", "min": 25, "max": 60, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.28},
        {"type": "item", "categorie": "Plastron", "chance": 0.20},
        {"type": "item", "categorie": "Casque", "chance": 0.16},
        {"type": "item", "categorie": "Bottes", "chance": 0.16}
    ],
    6: [
        {"type": "gold", "min": 30, "max": 75, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.30},
        {"type": "item", "categorie": "Plastron", "chance": 0.22},
        {"type": "item", "categorie": "Casque", "chance": 0.17},
        {"type": "item", "categorie": "Bottes", "chance": 0.17}
    ],
    7: [
        {"type": "gold", "min": 40, "max": 90, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.32},
        {"type": "item", "categorie": "Plastron", "chance": 0.23},
        {"type": "item", "categorie": "Casque", "chance": 0.18},
        {"type": "item", "categorie": "Bottes", "chance": 0.18}
    ],
    8: [
        {"type": "gold", "min": 50, "max": 110, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.34},
        {"type": "item", "categorie": "Plastron", "chance": 0.24},
        {"type": "item", "categorie": "Casque", "chance": 0.19},
        {"type": "item", "categorie": "Bottes", "chance": 0.19}
    ],
    9: [
        {"type": "gold", "min": 65, "max": 130, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.36},
        {"type": "item", "categorie": "Plastron", "chance": 0.25},
        {"type": "item", "categorie": "Casque", "chance": 0.20},
        {"type": "item", "categorie": "Bottes", "chance": 0.20}
    ],
    10: [
        {"type": "gold", "min": 80, "max": 150, "chance": 1.0},
        {"type": "item", "categorie": "Armes", "chance": 0.40},
        {"type": "item", "categorie": "Plastron", "chance": 0.27},
        {"type": "item", "categorie": "Casque", "chance": 0.22},
        {"type": "item", "categorie": "Bottes", "chance": 0.22}
    ]
}

raretes = {
    "Commun":     {"couleur": "gris",   "multiplicateur": 1.0,  "chance": 0.60},
    "Inhabituel": {"couleur": "vert",   "multiplicateur": 1.1,  "chance": 0.25},
    "Rare":       {"couleur": "bleu",   "multiplicateur": 1.25, "chance": 0.10},
    "Épique":     {"couleur": "violet", "multiplicateur": 1.5,  "chance": 0.04},
    "Légendaire": {"couleur": "orange", "multiplicateur": 2.0,  "chance": 0.01}
}

def generer_monstres():
    base_pv = 15
    base_force = 3
    base_def = 1
    base_xp = 2
    base_or = 5

    facteur_pv = 1.8
    facteur_force = 1.5
    facteur_def = 1.3
    facteur_xp = 2.0
    facteur_or = 1.7  # croissance un peu plus lente que l'xp

    monstres = []

    for difficulte in range(1, 11):
        for nom in noms_par_difficulte[difficulte]:
            pv = int(base_pv * (facteur_pv ** difficulte) + random.randint(-5, 5))
            force = int(base_force * (facteur_force ** difficulte) + random.randint(-1, 1))
            defense = int(base_def * (facteur_def ** difficulte) + random.randint(-1, 1))
            xp = int(base_xp * (facteur_xp ** difficulte))

            # Calcul de l'or looté
            or_min = int(base_or * (facteur_or ** difficulte) * 0.8)
            or_max = int(base_or * (facteur_or ** difficulte) * 1.2)
            or_loot = random.randint(or_min, or_max)

            monstres.append({
                "nom": nom,
                "pv": max(1, pv),
                "force": max(1, force),
                "defense": max(0, defense),
                "xp": xp,
                "or": or_loot,
                "difficulte": difficulte
            })

    return monstres

def tirer_rarete():
    roll = random.random()
    cumul = 0
    for rarete, data in raretes.items():
        cumul += data["chance"]
        if roll <= cumul:
            return rarete
    return "Commun"

def generer_items_difficulte():
    items = {
        "Armes": [],
        "Casque": [],
        "Plastron": [],
        "Bottes": []
    }

    materiaux = [
        "Bois", "Pierre", "Fer", "Acier", "Runes",
        "Obsidienne", "Cristal", "Ombre", "Dragon", "Divin"
    ]

    types_arme = ["Dague", "Épée", "Hache", "Sabre", "Claymore", "Lame", "Katana", "Glaive"]
    types_casque = ["Casque", "Heaume", "Coiffe"]
    types_plastron = ["Plastron", "Tunique", "Cuirasse"]
    types_bottes = ["Bottes", "Grèves", "Souliers"]

    for niveau in range(1, 101):
        difficulte = (niveau - 1) // 10
        materiau = materiaux[difficulte]

        # ARMES
        for _ in range(random.randint(2, 4)):
            type_arme = random.choice(types_arme)
            rarete = tirer_rarete()
            nom = f"{type_arme} en {materiau} ({rarete})"
            coef = raretes[rarete]["multiplicateur"]
            base_degats = int(3 + niveau * 1.3 + difficulte * 1.8)
            degats = int((base_degats + random.randint(-2, 4)) * coef)
            prix = int(degats ** 2 * 0.8 + random.randint(-degats * 2, degats * 2))
            items["Armes"].append({
                "nom": nom,
                "degats": degats,
                "prix": max(0, prix),
                "requis": niveau,
                "rarete": rarete
            })

        # Plastron
        for _ in range(random.randint(1, 2)):
            type_armure = random.choice(types_plastron)
            rarete = tirer_rarete()
            nom = f"{type_armure} en {materiau} ({rarete})"
            coef = raretes[rarete]["multiplicateur"]
            pv = int((20 + niveau * 2 + random.randint(0, 10)) * coef)
            defense = int((5 + difficulte * 2 + random.randint(0, 3)) * coef)
            prix = int(pv * 2 + defense * 10)
            items["Plastron"].append({
                "nom": nom,
                "pv": pv,
                "defense": defense,
                "prix": prix,
                "requis": niveau,
                "rarete": rarete
            })

        # Casque
        for _ in range(random.randint(1, 2)):
            type_armure = random.choice(types_casque)
            rarete = tirer_rarete()
            nom = f"{type_armure} en {materiau} ({rarete})"
            coef = raretes[rarete]["multiplicateur"]
            pv = int((10 + niveau * 1.5 + random.randint(0, 6)) * coef)
            defense = int((3 + difficulte + random.randint(0, 2)) * coef)
            degats = random.choice([0, random.randint(1, 3)])
            prix = int(pv * 1.5 + defense * 8 + degats * 20)
            items["Casque"].append({
                "nom": nom,
                "pv": pv,
                "defense": defense,
                "degats": degats if degats else None,
                "prix": prix,
                "requis": niveau,
                "rarete": rarete
            })

        # Bottes
        for _ in range(random.randint(1, 2)):
            type_armure = random.choice(types_bottes)
            rarete = tirer_rarete()
            nom = f"{type_armure} en {materiau} ({rarete})"
            coef = raretes[rarete]["multiplicateur"]
            pv = int((5 + niveau + random.randint(0, 4)) * coef)
            degats = random.choice([0, 1, 2])
            prix = int(pv * 1.8 + degats * 25)
            items["Bottes"].append({
                "nom": nom,
                "pv": pv,
                "degats": degats if degats else None,
                "prix": prix,
                "requis": niveau,
                "rarete": rarete
            })

    return items

def generer_loot(monstre, loot_tables, items_par_categorie):
    loots = []
    table = loot_tables[monstre["difficulte"]]
    niveau = monstre.get("niveau", monstre["difficulte"] * 10)  # ou adapte selon ton modèle
    for ligne in table:
        if random.random() <= ligne["chance"]:
            if ligne["type"] == "gold":
                or_loot = random.randint(ligne["min"], ligne["max"])
                loots.append({"type": "gold", "quantite": or_loot})
            elif ligne["type"] == "item":
                categorie = ligne["categorie"]
                objets_possibles = [i for i in items_par_categorie.get(categorie, []) if i["requis"] <= niveau]
                if objets_possibles:
                    objet = random.choice(objets_possibles)
                    loots.append({"type": "item", "objet": objet})
    return loots

def get_difficulte_par_niveau(niveau):
    return min(10, max(1, (niveau - 1) // 10 + 1))

def get_joueur_from_cookie():
    joueur_json = request.cookies.get('joueur')
    if joueur_json:
        return json.loads(joueur_json)
    return {
        "niveau": 1,
        "xp": 0,
        "pv": 100,
        "or": 0,
        "inventaire": []
    }

def save_joueur_to_cookie(joueur, resp):
    resp.set_cookie('joueur', json.dumps(joueur))

@app.route('/main_menu', methods=['GET', 'POST'])
def main_menu():
    pseudo = request.cookies.get('pseudo')
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        if pseudo:
            resp = make_response(redirect('/main_game'))
            resp.set_cookie('pseudo', pseudo)
            joueur = {
                "niveau": 1,
                "xp": 0,
                "pv": 100,
                "or": 0,
                "inventaire": []
            }
            save_joueur_to_cookie(joueur, resp)
            return resp
        else:
            return render_template('main_menu.html', error="Veuillez saisir un pseudo")
    return render_template('main_menu.html', pseudo=pseudo)

@app.route('/main_game')
def main_game():
    pseudo = request.cookies.get('pseudo')
    if not pseudo:
        return redirect('/main_menu')
    joueur = get_joueur_from_cookie()
    difficulte = get_difficulte_par_niveau(joueur["niveau"])
    monstres = [m for m in generer_monstres() if m["difficulte"] == difficulte]
    monstre = random.choice(monstres)
    items = generer_items_difficulte()
    items_filtrés = {cat: [i for i in items[cat] if i["requis"] <= joueur["niveau"]] for cat in items}

    # Si AJAX pour rencontrer un monstre
    if request.args.get('rencontrer'):
        return jsonify({"monstre": monstre})

    return render_template('main_game.html', pseudo=pseudo, joueur=joueur, monstre=monstre, items=items_filtrés)

@app.route('/api/combat', methods=['POST'])
def api_combat():
    data = request.json
    joueur = data["joueur"]
    monstre = data["monstre"]
    log = []
    joueur_force = joueur.get("force", 10)
    joueur_def = joueur.get("defense", 0)
    monstre_force = monstre.get("force", 10)
    monstre_def = monstre.get("defense", 0)
    joueur_pv = joueur["pv"]
    monstre_pv = monstre["pv"]

    while joueur_pv > 0 and monstre_pv > 0:
        degats_joueur = max(1, joueur_force - monstre_def)
        degats_monstre = max(1, monstre_force - joueur_def)
        monstre_pv -= degats_joueur
        joueur_pv -= degats_monstre
        log.append({
            "joueur_pv": max(0, joueur_pv),
            "monstre_pv": max(0, monstre_pv),
            "degats_joueur": degats_joueur,
            "degats_monstre": degats_monstre
        })

    resultat = "victoire" if joueur_pv > 0 else "defaite"
    loot = []
    if resultat == "victoire":
        items = generer_items_difficulte()
        loot = generer_loot(monstre, loot_tables, items)
        # Ajout XP et or
        joueur["xp"] += monstre.get("xp", 0)
        joueur["or"] += monstre.get("or", 0)
        # Gestion montée de niveau (exemple simple)
        while joueur["xp"] >= 100 * joueur["niveau"]:
            joueur["xp"] -= 100 * joueur["niveau"]
            joueur["niveau"] += 1

    return jsonify({
        "resultat": resultat,
        "log": log,
        "joueur": {**joueur, "pv": max(0, joueur_pv)},
        "monstre": {**monstre, "pv": max(0, monstre_pv)},
        "loot": loot
    })

if __name__ == '__main__':
    app.run(debug=True)
