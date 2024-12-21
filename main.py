import db
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.context import CryptContext
import decimal
app = Flask(__name__)


def  select_solde():
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT solde FROM joueur WHERE pseudo = %s;", (session['user_nickname'],))
        solde = cur.fetchone()
        solde = solde.solde
    return solde

## Page de connexion
@app.route("/connexion/connexion")
def connexion():
    if 'user_nickname' in session:
        return redirect(url_for('accueil'))  
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
            if password_ctx.verify(mdp, res.mdp): # Alors l'utilisateur s'est connecté avec succès
                # On récupère dans une session, son solde, son avatar, son age et son pseudo
                cur.execute('SELECT solde, url_avatar FROM joueur WHERE pseudo = %s', (pseudo,))
                for res in cur:
                    session['avatar'] = res.url_avatar
                cur.execute('SELECT EXTRACT(YEAR FROM age(date_naissance)) AS age FROM joueur WHERE pseudo = %s;', (pseudo,))
                for res in cur:
                    session['age'] = res.age
                session['user_nickname'] = pseudo 
                return redirect(url_for("accueil"))
        return render_template ("/connexion/connexion.html", error = True, error_msg = "Nom d'utilisateur ou mot de passe incorrect !") ## Nom d'utilisateur incorrect

@app.route("/connexion/cree_compte", methods=['POST'])
def cree_compte():
    error_condition = False
    return render_template("/connexion/cree_compte.html", error = error_condition)

import re ## Pour le mail
import os ## Pour les avatars
import random ## Pour choisir un avatar aléatoire lors de la création du compte
@app.route("/connexion/new_compte", methods=['POST'])
def new_compte():
    ## Pour l'avatar du joueur, on récupère les images et on lui associe un avatar au hasard
    images = []
    for fichier in os.listdir('static/img/avatar/'):
        if fichier == ".DS_Store": ## Fichier sur Mac caché dans le dossier, je l'enlève 
            continue
        images.append(fichier)
    avatar = random.choice(images)
    ## On récupère toutes les informations sous forme de liste
    value_list = request.form.getlist("value") # value_list = [Pseudo, MDP, prénom et nom, mail, date de naissance]
    if any(elem == '' for elem in value_list): ## Si un élément de la liste est égale à '', alors on n'a pas remplit une case
         return render_template("/connexion/cree_compte.html", error = True, error_msg = "Veuillez remplir toutes les informations !")
    # On vérifie qu'on a bien tapé une adresse mail valide grâce au module re.match()
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value_list[3])
    if not(valid):
         return render_template("/connexion/cree_compte.html", error = True, error_msg = "Veuillez renseigner une adresse mail correcte !")
    with db.connect() as conn:
        cur = conn.cursor()
        ## On vérifie que ce pseudo n'a pas déjà été pris
        cur.execute("SELECT pseudo FROM joueur WHERE pseudo = %s;", (value_list[0],))
        for res in cur: ## Si on rentre dans cette boucle, alors on a trouvé un pseudo
            return render_template("/connexion/cree_compte.html", error = True, error_msg = "Ce pseudo a déjà été utilisé !")
        ## On hash son MDP, puis ensuite on ajoute les données dans la BDD 
        password_ctx = CryptContext(schemes=['bcrypt']) 
        hash_pw = password_ctx.hash(value_list[1])
        cur.execute('''
                    INSERT INTO joueur 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''', 
                    (value_list[0], hash_pw, value_list[2], value_list[3], value_list[4], '../static/img/avatar/' + avatar,))
    return render_template("/connexion/connexion.html", create_compte = True, msg = "Le compte a été crée avec succès !")

@app.route("/connexion/back_to_connexion", methods=['POST'])
def back_to_connexion():
    error_condition = False
    return render_template("/connexion/connexion.html", error = error_condition)


@app.route("/")
@app.route("/accueil")
def accueil():
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))       
    return render_template("/accueil.html", user = session['user_nickname'], solde = select_solde(), avatar = session['avatar'])

############################################################################################################
## Début des requêtes pour la boutique
@app.route("/boutique")
def boutique():
    ## La liste pour filtrer les jeux, on utilise un dictionnaire en raison de la méthode de GETS 
    lst_type = {
        'Date':"Date de parution",
        'Nombre':"Nombre de ventes",
        'Note':"Note moyenne"
    }
    ## On vérifie qu'une session est active
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    ## On sélectionne toutes les informations en lien avec les JEUX pour qu'on puisse les afficher sur le site 
    with db.connect() as conn:
        cur = conn.cursor()
        ## On récupère le titre, prix, date de sortie, url de l'img, la moyenne de ses notes
        cur.execute(''' SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne 
                        FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) 
                        GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img;
                    ''')
        lst_jeu = cur.fetchall()
    return render_template("/boutique.html", user = session['user_nickname'], solde = select_solde(), avatar = session['avatar'],
                           lst_jeu = lst_jeu, lst_type = lst_type.values(), default = "Trier par",  filtre = False)

