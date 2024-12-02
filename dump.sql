DROP TABLE IF EXISTS  entreprise CASCADE;
DROP TABLE IF EXISTS  genre CASCADE;
DROP TABLE IF EXISTS  joueur CASCADE;
DROP TABLE IF EXISTS  jeu CASCADE;
DROP TABLE IF EXISTS  succes CASCADE;
DROP TABLE IF EXISTS  classer CASCADE;
DROP TABLE IF EXISTS  reapprovisionner CASCADE;
DROP TABLE IF EXISTS  achat CASCADE;
DROP TABLE IF EXISTS  partage CASCADE;
DROP TABLE IF EXISTS  debloquer CASCADE;

CREATE TABLE entreprise(
    nom varchar(20) PRIMARY KEY,
    pays varchar(20)
);

CREATE TABLE genre(
    id_genre serial PRIMARY KEY,
    nom_genre varchar(20) NOT NULL
);

CREATE TABLE joueur(
    pseudo varchar(20) PRIMARY KEY,
    mdp varchar(100) NOT NULL,
    nom varchar(30) NOT NULL,
    mail varchar(50) NOT NULL,
    date_naissance date NOT NULL,
    solde int default 0 NOT NULL
);


CREATE TABLE jeu(
    id_jeu serial PRIMARY KEY,
    titre varchar(100) NOT NULL, --On considére qu'un jeu n'a pas forcement un titre unique
    prix numeric(5, 2) default 0 NOT NULL,
    date_sortie date NOT NULL,
    age_min numeric(2, 0) NOT NULL,
    synopsis varchar(200), 
    nom_edite varchar(20), 
    nom_dev varchar(20),
    url_img varchar(200),
    FOREIGN KEY (nom_edite) REFERENCES entreprise(nom),
    FOREIGN KEY (nom_dev) REFERENCES entreprise(nom)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE succes(
    code varchar(4) PRIMARY KEY,
    intitule varchar(30) NOT NULL,
    condition varchar(100),
    id_jeu int,
    FOREIGN KEY (id_jeu) REFERENCES jeu(id_jeu)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE classer(
    id_jeu int,
    id_genre int,
    PRIMARY KEY (id_jeu, id_genre),
    FOREIGN KEY (id_jeu) REFERENCES jeu(id_jeu),
    FOREIGN KEY (id_genre) REFERENCES genre(id_genre)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE reapprovisionner(
    id_reapprovision serial PRIMARY KEY,
    pseudo varchar(20) NOT NULL,
    date_transaction date NOT NULL,
    montant int NOT NULL,
    CONSTRAINT montant_min CHECK (montant > 0),
    FOREIGN KEY (pseudo) REFERENCES joueur(pseudo)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE achat(
    pseudo varchar(20),
    id_jeu int,
    note numeric(2, 1), -- Note sur 5 
    commentaire text,
    date_achat date NOT NULL,
    PRIMARY KEY (pseudo, id_jeu),
    CONSTRAINT noteMAX CHECK (note <= 5),
    FOREIGN KEY (pseudo) REFERENCES joueur(pseudo),
    FOREIGN KEY (id_jeu) REFERENCES jeu(id_jeu)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE partage(
    pseudo1 varchar(20),
    pseudo2 varchar(20),
    id_jeu int,
    date_partage date NOT NULL,
    PRIMARY KEY (pseudo1, pseudo2, id_jeu),
    FOREIGN KEY (pseudo1) REFERENCES joueur(pseudo),
    FOREIGN KEY (pseudo2) REFERENCES joueur(pseudo),
    FOREIGN KEY (id_jeu) REFERENCES jeu(id_jeu)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE debloquer(
    pseudo varchar(20),
    id_jeu int,
    code varchar(4),
    date_obtention date NOT NULL,
    PRIMARY KEY (pseudo, id_jeu, code),
    FOREIGN KEY (pseudo) REFERENCES joueur(pseudo),
    FOREIGN KEY (id_jeu) REFERENCES jeu(id_jeu),
    FOREIGN KEY (code) REFERENCES succes(code)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE VIEW rapport AS
(
    SELECT jour, nom_edite, titre, nb_vente, nb_partage,
           vente_jeu.nb_vente * jeu.prix AS chiffre_affaire, --le chiffre d’affaire réalisé
           moyenne_note, nb_succe
    FROM jeu NATURAL LEFT JOIN
    (
       SELECT id_jeu, date_achat AS jour, count(*) AS nb_vente, avg(note) AS moyenne_note
       FROM achat
       GROUP BY id_jeu, date_achat
    ) AS vente_jeu NATURAL LEFT JOIN
    (
        SELECT id_jeu, date_partage AS jour, count(*) AS nb_partage
        FROM partage
        GROUP BY id_jeu, date_partage
    ) AS partage_jeu NATURAL LEFT JOIN
    (
       SELECT id_jeu, date_obtention AS jour, count(*) AS nb_succe
       FROM debloquer
       GROUP BY id_jeu, date_obtention
    ) AS debloque_jeu 

);

-- Entreprises
INSERT INTO entreprise (nom, pays) VALUES
('Capcom', 'Japon'),
('Square Enix', 'Japon'),
('Bethesda', 'USA'),
('Bungie', 'USA'),
('CD Projekt', 'Pologne'),
('Naughty Dog', 'USA'),
('2K Games', 'USA'),
('Riot Games', 'USA'),
('Sega', 'Japon'),
('Gearbox Software', 'USA'),
('Project Moon', 'Corée'),
('Ubisoft Montreal', 'Canada'),
('Spike Chunsoft', 'Japon'),
('KOEI TECMO', 'Japon'),
('FromSoftware', 'Japon'),
('Ankama Games', 'France'),
('PlayStation Studio', 'USA'),
('Thomas Moon Kang', 'USA'),
('Humble Games', 'USA');

-- Genres de jeux
INSERT INTO genre (nom_genre) VALUES
('Simulation'),
('Stratégie'),
('MMORPG'),
('Survival'),
('VR'),
('Sandbox'),
('Musique'),
('Puzzle'),
('Horreur'),
('Indépendant'),
('Aventure'),
('Action'),
('RPG'),
('Multijoueur'),
('Jeu de rôle');


-- Joueurs
INSERT INTO joueur (pseudo, mdp, nom, mail, date_naissance) VALUES
('Oliver', 'oliver123', 'Oliver Grey', 'oliver@mail.com', '1992-11-01'),
('Sophia', 'sophia123', 'Sophia Black', 'sophia@mail.com', '1990-10-12'),
('Liam', 'liam123', 'Liam Turner', 'liam@mail.com', '1994-06-20'),
('Mia', 'mia123', 'Mia Lee', 'mia@mail.com', '1988-08-09'),
('Lucas', 'lucas123', 'Lucas Hall', 'lucas@mail.com', '1996-12-15'),
('Amelia', 'amelia123', 'Amelia Scott', 'amelia@mail.com', '1995-04-02'),
('Noah', 'noah123', 'Noah White', 'noah@mail.com', '1993-03-23'),
('Ava', 'ava123', 'Ava Martin', 'ava@mail.com', '1991-07-15'),
('James', 'james123', 'James Harris', 'james@mail.com', '1987-02-14'),
('Isabella', 'isabella123', 'Isabella Carter', 'isabella@mail.com', '1999-01-25');

-- Jeux
INSERT INTO jeu (titre, prix, date_sortie, age_min, synopsis, nom_edite, nom_dev, url_img) VALUES
('Lobotomy Corp', 22.99, '2018-04-18', 18, 
'Vous incarnez un manager qui a pour but de guider les Sephirah eux-mêmes chefs d''une troupe d''employés. La lobotomy corporation contient plusieurs monstre étranges qui serviront à récolter de l''énergie quitte à sacrifier des employés. Serez-vous capable de capable de génerer un maximum d''énergie avec un minimum de perte ?', 
'Project Moon', 'Project Moon', '../static/img/game_cover/LobotomyCorp.webp'),

('Danganronpa: Trigger Happy Havoc', 19.99, '2016-02-18', 16, 
'Dans une école coupée du monde extérieur, vous êtes forcé de trouver meutrier en passant par une phase d''enquête pour ensuite utiliser ces preuves pour briser les arguments erroné afin de découvrir l''identité du coupable.',
'Spike Chunsoft', 'Spike Chunsoft', '../static/img/game_cover/DanganronpaTriggerHappyHavoc.webp'),

('Fate/Samurai Remnant', 69.99, '2023-09-29', 18, 
'Dans un paisible village à l''èree d''edo au Japon, un étrange Rituel invoque plusieurs esprits héroïques du passé chacun rattaché à un maître qui leur est propre. Il est dit que celui qui arrive à venir au bout des autres servant aura son voeu exaucé.', 
'KOEI TECMO', 'KOEI TECMO', '../static/img/game_cover/FateSamuraiRemnant.webp'),

('Elden Ring', 59.99, '2022-02-25', 18, 
'Découvrez un monde brisé où règne terreur et sang. Répondez à l''appel que vous, sans-éclat, pouvez entendre et suivez votre destin en vainquant de nombreux adversaires tous plus coriaces que les autres jusqu''a devenir Seigneur d''Elden.',
'FromSoftware', 'FromSoftware', '../static/img/game_cover/EldenRing.webp'),

('Waven', 0.00, '2023-08-16', 12, 
'Le nouveau jeu d''Ankama suivant la chronologie de Wakfu ! Sélectionnez une classe, puis améliorez votre personnage via ses équipements ou sorts. Façonnez votre aventure solo ou avec vos amis dans un gameplay au tour par tour !', 
'Ankama Games', 'Ankama Games', '../static/img/game_cover/Waven.webp'),

('Limbus Company', 0.00, '2023-02-27', 18, 
'Vous êtes un manager au sein d''un troupe de 12 Sinners engagés par la Limbus Company avec comme mission de ramener le Golden Bough. Explorez les ruines de la lobotomy corporation afin de trouver votre dû.', 
'Project Moon', 'Project Moon', '../static/img/game_cover/LimbusCompany.webp'),

('Ghost of Tsushima DIRECTOR''S CUT', 59.99, '2024-03-16', 18, 
'Tracez votre propre voie dans ce jeu d''action-aventure en monde ouvert et découvrez tous ses secrets.', 
'PlayStation Studio', 'PlayStation Studio', '../static/img/game_cover/ghost-of-tsushima-directors-cut.webp'),

('One Step From EDEN', 5.99, '2020-03-26', 12, 
'Frayez-vous un chemin jusqu''à Eden à l''aide d''un deck de sorts que vous sélectionnerez au fil de votre partie. Faites des rencontres, bonnes ou mauvaises peu importe, progressez et atteignez Eden', 
'Thomas Moon Kang', 'Humble Games', '../static/img/game_cover/One-Step-From-Eden.webp'),

('Master Detective Archives: RAIN CODE Plus', 59.99, '2024-07-17', 18, 
'Yuma, un détective en formation amnésique, et Shinigami, l''esprit qui le hante, s''attaquent aux mystères non résolus.', 
'Spike Chunsoft', 'Spike Chunsoft', '../static/img/game_cover/MasterDetectiveRainCode.webp'),

('Danganronpa 2: Goodbye Despair', 19.99, '2016-04-19', 18, 
'Vos camarades de classe et vous étiez prêts à profiter du soleil, mais Monokuma est revenu pour relancer son jeu meurtrier ! Pris au piège dans une situation où il vous faut tuer ou être tué, votre seul espoir est de lever le voile sur les mystères de l''île.', 
'Spike Chunsoft', 'Spike Chunsoft', '../static/img/game_cover/DanganronpaGoodbyeDespair.webp');

-- Classer les jeux dans des genres
INSERT INTO classer (id_jeu, id_genre) VALUES
(1, 9),  -- Lobotomy Corp est un jeu d'Horreur psychologique
(2, 11), -- Danganronpa: Trigger Happy Havoc est un jeu d'aventure
(3, 12),  -- Fate/Samurai Remnant est un jeu d'action et de RPG
(3, 13),
(4, 12),  -- Elden ring est un jeu d'action et de RPG
(4, 13), 
(5, 14),  -- Waven est un jeu multi et un jeu de rôle
(5, 15), 
(6, 2), -- Limbus Company est un jeu de stratégie, un jeu d'horreur, et un RPG
(6, 9),  
(6, 13), 
(7, 11), -- Ghost of Tsushima est un jeu d'action et d'aventure
(7, 12), 
(8, 2),  -- One Step est un jeu de Stratégie, indépendant, aventure, action
(8, 10),
(8, 11),
(8, 12),
(9, 11), -- Rain Code est un jeu d'action et d'aventure
(9, 12),
(10, 11); -- Danganronpa 2 est un jeu d'aventure


-- Succès pour les jeux
INSERT INTO succes (code, intitule, condition, id_jeu) VALUES
('S011', 'Survivant', 'Survivre 7 jours dans Resident Evil 4', 1),
('S012', 'Vainqueur de la Guerre', 'Terminer tous les chapitres de Final Fantasy VII Remake', 2),
('S013', 'République Fallout', 'Construire un abri complet dans Fallout 76', 3),
('S014', 'Maître des Armes', 'Tuer 500 ennemis dans Destiny 2', 4),
('S015', 'Cyber Hacker', 'Compléter toutes les missions secondaires de Cyberpunk 2077', 5),
('S016', 'Survivant Ultime', 'Terminer le jeu sur la difficulté la plus élevée dans The Last of Us', 6),
('S017', 'Voleur', 'Voler 100 véhicules dans Borderlands 3', 7),
('S018', 'Légende', 'Obtenir tous les champions dans League of Legends', 8),
('S019', 'Turbo', 'Compléter le jeu à 100% dans Sonic the Hedgehog', 9),
('S020', 'Viking', 'Construire un village complet dans Assassin''s Creed Valhalla', 10);

-- Reapprovisionner (argent ajouté au porte-monnaie)
INSERT INTO reapprovisionner (pseudo, date_transaction, montant) VALUES
('Oliver', '2024-11-01', 300),
('Sophia', '2024-11-05', 400),
('Liam', '2024-11-10', 500),
('Mia', '2024-11-12', 600),
('Lucas', '2024-11-15', 700),
('Amelia', '2024-11-17', 800),
('Noah', '2024-11-20', 150),
('Ava', '2024-11-22', 900),
('James', '2024-11-25', 1100),
('Isabella',  '2024-11-26', 1300);

-- Achats de jeux
INSERT INTO achat (pseudo, id_jeu, note, commentaire, date_achat) VALUES
('Oliver', 1, 4.5, 'Superbes graphismes et ambiance. Bien stressant.', '2024-11-02'),
('Sophia', 1, 5.0, 'Une expérience incroyable, la meilleure des rééditions.', '2024-11-06'),
('Liam', 3, 3.8, 'Je suis encore un peu perdu dans ce monde ouvert.', '2024-11-12'),
('Mia', 4, 4.0, 'Le gameplay est top mais parfois répétitif.', '2024-11-14'),
('Lucas', 5, 4.5, 'Cyberpunk 2077 reste l''un des meilleurs jeux d''action.', '2024-11-17'),
('Amelia', 6, 4.2, 'Histoire excellente, mais la fin était décevante.', '2024-11-18'),
('Noah', 7, 4.8, 'Trop fun, un véritable jeu de tir à la Borderlands!', '2024-11-19'),
('Ava', 8, 5.0, 'Le meilleur jeu multijoueur que j''ai joué.', '2024-11-21'),
('James', 9, 3.5, 'Je l''ai trouvé un peu facile mais très mignon.', '2024-11-23'),
('Isabella', 10, 4.9, 'Un jeu vraiment bien conçu et riche en contenu.', '2024-11-25');

-- Partages de jeux entre joueurs
INSERT INTO partage (pseudo1, pseudo2, id_jeu, date_partage) VALUES
('Oliver', 'Sophia', 1, '2024-11-03'),
('Liam', 'Mia', 3, '2024-11-07'),
('Lucas', 'Amelia', 5, '2024-11-12'),
('Noah', 'Ava', 7, '2024-11-16'),
('James', 'Isabella', 9, '2024-11-22');

-- Déblocages supplémentaires de succès
INSERT INTO debloquer (pseudo, id_jeu, code, date_obtention) VALUES
('Oliver', 1, 'S011', '2024-11-04'),
('Sophia', 2, 'S012', '2024-11-07'),
('Liam', 3, 'S013', '2024-11-10'),
('Mia', 4, 'S014', '2024-11-13'),
('Lucas', 5, 'S015', '2024-11-16'),
('Amelia', 6, 'S016', '2024-11-18'),
('Noah', 7, 'S017', '2024-11-20'),
('Ava', 8, 'S018', '2024-11-22'),
('James', 9, 'S019', '2024-11-24'),
('Isabella', 10, 'S020', '2024-11-27');

