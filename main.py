import db
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.context import CryptContext
import random

app = Flask(__name__)

## Page de connexion
@app.route("/connexion/connexion")
def connexion():
    error_condition = False
    return render_template("/connexion/connexion.html", error = error_condition)

## Lorsqu'on appuie sur le bouton "Se connecter"
app.secret_key = b'988d6b3b992fe9df993a4cb5190fd54a785cf5549eada60c7600e7aa0b03de89'
@app.route("/connexion/login", methods = ['POST'])
def login():
    ## On récupère le pseudo et mdp, si on a rien renseigné, on renvoit erreur
    pseudo = request.form.get("pseudo")
    mdp = request.form.get("password")
    if (not pseudo) or (not mdp):
        return render_template("/connexion/connexion.html", error = True, error_msg = "Veuillez rentrer un pseudo ET un mot de passe !") ## Champs vides
    ## On se connecte à la BDD
    with db.connect() as conn:
        cur = conn.cursor()
        ## On cherche dans la BDD si le pseudo qu'on a rentré est dans la BDD
        cur.execute("SELECT pseudo, mdp FROM joueur WHERE pseudo = %s;", (pseudo,))
        for res in cur: ## Si ce n'est pas le cas, on saute la boucle for et on return Error
            # On vérifie si le mdp correspond aux mdp hashés de l'utilisateur
            password_ctx = CryptContext(schemes=['bcrypt'])
            if password_ctx.verify(mdp, res.mdp):
                # Alors l'utilisateur s'est connecté avec succès
                session['user_nickname'] = pseudo # On enregistre la session, pour éviter qu'il se reconnecte à chaque fois
                return redirect(url_for("accueil"))
        return render_template ("/connexion/connexion.html", error = True, error_msg = "Nom d'utilisateur ou mot de passe incorrect !") ## Nom d'utilisateur incorrect

@app.route("/connexion/cree_compte", methods=['POST'])
def cree_compte():
    error_condition = False
    return render_template("/connexion/cree_compte.html", error = error_condition)

## On suppose que l'adresse mail est bien tapé, et qu'on peut avoir comme nom d'utilisateur '       '
@app.route("/connexion/new_compte", methods=['POST'])
def new_compte():
    ## On récupère toutes les informations sous forme de liste
    value_list = request.form.getlist("value") # value_list = [Pseudo, MDP, prénom et nom, mail, date de naissance]
    if any(elem == '' for elem in value_list): ## Si un élément de la liste est égale à '', alors on n'a pas remplit une case
         return render_template("/connexion/cree_compte.html", error = True, error_msg = "Veuillez remplir toutes les informations !")
    with db.connect() as conn:
        cur = conn.cursor()
        ## On vérifie que ce pseudo n'a pas déjà été pris
        cur.execute("SELECT pseudo FROM joueur WHERE pseudo = %s;", (value_list[0],))
        for res in cur: ## Si on rentre dans cette boucle, alors on a trouvé un pseudo
            return render_template("/connexion/cree_compte.html", error = True, error_msg = "Ce pseudo a déjà été utilisé !")
        ## On hash son MDP, puis ensuite on ajoute les données dans la BDD 
        password_ctx = CryptContext(schemes=['bcrypt']) 
        hash_pw = password_ctx.hash(value_list[1])
        cur.execute("INSERT INTO joueur VALUES (%s, %s, %s, %s, %s)", (value_list[0], hash_pw, value_list[2], value_list[3], value_list[4],))
    return render_template("/connexion/connexion.html", create_compte = True, msg = "Le compte a été crée avec succès !")

@app.route("/connexion/back_to_connexion", methods=['POST'])
def back_to_connexion():
    error_condition = False
    return render_template("/connexion/connexion.html", error = error_condition)

@app.route("/accueil")
def accueil():
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    return render_template("/accueil.html", user = session['user_nickname'])
############################################################################################################
## Début des requêtes pour la boutique
@app.route("/boutique")
def boutique():
    lst_type = {
        'Date':"Date de parution",
        'Nombre':"Nombre de ventes",
        'Note':"Note moyenne"
    }
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute('SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img;')
        lst_jeu = cur.fetchall()
    return render_template("/boutique.html", user = session['user_nickname'], lst_jeu = lst_jeu, lst_type = lst_type.values(), default = "Trier par", filtre = False)
@app.route("/add_filtre", methods = ['GET'])
def add_filtre():
    lst_type = {
        'Date':"Date de parution",
        'Nombre':"Nombre de ventes",
        'Note':"Note moyenne"
    }
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    type_trie = request.args.get("type", None)
    with db.connect() as conn:
        cur = conn.cursor()
        if type_trie == "Date":
            cur.execute('SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img ORDER BY date_sortie DESC;')
        if type_trie == "Nombre":
            cur.execute('SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img ORDER BY count(jeu.id_jeu) DESC;')
        if type_trie == "Note":
            cur.execute('SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img ORDER BY avg(note) DESC;')
        type_default = lst_type[type_trie]
        del lst_type[type_trie]
        lst_jeu = cur.fetchall()
    return render_template("/boutique.html", user = session['user_nickname'], lst_jeu = lst_jeu, lst_type = lst_type.values(), default = type_default, filtre = True)

@app.route("/supp_filtre")
def supp_filtre():
    return redirect(url_for('boutique'))
## FIN des requêtes pour la boutique
############################################################################################################
## Début des requêtes pour la recherche
@app.route("/recherche")
def recherche():
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    return render_template("/recherche.html", user = session['user_nickname'])

""" 
@app.route("/type_game", methods = ['GET'])
def trier_type():
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    type_game = request.args.get("type",None)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute('SELECT titre FROM classer NATURAL JOIN genre NATURAL JOIN jeu WHERE nom_genre = %s;', (type_game,))
        lst_jeu = cur.fetchall()
        cur.execute('SELECT nom_genre FROM genre WHERE nom_genre <> %s;', (type_game,))
        lst_type = cur.fetchall()
    return render_template("/boutique.html", user = session['user_nickname'], lst_jeu = lst_jeu, lst_type = lst_type, default = type_game, filtre = True)

with db.connect() as conn:
    cur = conn.cursor()
    cur.execute('SELECT titre FROM jeu;')
    lst_jeu = cur.fetchall()
    cur.execute('SELECT nom_genre FROM genre;')
    lst_type = cur.fetchall()
return render_template("/recherche.html", user = session['user_nickname'], lst_jeu = lst_jeu, lst_type = lst_type, default = "Trier par", filtre = False)

"""
## Fin des requêtes pour la recherche
############################################################################################################
## Début des requêtes pour le profil
@app.route("/profil")
def profil():
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    return render_template("/profil.html", user = session['user_nickname'])

@app.route("/disconnect", methods = ['POST'])
def disconnect():
    session.pop('user_nickname', None)
    return redirect(url_for('connexion'))

if __name__ == '__main__':
  app.run()