@app.route("/add_filtre", methods = ['GET'])
def add_filtre():
    ## La méthode GETS renvoie seulement le 1er mot, si on selectionne "Date de parution", GETS va renvoyer "Date" seulement, d'où la raison d'un dico
    lst_type = {
        'Date':"Date de parution",
        'Nombre':"Nombre de ventes",
        'Note':"Note moyenne"
    }
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    ## On récupère la méthode de trie
    type_trie = request.args.get("type", None)
    with db.connect() as conn:
        cur = conn.cursor()
        ## En fonction de son résultat, on fait la requête approprié pour trier les jeux
        if type_trie == "Date":
            cur.execute('''
                        SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu 
                        LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img 
                        ORDER BY date_sortie DESC;
                        ''')
        if type_trie == "Nombre":
            cur.execute('''
                        SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu 
                        LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img 
                        ORDER BY count(jeu.id_jeu) DESC;
                        ''')
        if type_trie == "Note":
            cur.execute('''
                        SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu 
                        LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img 
                        ORDER BY avg(note) DESC;
                        ''')
       ## On récupère la liste des filtres
        type_default = lst_type[type_trie]
        del lst_type[type_trie] ## On supprime les filtre qu'on a appliqué pour éviter qu'on le selectionne
        lst_jeu = cur.fetchall()
    return render_template("/boutique.html", user = session['user_nickname'], solde = select_solde(), avatar = session['avatar'], 
                           lst_jeu = lst_jeu, lst_type = lst_type.values(), default = type_default, filtre = True)

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
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute('SELECT nom_genre FROM genre;')
        lst_gen = cur.fetchall()
        cur.execute('SELECT nom FROM entreprise;')
        lst_entreprise = cur.fetchall()
    return render_template("/recherche.html", user = session['user_nickname'], solde = select_solde(), avatar = session['avatar'],
                           lst_jeu = [], lst_genre = lst_gen, lst_editeur = lst_entreprise, lst_developpeur = lst_entreprise, default = ['', False, False, False])

