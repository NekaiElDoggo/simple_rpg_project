let joueur = null;
let monstre = null;
let equipement = {
    "Armes": null,
    "Plastron": null,
    "Casque": null,
    "Bottes": null
};
let loot = [];
let combatLog = [];

function initialiserJeu(j, m) {
    joueur = j;
    monstre = m;
    afficherInfosJoueur();
    afficherMonstre();
    document.getElementById('btn_combat').style.display = "none";
    document.getElementById('btn_terminer').style.display = "none";
    document.getElementById('btn_rencontrer').style.display = "inline-block";
    document.getElementById('loot_zone').innerHTML = "";
    document.getElementById('combat_log').innerHTML = "";
    document.getElementById('resultat').innerText = "";
}

function rencontrerMonstre() {
    fetch(window.location.pathname + "?rencontrer=1")
        .then(r => r.json())
        .then(data => {
            monstre = data.monstre;
            afficherMonstre();
            document.getElementById('btn_combat').style.display = "inline-block";
            document.getElementById('btn_combat').disabled = false;
            document.getElementById('btn_rencontrer').style.display = "none";
            document.getElementById('combat_log').innerHTML = "";
            document.getElementById('resultat').innerText = "";
            document.getElementById('loot_zone').innerHTML = "";
        });
}

function afficherMonstre() {
    document.getElementById('nom_monstre').innerText = monstre.nom;
    document.getElementById('pv_monstre').innerText = monstre.pv;
    document.getElementById('force_monstre').innerText = monstre.force;
    document.getElementById('def_monstre').innerText = monstre.defense;
    document.getElementById('xp_monstre').innerText = monstre.xp;
    document.getElementById('or_monstre').innerText = monstre.or;
}

function afficherInfosJoueur() {
    recalculerStatsJoueur();
    document.getElementById('niveau_joueur').innerText = joueur.niveau;
    // Calcul de l'XP à atteindre pour le prochain niveau
    let xpMax = 100 * joueur.niveau;
    document.getElementById('xp_joueur').innerText = `${joueur.xp} / ${xpMax}`;
    document.getElementById('pv_joueur').innerText = joueur.pv;
    document.getElementById('pvmax_joueur').innerText = joueur.pvmax;
    document.getElementById('force_joueur').innerText = joueur.force;
    document.getElementById('def_joueur').innerText = joueur.defense;
    document.getElementById('or_joueur').innerText = joueur.or;
    for (let cat in equipement) {
        let eq = equipement[cat];
        let txt = "-";
        if (eq) {
            txt = eq.nom;
            let stats = [];
            if (eq.pv) stats.push(`PV: ${eq.pv}`);
            if (eq.degats) stats.push(`Attaque: ${eq.degats}`);
            if (eq.defense) stats.push(`Déf: ${eq.defense}`);
            if (stats.length) txt += " [ " + stats.join(", ") + " ]";
        }
        document.getElementById('eq_' + cat).innerText = cat.replace(/s$/, "") + " : " + txt;
    }
}

function tourDeCombat() {
    fetch('/api/combat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({joueur: joueur, monstre: monstre})
    })
    .then(r => r.json())
    .then(data => {
        combatLog = data.log;
        joueur = data.joueur;
        monstre = data.monstre;
        loot = data.loot;
        afficherCombat();
        if (data.resultat === "victoire") {
            afficherLoot();
        }
        document.getElementById('btn_combat').style.display = "none";
        document.getElementById('btn_combat').disabled = true;
        document.getElementById('btn_terminer').style.display = "inline-block";
    });
}

function afficherCombat() {
    let logDiv = document.getElementById('combat_log');
    logDiv.innerHTML = '';
    combatLog.forEach((tour, i) => {
        logDiv.innerHTML += `<div>Tour ${i+1} : Joueur inflige ${tour.degats_joueur} | Monstre inflige ${tour.degats_monstre} (PV Joueur : ${tour.joueur_pv}, PV Monstre : ${tour.monstre_pv})</div>`;
    });
    document.getElementById('resultat').innerText = joueur.pv > 0 ? "Victoire !" : "Défaite...";
    afficherInfosJoueur();
    afficherMonstre();
}

function afficherLoot() {
    let zone = document.getElementById('loot_zone');
    zone.innerHTML = "<h3>Loots :</h3>";
    loot.forEach((l, idx) => {
        if (l.type === "gold") {
            zone.innerHTML += `<div>Or : +${l.quantite}</div>`;
            joueur.or = (joueur.or || 0) + l.quantite;
        } else if (l.type === "item") {
            let cat = l.objet.categorie || devinerCategorie(l.objet.nom);
            let txt = l.objet.nom;
            let stats = [];
            if (l.objet.pv) stats.push(`PV: ${l.objet.pv}`);
            if (l.objet.degats) stats.push(`Attaque: ${l.objet.degats}`);
            if (l.objet.defense) stats.push(`Déf: ${l.objet.defense}`);
            if (stats.length) txt += " [ " + stats.join(", ") + " ]";
            zone.innerHTML += `<div>${txt} <button onclick="equiperItem(${idx}, '${cat}')">Équiper</button></div>`;
        }
    });
}

function devinerCategorie(nom) {
    if (nom.includes("Plastron") || nom.includes("Tunique") || nom.includes("Cuirasse")) return "Plastron";
    if (nom.includes("Casque") || nom.includes("Heaume") || nom.includes("Coiffe")) return "Casque";
    if (nom.includes("Bottes") || nom.includes("Grèves") || nom.includes("Souliers")) return "Bottes";
    return "Armes";
}

function equiperItem(idx, cat) {
    equipement[cat] = loot[idx].objet;
    recalculerStatsJoueur();
    afficherInfosJoueur();
    // Désactive tous les boutons "Équiper"
    document.querySelectorAll('#loot_zone button').forEach(btn => {
        btn.disabled = true;
        btn.innerText = "Déjà équipé";
    });
    // Affiche "Équipé !" sur le bouton choisi
    let btn = document.querySelectorAll('#loot_zone button')[idx];
    if (btn) btn.innerText = "Équipé !";
}

function terminerCombat() {
    joueur.pv = joueur.pvmax;
    afficherInfosJoueur();
    document.getElementById('btn_terminer').style.display = "none";
    document.getElementById('btn_rencontrer').style.display = "inline-block";
    document.getElementById('loot_zone').innerHTML = "";
    document.getElementById('combat_log').innerHTML = "";
    document.getElementById('resultat').innerText = "";
}

function recalculerStatsJoueur() {
    // Valeurs de base
    let base = joueur.base || {pvmax: 100, force: 10, defense: 0};
    let pvmax = base.pvmax;
    let force = base.force;
    let defense = base.defense;

    for (let cat in equipement) {
        let eq = equipement[cat];
        if (!eq) continue;
        if (eq.pv) pvmax += eq.pv;
        if (eq.degats) force += eq.degats;
        if (eq.defense) defense += eq.defense;
    }
    joueur.pvmax = pvmax;
    joueur.force = force;
    joueur.defense = defense;
    if (joueur.pv > pvmax) joueur.pv = pvmax;
}