## Pour trier les jeux en fonctions de la barre de recherche ET de ses filtres 
@app.route("/search_game", methods=['GET'])
def search_game():
    '''
    Fonction qui va permettre de faire le filtre dans la page RECHERCHE, la méthode de filtre est la suivante :
        - On récupère la lst des jeux (L1) filtré à partir de la barre de recherche.
        - A partir de cette liste L1, on va filtrer en fonction du genre cette fois ci, on obtiendra une nouvelle lst (L2)
        - A partir de cette liste L2, on va re-filtrer en fonction des Editeurs, on obtienra une nouvelle lst (L3)
        - Pareil pour les Developpeurs.
    On obtient donc une liste finale filtré en fonction des paramètres indiqués.
    Après avoir filtré, on récupère la liste des Genres, Editeurs, Dev en retirant les options sélectionnées 
    '''
    lst_gen = []
    lst_edi = []
    lst_dev = []
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    ## On récupère avec la méthode GETS, 
    titre_recherche = request.args.get("titre_recherche", None) ## GETS renvoie '' si on a pas choisit d'option
    genre = request.args.get("recherche_genre", None) ## GETS renvoie '' si on a pas choisit d'option
    editeur = request.args.get("recherche_editeur", None) ## GETS renvoie '' si on a pas choisit d'option
    dev = request.args.get("recherche_developpeur", None) ## GETS renvoie '' si on a pas choisit d'option
    with db.connect() as conn:
        cur = conn.cursor()
        ## On filtre d'abord en fonction de la barre de recherche grâce à LIKE
        cur.execute('SELECT titre FROM jeu WHERE LOWER(titre) LIKE LOWER(%s);', ("%" + titre_recherche + "%",)) ## On utilise LOWER pour négliger les majuscules
        lst_jeu = cur.fetchall() ## On récupère lst_jeu (= L1)
        ## Si genre ne renvoie pas '', alors on veut filtrer en fonction
        if (genre): 
            lst_jeu_genre = []
            ## On va filtrer mais en fonction de la liste L1 cette fois-ci
            for elem in lst_jeu:
                cur = conn.cursor()
                cur.execute('SELECT titre FROM jeu NATURAL JOIN classer NATURAL JOIN genre WHERE titre = %s AND nom_genre = %s;',(elem.titre, genre,))
                genre_result = cur.fetchone()
                ## Si on trouve un résultat, alors se titre valide la Recherche et le Genre
                if genre_result:
                    lst_jeu_genre.append(genre_result)
            ## On récupère lst_jeu (= L2)
            lst_jeu = lst_jeu_genre
        ## Pareil pour editeur
        if (editeur): 
            lst_jeu_editeur = []
            for elem in lst_jeu:
                cur = conn.cursor()
                cur.execute('SELECT titre FROM jeu WHERE titre = %s AND nom_edite = %s;', (elem.titre, editeur,))
                editeur_result = cur.fetchone()
                if editeur_result:
                    lst_jeu_editeur.append(editeur_result)
            ## On récupère lst_jeu (= L3)
            lst_jeu = lst_jeu_editeur
        ## Pareil pour dev
        if (dev):
            lst_jeu_dev = []
            for elem in lst_jeu:
                cur = conn.cursor()
                cur.execute('SELECT titre FROM jeu WHERE titre = %s AND nom_dev = %s;', (elem.titre, dev,))
                dev_result = cur.fetchone()
                if dev_result:
                    lst_jeu_dev.append(dev_result)
            ## On récupère lst_jeu (= L4)
            lst_jeu = lst_jeu_dev
        ## On a la liste avec seulement les TITRES de tout les jeux, maintenant on récupère les informations concernant le jeu
        ## (titre, prix, date_sortie, url_img, moyenne des notes)
        lst_finale = []
        for elem in lst_jeu:
            cur = conn.cursor()
            cur.execute('''
                        SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne FROM jeu 
                        LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img 
                        HAVING jeu.titre = %s;
                        ''', (elem.titre,))
            res = cur.fetchone()
            if res:
                lst_finale.append(res)
        ## Ainsi, on obtient la liste finale
        lst_jeu = lst_finale
        ##### Après avoir obtenu le résultat, on souhaite conserver sur le site les filtres qu'on y a appliqués
        ##### On récupère la liste des options, sauf qu'on va mettre l'option choisit en tête de liste
        # Genre
        cur.execute('SELECT nom_genre FROM genre WHERE nom_genre = %s;', (genre,)) # On sélectionne l'option choisis
        for res in cur:
            lst_gen.append(res)
        cur.execute('SELECT nom_genre FROM genre EXCEPT SELECT nom_genre FROM genre WHERE nom_genre = %s;', (genre,)) # On sélectionne les autres
        for res in cur:
            lst_gen.append(res) # On obtient la liste des genres, avec en tête le genre choisi
        # Editeur
        cur.execute('SELECT nom FROM entreprise WHERE nom = %s;', (editeur,))
        for res in cur:
            lst_edi.append(res)
        cur.execute('SELECT nom FROM entreprise EXCEPT SELECT nom FROM entreprise WHERE nom = %s ;', (editeur,))
        for res in cur:
            lst_edi.append(res)
        # Dev
        cur.execute('SELECT nom FROM entreprise WHERE nom = %s;', (dev,))
        for res in cur:
            lst_dev.append(res)
        cur.execute('SELECT nom FROM entreprise EXCEPT SELECT nom FROM entreprise WHERE nom = %s ;', (dev,))
        for res in cur:
            lst_dev.append(res)
        ## Si on a trouvé aucun jeu correspondant aux filtres, on affiche à l'utilisateur qu'on a trouvé aucun jeu
        if not lst_jeu:
            return render_template("/recherche.html", user = session['user_nickname'], solde = select_solde(), avatar = session['avatar'], 
                                    lst_jeu = lst_jeu, nothing = True, lst_genre = lst_gen, lst_editeur = lst_edi, 
                                    lst_developpeur = lst_dev, default = [titre_recherche, genre, editeur, dev], filtre=True)
    return render_template("/recherche.html", user = session['user_nickname'], solde = select_solde(),  avatar = session['avatar'],
                           lst_jeu = lst_jeu, lst_genre = lst_gen, lst_editeur = lst_edi, 
                           lst_developpeur = lst_dev, default = [titre_recherche, genre, editeur, dev], filtre=True)
    
@app.route("/supp_filtre_recherche")
def supp_filtre_recherche():
    return redirect(url_for('recherche'))

## Fin des requêtes pour la recherche
############################################################################################################
## Début des requêtes pour les jeux
@app.route("/game_click/<string:type>", methods=['GET'])
def game_click(type):
    """
    Fonction qui s'active lorsqu'on clique sur un jeu, on utilise la méthode GET
    pour conserver les informations sur l'url de la page 

    Args:
        type (_type_): variable de type str, qui est égale au nom du jeu
    """
    ## type = type.replace("%2F", "/")
    type = type.replace("%20", " ") ## Le caractère %20 est la touche espace convertit dans l'url, on remplace donc le caractère %20 par des ' '
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    ## On sélectionne toutes les informations en lien avec le JEU cliqué pour qu'on puisse les afficher sur le site 
    with db.connect() as conn:
        cur = conn.cursor()
        ## on récupère l'ID du jeu
        cur.execute('SELECT id_jeu FROM jeu WHERE titre = %s', (type,) )
        for res in cur:
            id_jeu = res.id_jeu
        ## On récupère le titre, prix, date de sortie, age_min, synopsis, editeur, dev, url de l'img, la moyenne de ses notes
        cur.execute('''
                    SELECT titre, prix, date_sortie, age_min, synopsis, nom_edite, nom_dev, url_img, ROUND(avg(note), 1) AS moyenne 
                    FROM jeu LEFT JOIN achat ON (jeu.id_jeu = achat.id_jeu) 
                    GROUP BY jeu.id_jeu, titre, prix, date_sortie, age_min, synopsis, nom_edite, nom_dev, url_img 
                    HAVING titre = %s;''', 
                    (type,))
        jeu = cur.fetchone()
        ## On récupère tout les genres associés à ce jeu
        cur.execute('SELECT nom_genre FROM jeu NATURAL JOIN classer NATURAL JOIN genre WHERE titre = %s', (jeu.titre,))
        lst_genre = cur.fetchall()
        ## On récupère tout les commentaires/avis de ce jeu
        cur.execute('SELECT pseudo, note, commentaire, url_avatar, date_achat FROM achat NATURAL JOIN joueur WHERE id_jeu = %s AND commentaire IS NOT NULL', (id_jeu,))
        lst_commentaire = cur.fetchall()
        ## On récupère le solde restant du joueur s'il décide d'acheter le jeu
        solde_restant = decimal.Decimal(select_solde()) - jeu.prix
        ## On récupère la liste des succès que le joueur a débloqué sur ce jeu
        cur.execute('SELECT intitule, condition, date_obtention FROM succes NATURAL JOIN debloquer WHERE id_jeu = %s AND pseudo = %s', (id_jeu, session['user_nickname'],))
        lst_succes_debloque = cur.fetchall()
        ## On récupère la liste des succès que le joueur n'a pas débloqué
        cur.execute('''
                    SELECT intitule, condition FROM succes WHERE id_jeu = %s 
                    EXCEPT SELECT intitule, condition FROM succes 
                    NATURAL JOIN debloquer WHERE id_jeu = %s AND pseudo = %s''', 
                    (id_jeu, id_jeu, session['user_nickname'],))
        lst_succes_bloque = cur.fetchall()
        nb_succes = [len(lst_succes_debloque), len(lst_succes_bloque) + len(lst_succes_debloque)]
        ## On vérifie si le jeu a été partagé à l'utilisateur ou pas
        cur.execute('SELECT pseudo1, pseudo2, id_jeu FROM partage WHERE pseudo2 = %s AND id_jeu = %s', (session['user_nickname'], id_jeu,))
        partage = cur.fetchone()
        if partage: ## Si on a trouve un truc, alors le jeu a été partagé à l'utilisateur
            return render_template("jeu.html", user = session['user_nickname'], solde=select_solde(),  avatar = session['avatar'],  
                                    partage = partage, jeu = jeu, lst_genre = lst_genre, lst_commentaire = lst_commentaire, nb_succes = nb_succes, 
                                    lst_succes_debloque = lst_succes_debloque, lst_succes_bloque = lst_succes_bloque)
        ## On vérifie si l'utilisateur a acheté le jeu
        cur.execute('SELECT pseudo, id_jeu, commentaire FROM achat WHERE pseudo = %s AND id_jeu = %s', (session['user_nickname'], id_jeu,))
        ## Si la requête ne trouve rien, alors l'utilisateur n'a pas acheté le jeu et on saute la boucle
        for res in cur:
            ## On affiche la liste des joueurs avec qui il peut partager le jeu
            ## i.e les joueurs amis avec la personne et qui ne POSSEDENT PAS LE JEU (Via achat ou par partage)
            ## On vérifie d'abord qu'il a pas déjà partagé le jeu
            cur.execute('SELECT pseudo2 FROM partage WHERE pseudo1 = %s and id_jeu = %s;', (session['user_nickname'], id_jeu ))
            lst_joueur = cur.fetchone()
            if not(lst_joueur):
                ## On sélectionne sa liste d'ami, puis on y retire ceux qui possède le jeu ou ceux qui ont déjà le jeu partagé 
                cur.execute('''
                            SELECT pseudo1 AS pseudo, url_avatar
                            FROM ami JOIN joueur ON pseudo1 = joueur.pseudo AND pseudo2 =  %s AND statut = 1 AND EXTRACT(YEAR FROM age(date_naissance)) >= %s
                            UNION SELECT pseudo2, url_avatar
                            FROM ami JOIN joueur ON pseudo2 = joueur.pseudo AND pseudo1 =  %s AND statut = 1 AND EXTRACT(YEAR FROM age(date_naissance)) >= %s
                            EXCEPT SELECT pseudo, url_avatar FROM achat NATURAL JOIN joueur WHERE id_jeu = %s
                            EXCEPT SELECT pseudo2, url_avatar FROM partage NATURAL JOIN jeu NATURAL JOIN joueur WHERE id_jeu = %s;
                            ''',
                            (
                                session['user_nickname'], jeu.age_min,
                                session['user_nickname'], jeu.age_min,
                                id_jeu, id_jeu,))
                lst_joueur = cur.fetchall()
                already_partage = False
            else:
                already_partage = True
            ## On vérifie s'il a mit un commentaire
            if res.commentaire != None:   
                ## Si ce n'est pas le cas, alors on lui return la template pour qu'il puisse mettre un commentaire
                return render_template("jeu.html", user = session['user_nickname'], solde= select_solde(),  avatar = session['avatar'],  
                                       jeu = jeu, lst_genre = lst_genre, lst_joueur = lst_joueur, 
                                       already_partage= already_partage, already_game = True, solde_restant = solde_restant, nb_succes = nb_succes, 
                                       no_commentaire = False,lst_commentaire = lst_commentaire, lst_succes_debloque = lst_succes_debloque, 
                                       lst_succes_bloque = lst_succes_bloque)
            ## Sinon on return la template normal
            return render_template("jeu.html", user = session['user_nickname'], solde= select_solde(),  avatar = session['avatar'],
                                   jeu = jeu, lst_genre = lst_genre, lst_joueur = lst_joueur, 
                                   already_partage= already_partage, already_game = True, solde_restant = solde_restant, nb_succes = nb_succes, no_commentaire = True, 
                                   lst_commentaire = lst_commentaire, lst_succes_debloque = lst_succes_debloque, 
                                   lst_succes_bloque = lst_succes_bloque)
        ## On vérifie que l'utilisateur peut acheter le jeu
        if solde_restant < 0:  ## Si ce n'est pas le cas, on le prévient
            return render_template("jeu.html", user = session['user_nickname'], solde= select_solde(),  avatar = session['avatar'],
                                   jeu = jeu, lst_genre = lst_genre, no_money = True, solde_restant = solde_restant, nb_succes = nb_succes, 
                                   lst_commentaire = lst_commentaire, lst_succes_debloque = lst_succes_debloque, 
                                   lst_succes_bloque = lst_succes_bloque)
        ## On vérifie aussi qu'il a l'âge pour jouer, si ce n'est pas le cas, on le prévient
        elif int(session['age']) < jeu.age_min:
            return render_template("jeu.html", user = session['user_nickname'], solde= select_solde(),  avatar = session['avatar'], 
                                   jeu = jeu, lst_genre = lst_genre, no_age = True, solde_restant = solde_restant, nb_succes = nb_succes, lst_commentaire = lst_commentaire, 
                                   lst_succes_debloque = lst_succes_debloque, lst_succes_bloque = lst_succes_bloque)
    ## Si on arrive ici, alors le joueur peut acheter le jeu
    return render_template("jeu.html", user = session['user_nickname'], solde=select_solde(),  avatar = session['avatar'],  
                           jeu = jeu, lst_genre = lst_genre, solde_restant = solde_restant, nb_succes = nb_succes, lst_commentaire = lst_commentaire, 
                           lst_succes_debloque = lst_succes_debloque, lst_succes_bloque = lst_succes_bloque)

@app.route("/buy_game", methods=['POST'])
def buy_game():
    """
    Fonction qui s'active lorsqu'on appuie sur le boutton
    pour acheter un jeu, on utilise la methode POST pour
    éviter qu'on puisse acheter un jeu en passant par une URL.
    """
    ## On récupère le nom du jeu
    name = request.form.get("nom_jeu")
    ## On a convertit le nom du jeu en format URL car request.form.get ne peut pas récupérer une suite de mot
    ## Le format URL convertit les " " en "%20", donc en enlève le format URL
    name = name.replace("%20", " ")
    with db.connect() as conn:
        cur = conn.cursor()
        ## On récupère l'ID et le prix du jeu qu'on souhaite acheter 
        cur.execute('SELECT id_jeu, prix FROM jeu WHERE titre = %s;', (name,) )
        for res in cur:
            id_jeu, prix_jeu = res.id_jeu, res.prix
        ## SEULEMENT dans le cas où on veut acheter alors qu'a déjà le jeu (Si on fait un retour en arrière après avoir acheté le jeu)
        cur.execute('SELECT id_jeu, pseudo FROM achat WHERE id_jeu = %s AND pseudo = %s', (id_jeu, session['user_nickname']))
        for res in cur:
            return redirect(url_for('game_click', type=name))
        ## On insère dans la table "achat", l'achat qu'on vient de faire.
        ## ATTENTION !! On n'insère pas de commentaire, ni de note dans la table "achat", lorsqu'on achète un jeu, on ne met pas un commentaire directement ...
        cur.execute('INSERT INTO achat (pseudo, id_jeu, date_achat) VALUES (%s, %s, DATE(NOW()));', (session['user_nickname'], id_jeu, ))
        cur.execute('UPDATE joueur SET solde = %s WHERE pseudo = %s;', (decimal.Decimal(select_solde()) - prix_jeu, session['user_nickname'], ))
    name = name.replace(" ", "%20")
    return redirect(url_for('game_click', type=name))

@app.route("/send_commentaire", methods=['POST'])
def send_commentaire():
    '''
    Fonction qui permet de mettre un commentaire sur un jeu
    Cette fonction est appelé seulement si l'utilisateur a déjà le jeu 
    
    ATTENTION !! On appelle aussi cette fonction pour mettre à jour le commentaire et la note
    la fonction pour modifier un commentaire étant la MEME, c'est inutile de créer une fonction "modif_commentaire"
    qui est la même que celle-là.
    '''
    ## On récupère le nom du jeu
    name = request.form.get("nom_jeu")
    name = name.replace("%20", " ")
    ## On récupère le commentaire et la note
    commentaire = request.form.get("commentaire")
    rate = request.form.get("note_jeu")
    with db.connect() as conn:
        cur = conn.cursor()
        ## On récupère l'ID du jeu
        cur.execute('SELECT id_jeu FROM jeu WHERE titre = %s;', (name,) )
        for res in cur:
            id_jeu = res.id_jeu
        ## On update la table achat qui contient la facture du jeu de l'utilisateur, et on ajoute son acommentaire ainsi que sa note 
        cur.execute('UPDATE achat SET commentaire = %s, note = %s WHERE pseudo = %s AND id_jeu = %s;', (commentaire, rate, session['user_nickname'], id_jeu, ))
    name = name.replace(" ", "%20")
    return redirect(url_for('game_click', type=name))

@app.route("/send_partage", methods=['POST'])
def send_partage():
    '''
    Fonction qui comme son nom l'indique, permet de
    partager un jeu avec un ami
    '''
    name = request.form.get("nom_jeu")
    name = name.replace("%20", " ")
    pseudo = request.form.get("send", None)
    with db.connect() as conn:
        cur = conn.cursor()
        ## On récupère l'ID du jeu qu'on souhaite partager
        cur.execute('SELECT id_jeu FROM jeu WHERE titre = %s;', (name,) )
        for res in cur:
            id_jeu = res.id_jeu
        ## On insère l'information dans la BDD
        cur.execute('''
                    INSERT INTO partage VALUES (%s, %s, %s, DATE(NOW()));
                    ''', 
                    (session["user_nickname"], pseudo, id_jeu,))
    name = name.replace(" ", "%20")
    return redirect(url_for('game_click', type=name))

@app.route("/stop_partage", methods=['POST'])
def stop_partage():
    '''
    Fonction qui comme son nom l'indique
    arrête le partage avec un utilisateur
    '''
    name = request.form.get("nom_jeu")
    name = name.replace("%20", " ")
    pseudo = request.form.get("send", None)
    with db.connect() as conn:
        cur = conn.cursor()
        ## On récupère l'ID du jeu qu'on souhaite partager
        cur.execute('SELECT id_jeu FROM jeu WHERE titre = %s;', (name,) )
        for res in cur:
            id_jeu = res.id_jeu
        cur.execute('''
                    DELETE FROM partage WHERE pseudo1 = %s AND pseudo2 = %s AND id_jeu = %s;
                    ''', 
                    (session["user_nickname"], pseudo, id_jeu,))
    name = name.replace(" ", "%20")
    return redirect(url_for('game_click', type=name))
## FIN des requêtes pour les jeux

############################################################################################################

## Début des requêtes pour le profil
@app.route("/profil")
def profil():
    '''
    Fonction qui va faire toutes les requêtes
    SQL pour récolter les informations concernant
    l'utilisateur.
    
    Ses amis, ses requêtes d'amis, les jeux partagés ...
    '''
    if 'user_nickname' not in session:
        return redirect(url_for('connexion'))
    with db.connect() as conn:
        cur = conn.cursor()
        ## Les infos de l'utilisateur
        cur.execute('''
                    SELECT pseudo, nom, mail, date_naissance, url_avatar
                    FROM joueur WHERE pseudo = %s;''',
                    (session['user_nickname'],))
        user_info = cur.fetchone()
        ## La liste de ses amis 
        cur.execute('''
                    SELECT DISTINCT pseudo, nom, mail, url_avatar
                    FROM ami JOIN joueur
                    ON ((joueur.pseudo = ami.pseudo1 AND  ami.pseudo2 = %s)
                    OR (joueur.pseudo = ami.pseudo2 AND  ami.pseudo1 = %s))
                    WHERE ami.statut = 1;''',
                    (session['user_nickname'], session['user_nickname'],))
        liste_ami = cur.fetchall()
        ## La liste de ses requêtes d'amis
        cur.execute('''
                    SELECT pseudo1, nom, url_avatar
                    FROM ami JOIN joueur
                    ON joueur.pseudo = ami.pseudo1
                    WHERE ami.statut = 0 AND pseudo2 = %s;
                    ''', ( session['user_nickname'],))
        liste_demande = cur.fetchall()    
        ## La liste des demandes d'amis qu'il a fait
        cur.execute('''
                    SELECT pseudo2, nom, url_avatar
                    FROM ami JOIN joueur
                    ON joueur.pseudo = ami.pseudo2
                    WHERE ami.statut = 0 AND pseudo1 = %s;
                    ''', ( session['user_nickname'],))
        lst_requete = cur.fetchall()  
        ## La liste de tous les joueurs sur le site Nuage (En retirant ceux qui sont ami, et les requêtes d'amis) 
        cur.execute('''
                    SELECT pseudo, url_avatar FROM joueur WHERE pseudo <> %s EXCEPT 
                    (SELECT pseudo1, url_avatar FROM ami NATURAL JOIN joueur WHERE pseudo2 = %s) EXCEPT 
                    (SELECT pseudo2, url_avatar FROM ami NATURAL JOIN joueur WHERE pseudo1 = %s);
                    ''', (session['user_nickname'], session['user_nickname'], session['user_nickname'],))
        lst_joueur = cur.fetchall()
        ## La liste des jeux qu'il a acheté
        cur.execute('''
                    SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne 
                    FROM jeu NATURAL JOIN achat
                    WHERE pseudo = %s GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img;
                    '''
                    , (session['user_nickname'],))
        lst_jeu = cur.fetchall()
        ## La liste des jeux qu'on lui a partagé
        cur.execute('''
                    SELECT titre, prix, date_sortie, url_img, ROUND(avg(note), 1) AS moyenne 
                    FROM partage NATURAL JOIN jeu NATURAL JOIN achat
                    WHERE pseudo2 = %s GROUP BY jeu.id_jeu, titre, prix, date_sortie, url_img;
                    '''
                    , (session['user_nickname'],))
        lst_jeu_partage = cur.fetchall()
         ## Les infos sur les jeux qu'ils possèdent
        cur.execute('''
                    SELECT joueur.pseudo, COUNT(achat.id_jeu) AS nbr FROM joueur AS joueur 
                    LEFT JOIN achat AS achat ON joueur.pseudo = achat.pseudo 
                    GROUP BY joueur.pseudo HAVING joueur.pseudo = %s;
                    ''',
                    (session['user_nickname'],))
        nbr_jeu = cur.fetchone()
        ## Les infos sur les jeux qu'on lui a partagé qu'il possède
        cur.execute('''
                    SELECT joueur.pseudo, COUNT(partage.id_jeu) AS nbr FROM joueur AS joueur 
                    LEFT JOIN partage AS partage ON joueur.pseudo = partage.pseudo2 
                    GROUP BY joueur.pseudo HAVING joueur.pseudo = %s;
                    ''',
                    (session['user_nickname'],))
        nbr_jeu_partage = cur.fetchone()
        ## La liste des jeux qu'il a partagé
        cur.execute('''
                    SELECT joueur.pseudo, COUNT(partage.id_jeu) AS nbr FROM joueur AS joueur 
                    LEFT JOIN partage AS partage ON joueur.pseudo = partage.pseudo1 
                    GROUP BY joueur.pseudo HAVING joueur.pseudo = %s;
                    ''',
                    (session['user_nickname'],))
        nbr_jeu_partage_me = cur.fetchone()
    return render_template("/profil.html", user = user_info, nbr_jeu = nbr_jeu.nbr, nbr_jeu_partage = nbr_jeu_partage.nbr, nbr_jeu_partage_me = nbr_jeu_partage_me.nbr,
                           lst_jeu = lst_jeu, lst_jeu_partage = lst_jeu_partage, solde = select_solde(), liste_ami = liste_ami,
                           liste_demande = liste_demande, lst_joueur = lst_joueur, lst_requete = lst_requete)

@app.route("/add_solde", methods=['POST'])
def add_solde():
    '''
    Fonction qui va permettre de mettre à jour le solde du joueur
    '''
    new_solde = request.form.get("solde", None)
    montant = str(int(float(new_solde) - float(select_solde())))
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE joueur SET solde = %s WHERE pseudo = %s;", (new_solde, session['user_nickname'],))
        cur.execute("INSERT INTO reapprovisionner (pseudo, date_transaction, montant) VALUES (%s, DATE(NOW()), %s);", (session['user_nickname'], montant, ))
    return redirect(url_for('profil'))
    
    
@app.route("/request_ami", methods=['POST'])
def request_ami():
    '''
    Fonction qui va permettre de gérer les requêtes d'amis
    '''
    message = request.form.get("accepter", None)
    pseudo = request.form.get("pseudo", None)
    with db.connect() as conn:
        cur = conn.cursor()
        if (message  == "True"): # Si on a accepté la requête le statut devient 1
                cur.execute('''
                            UPDATE ami
                            SET statut = 1
                            WHERE pseudo1 = %s AND pseudo2 = %s;
                            DELETE FROM ami
                            WHERE pseudo1 = %s AND pseudo2 = %s;''',
                            (pseudo, session["user_nickname"], session["user_nickname"], pseudo))
        elif (message == "False"): # Si on a refusé la requête, on supprime tout simplement la ligne
                cur.execute('''
                            DELETE FROM ami
                            WHERE pseudo1 = %s AND pseudo2 = %s;
                            ''',
                            (pseudo, session["user_nickname"],))
    return redirect(url_for('profil'))

@app.route("/send_request", methods=['POST'])
def send_request():
    '''
    Fonction qui permet l'envoie d'une demande d'ami à un joueur
    '''
    pseudo = request.form.get("send", None)
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute('''
                    INSERT INTO ami VALUES (%s, %s, 0);
                    ''', 
                    (session["user_nickname"], pseudo,))
    return redirect(url_for('profil'))

@app.route("/supp_ami", methods=['POST'])
def supp_ami():
    '''
    Fonction qui permet la suppression d'un ami.
    
    La suppression d'un ami implique la suppresion de tout les jeux
    partagés avec l'ami.
    '''
    pseudo = request.form.get("send", None)
    with db.connect() as conn:
        cur = conn.cursor()
        ## On le supprime de sa liste d'ami
        cur.execute('''
                    DELETE FROM ami WHERE pseudo1 = %s AND pseudo2 = %s
                    OR pseudo1 = %s AND pseudo2 = %s;
                    ''', 
                    (session["user_nickname"], pseudo,
                     pseudo, session["user_nickname"]))
        ## On supprime tout les jeux que l'ami a partagé à l'utilisateur
        ## ou que l'utilisateur a partagé avec l'ami
        cur.execute('''
                    DELETE FROM partage WHERE pseudo1 = %s AND pseudo2 = %s
                    OR pseudo1 = %s AND pseudo2 = %s;
                    ''', 
                    (session["user_nickname"], pseudo,
                     pseudo, session["user_nickname"]))
    return redirect(url_for('profil'))

@app.route("/disconnect", methods = ['POST'])
def disconnect():
    '''
    Fonction pour se déconnecter du compte
    on supprime toutes les sessions et on ramène
    l'utilisateur à la page de connexion
    '''
    session.pop('user_nickname', None)
    session.pop('age', None)
    session.pop('avatar', None)
    return redirect(url_for('connexion'))

if __name__ == '__main__':
  app.run()
