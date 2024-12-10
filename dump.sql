DROP TABLE IF EXISTS  entreprise CASCADE;
DROP TABLE IF EXISTS  genre CASCADE;
DROP TABLE IF EXISTS  joueur CASCADE;
DROP TABLE IF EXISTS  jeu CASCADE;
DROP TABLE IF EXISTS  ami CASCADE;
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
    solde numeric(4, 2) default 0 NOT NULL
);

CREATE TABLE ami(
    pseudo1 varchar(20),
    pseudo2 varchar(20),
    statut int, -- 0 = attente ; 1 = accepté 
    PRIMARY KEY (pseudo1, pseudo2),
    FOREIGN KEY (pseudo1) REFERENCES joueur(pseudo),
    FOREIGN KEY (pseudo2) REFERENCES joueur(pseudo)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE jeu(
    id_jeu serial PRIMARY KEY,
    titre varchar(100) NOT NULL, --On considére qu'un jeu n'a pas forcement un titre unique
    prix numeric(4, 2) default 0 NOT NULL,
    date_sortie date NOT NULL,
    age_min numeric(2, 0) NOT NULL,
    synopsis text, 
    nom_edite varchar(20), 
    nom_dev varchar(20),
    url_img varchar(200) NOT NULL,
    FOREIGN KEY (nom_edite) REFERENCES entreprise(nom),
    FOREIGN KEY (nom_dev) REFERENCES entreprise(nom)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE succes(
    code varchar(4) PRIMARY KEY,
    intitule varchar(200) NOT NULL,
    condition varchar(200),
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
('Square_Enix', 'Japon'),
('Bethesda', 'USA'),
('Bungie', 'USA'),
('CD_Projekt', 'Pologne'),
('Naughty_Dog', 'USA'),
('2K_Games', 'USA'),
('Riot_Games', 'USA'),
('Sega', 'Japon'),
('Gearbox_Software', 'USA'),
('Project_Moon', 'Corée'),
('Ubisoft_Montreal', 'Canada'),
('Spike_Chunsoft', 'Japon'),
('KOEI_TECMO', 'Japon'),
('FromSoftware', 'Japon'),
('Ankama_Games', 'France'),
('PlayStation_Studio', 'USA'),
('Thomas_Moon_Kang', 'USA'),
('Humble_Games', 'USA'),
('Digital_Sun', 'Espagne'),
('Riot_Forge', 'USA'),
('Activision', 'USA'),
('Double_Stallion', 'Canada');

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

-- Attention, les INSERTS sont pas oufs
-- Joueurs
INSERT INTO joueur (pseudo, mdp, nom, mail, date_naissance) VALUES
('BlazedSora', 'oliver123', 'Oliver Grey', 'oliver@mail.com', '1992-11-01'),
('Gammandi', 'Gammandi123', 'Sophia Black', 'sophia@mail.com', '1990-10-12'),
('Zerio', 'liam123', 'Liam Turner', 'liam@mail.com', '1994-06-20'),
('Shing', 'Shing123', 'Shing Lee', 'Shing@mail.com', '1988-08-09'),
('LeCrapuleux', 'LeCrapuleux123', 'LeCrapuleux Hall', 'LeCrapuleux@mail.com', '1996-12-15'),
('RolandLover19', 'RolandLover19123', 'RolandLover19 Scott', 'RolandLover19@mail.com', '1995-04-02'),
('IsThatTheRedMist2', 'IsThatTheRedMist2123', 'IsThatTheRedMist2 White', 'IsThatTheRedMist2@mail.com', '1993-03-23'),
('Gregor14', 'ava123', 'Ava Martin', 'ava@mail.com', '1991-07-15'),
('Rocinante', 'Rocinante123', 'Rocinante Harris', 'Rocinante@mail.com', '1987-02-14'),
('KebabIsGood24', 'KebabIsGood24123', 'KebabIsGood24 Carter', 'KebabIsGood24@mail.com', '1999-01-25');

INSERT INTO joueur (pseudo, mdp, nom, mail, date_naissance, solde) VALUES
('david', '$2b$12$EGQmS9W6aN5x.cU7sbRE4uM.FwmL6kSBGoFfHGn539tBO/IeyPU0i', 'dada dembele', 'dada@gmail.com', '2006-01-10', 50), --MDP : 123
('abdel', '$2b$12$65L8VEsVpi1oHY1hKuVTl.ENKwHtxNWNjPD4tRtldU/EE1YnoSZCC', 'abdel kader', 'abdel@gmail.com', '2014-03-04', 60); --MDP : 123
-- Jeux
INSERT INTO jeu (titre, prix, date_sortie, age_min, synopsis, nom_edite, nom_dev, url_img) VALUES
('Lobotomy Corp', 22.99, '2018-04-18', 18, 
'Vous incarnez un manager qui a pour but de guider les Sephirah eux-mêmes chefs d''une troupe d''employés. La lobotomy corporation contient plusieurs monstre étranges qui serviront à récolter de l''énergie quitte à sacrifier des employés. Serez-vous capable de capable de génerer un maximum d''énergie avec un minimum de perte ?', 
'Project_Moon', 'Project_Moon', '../static/img/game_cover/LobotomyCorp.webp'),

('Danganronpa: Trigger Happy Havoc', 19.99, '2016-02-18', 16, 
'Dans une école coupée du monde extérieur, vous êtes forcé de trouver meutrier en passant par une phase d''enquête pour ensuite utiliser ces preuves pour briser les arguments erroné afin de découvrir l''identité du coupable.',
'Spike_Chunsoft', 'Spike_Chunsoft', '../static/img/game_cover/DanganronpaTriggerHappyHavoc.webp'),

('Fate Samurai Remnant', 69.99, '2023-09-29', 18, 
'Dans un paisible village à l''èree d''edo au Japon, un étrange Rituel invoque plusieurs esprits héroïques du passé chacun rattaché à un maître qui leur est propre. Il est dit que celui qui arrive à venir au bout des autres servant aura son voeu exaucé.', 
'KOEI_TECMO', 'KOEI_TECMO', '../static/img/game_cover/FateSamuraiRemnant.webp'),

('Elden Ring', 59.99, '2022-02-25', 18, 
'Découvrez un monde brisé où règne terreur et sang. Répondez à l''appel que vous, sans-éclat, pouvez entendre et suivez votre destin en vainquant de nombreux adversaires tous plus coriaces que les autres jusqu''a devenir Seigneur d''Elden.',
'FromSoftware', 'FromSoftware', '../static/img/game_cover/EldenRing.webp'),

('Waven', 0.00, '2023-08-16', 12, 
'Le nouveau jeu d''Ankama suivant la chronologie de Wakfu ! Sélectionnez une classe, puis améliorez votre personnage via ses équipements ou sorts. Façonnez votre aventure solo ou avec vos amis dans un gameplay au tour par tour !', 
'Ankama_Games', 'Ankama_Games', '../static/img/game_cover/Waven.webp'),

('Limbus Company', 0.00, '2023-02-27', 18, 
'Vous êtes un manager au sein d''un troupe de 12 Sinners engagés par la Limbus Company avec comme mission de ramener le Golden Bough. Explorez les ruines de la lobotomy corporation afin de trouver votre dû.', 
'Project_Moon', 'Project_Moon', '../static/img/game_cover/LimbusCompany.webp'),

('Ghost of Tsushima DIRECTOR''S CUT', 59.99, '2024-03-16', 18, 
'Tracez votre propre voie dans ce jeu d''action-aventure en monde ouvert et découvrez tous ses secrets.', 
'PlayStation_Studio', 'PlayStation_Studio', '../static/img/game_cover/ghost-of-tsushima-directors-cut.webp'),

('One Step From EDEN', 5.99, '2020-03-26', 12, 
'Frayez-vous un chemin jusqu''à Eden à l''aide d''un deck de sorts que vous sélectionnerez au fil de votre partie. Faites des rencontres, bonnes ou mauvaises peu importe, progressez et atteignez Eden', 
'Thomas_Moon_Kang', 'Humble_Games', '../static/img/game_cover/One-Step-From-Eden.webp'),

('Master Detective Archives: RAIN CODE Plus', 59.99, '2024-07-17', 18, 
'Yuma, un détective en formation amnésique, et Shinigami, l''esprit qui le hante, s''attaquent aux mystères non résolus.', 
'Spike_Chunsoft', 'Spike_Chunsoft', '../static/img/game_cover/MasterDetectiveRainCode.webp'),

('Danganronpa 2: Goodbye Despair', 19.99, '2016-04-19', 18, 
'Vos camarades de classe et vous étiez prêts à profiter du soleil, mais Monokuma est revenu pour relancer son jeu meurtrier ! Pris au piège dans une situation où il vous faut tuer ou être tué, votre seul espoir est de lever le voile sur les mystères de l''île.', 
'Spike_Chunsoft', 'Spike_Chunsoft', '../static/img/game_cover/DanganronpaGoodbyeDespair.webp'),

('The Mageseeker', 29.99, '2023-04-18', 12,
'Découvrez une ville pourrie par les conflit entre les mages et les humains lambda à travers Sylas, un mage prisonnier depuis son enfance avec un profond désir de vengeance envers ces traqueurs de mages qui l''ont enfermé. Battez vous avec les chaines qui faisaient de vous un prisonnier et utilisez la magie de vos adversaires pour libérer Demacia.',
'Digital_Sun', 'Riot_Forge', '../static/img/game_cover/The-Mageseeker-A-League-Of-Legends-Story-Artwork.webp'
),

('Sekiro Shadows Die Twice', 59.99, '2019-03-19', 18,
'Loup, un shinobi ayant perdu son bras au cours d''un de ses combats voit celui-ci remplacer par une prothèse. Combinez les arts Shinobi avec votre bras mécanique pour combattre des adversaires entrainés sous ordre de votre maître. Préparez vous à des combats féroces et sans-pitié qui vont vous donner du fil à retordre',
'FromSoftware', 'Activision', '../static/img/game_cover/Sekiro.webp'
),

('Convergence', 29.99, '2023-05-23', 12,
'Découvrez les bas-fonds de Zaun avec Ekko un jeune inventeur qui ne cesse d''innover et qui traverse Zaun et mets des raclées à ceux qui le mérite avec sa machine à remonter le temps ! Créez de nouveaux Gadgets et débloquez de nouvelles façon de les utiliser au cours de votre aventure.',
'Double_Stallion', 'Riot_Forge', '../static/img/game_cover/Convergence.webp'
),
('Library of Ruina', 24.99, '2021-08-10', 18,
'Roland, un gars à l''apparence plutôt banal se retrouve par accident dans la "Library" et sera forcé de travailler pour la directrice des lieux. Affrontez les invités avec une système de combat qui force la réfléxion. Transformez-les en livres pour agrandir la bibliothèque ou apprendres de nouvelles technniques. ',
'Project_Moon', 'Project_Moon', '../static/img/game_cover/Library.webp'
);

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
(10, 11), -- Danganronpa 2 est un jeu d'aventure
(11, 12), -- Mageseeker est un jeu d'Action, RPG et Indépendant
(11, 13),
(11, 10),
(12, 11), -- Sekiro est un jeu Action et Aventure
(12, 12),
(13, 11), -- Convergence est un jeu Action et Aventure
(13, 12);
-- Succès pour les jeux
INSERT INTO succes (code, intitule, condition, id_jeu) VALUES
('S011', 'Angela.', 'Finir le jeu Loboymy Corp', 1),
('S012', 'Désespoir', 'Vous avez succombé aux désespoirs.', 2),
('S013', 'Espoir ??', 'Terminez le jeu.', 2),
('S014', 'Samurai forever', 'Devenez l''ultime Samourai', 3),
('S015', 'Malania EZ', 'Tuer Malania en NO HIT', 4),
('S016', 'Pigeon', 'Faire une transaction sur Waven', 5),
('S017', 'Lament.', 'Télécharger le jeu Limbus Company', 6),
('S018', 'Let us be free', 'Finir le Canto V', 6),
('S019', 'J''ai pas d''idee', 'Succes sur Tsushima', 7),
('S020', 'One try', 'Gagner votre première partie', 8),
('S021', 'It''s just teddy !', 'Trouver un ours en peluche', 9),
('S022', 'Hope blooms', 'Finir Danganronpa 2', 10),
('S023', 'Matrixé par LoL', 'Finir Mageseeker', 11),
('S024', 'J''ai pas d''idee aussi', 'Succes sur Tsushima', 12),
('S025', 'Matrixé par Arcane', 'Finir Convergence', 13),
('S026', 'Léger accident', 'Tuez tout vos employé', 1),
('S027', 'Aucune perte à signaler', 'Finissez une journée sans pertes à déplorer', 1),
('S028', 'Efficacité > Nombre', 'Finissez une journée avec uniquement des employés au niveau maximum', 1),
('S029', 'Il était une fois, trois oiseaux dans une forêt.. ', 'Faites un travail avec les abnormalités suivantes : Oiseau de la punition,  Oiseau du jugement , Gros oiseau', 1),
('S030', 'Vroom-vroom', 'Finissez le prologue', 6),
('S031', 'Chanceux', 'Obtenez deux identités 3Ø différentes lors d''une extraction', 6),
('S032', 'Malchanceux', 'Invoquez 4 fois de suites sans avoir de 3Ø ', 6),
('S033', 'Mon bras a changé...', 'utilisez l''E.G.O de Gregor à la fin du Canto 1', 6),
('S034', 'Dégommeur de monstre', 'Vaincre un monstre pour la première fois', 3),
('S035', 'Rénovation', 'Constuire l''atelier pour la première fois', 3),
('S036', 'Âme d''épéiste', 'Apprendre toutes les postures', 3),
('S037', 'Pas mal pour un mortel.', 'Vendre une statue de bouddha à Babyloni-ya', 3),
('S038', 'Collectionneur', 'Acquérir toute les décorations', 3),
('S039', 'Pour Demacia', 'Combattre Garen au début du jeu', 11),
('S040', 'Quintuplé', 'Tuer 5 ennemis en même temps', 11),
('S041', 'Grand Helmet Bro', 'Vaincre le casque du géant', 11),
('S042', 'Traumatisme Ancien', 'Vaincre Rayn à Devineur', 11),
('S043', 'Détournement', 'Copier les Compétences ennemis 200 fois', 11),
('S044', 'Immortel ', 'Finissez le jeu sans mourir', 13),
('S045', 'Plus dure sera la chute', 'Parez l''attaque d''un boss', 13),
('S046', 'Apprendre de ses erreurs', 'Subissez une attaque, remontez le temps, puis parez cette même attaque.', 13),
('S047', 'Bon Voisin', 'Ne tabassez le voisinage', 13),
('S048', 'La gâchette Folle', 'Vainquez Jinx', 13),
('S049', 'Ego emprunté', 'Utilisez une page E.G.O', 14),
('S050', 'Gambling', 'Utilisez "Boundary of death" plusieurs fois dans la même réception', 14),
('S051', 'Seul contre tous', 'Réussissez une réception avec un seul personnage face à un groupe d''au moins 4 invités', 14),
('S052', '"That''s that and this is this"', 'Revisionnez tout les moments où Roland dit "That''s that and this is this"', 14),
('S053', 'Un invité inattendu', 'Envoyez une invitation générale', 14),
('S054', 'Revenant', 'Mourrez, puis ressuscitez pour la première fois.', 12),
('S055', 'Les pilleurs de tombes', 'Rencontrez les pilleurs de tombes.', 12),
('S056', 'Lame Révérée', 'Vous avez reçu "Kusabimaru" de la part de kuro.', 12),
('S057', 'Traumatisme', 'Mourrez plus de 20 fois sur le même boss.', 12),
('S058', 'Seigneur d''Elden', 'Atteindre la fin "seigneur d''Elden"', 4),
('S059', 'Loyale Monture', 'Mourrez avec torrent, votre monture.', 4),
('S060', 'Ton pire ennemi?', 'Mourrez de chute lors d''un combat de boss', 4),
('S061', 'A l''aide !', 'Gagnez un combat de boss grâce à un joueur invoqué', 4)
;

-- Reapprovisionner (argent ajouté au porte-monnaie)
INSERT INTO reapprovisionner (pseudo, date_transaction, montant) VALUES
('BlazedSora', '2024-11-01', 300),
('Gammandi', '2024-11-05', 400),
('Zerio', '2024-11-10', 500),
('Shing', '2024-11-12', 600),
('LeCrapuleux', '2024-11-15', 700),
('RolandLover19', '2024-11-17', 800),
('IsThatTheRedMist2', '2024-11-20', 150),
('Gregor14', '2024-11-22', 900),
('Rocinante', '2024-11-25', 1100),
('KebabIsGood24',  '2024-11-26', 1300);

-- Achats de jeux
INSERT INTO achat (pseudo, id_jeu, note, commentaire, date_achat) VALUES
('BlazedSora', 1, 4.9, 'J''ai attaqué un piaf qui s''est échappé et il a tué tout mes employés, BANGER', '2021-10-09'),
('Gammandi', 1, 4.2, 'Je suis désormais traumatisé à vie mais au moins j''ai finit le jeu', '2023-03-16'),
('Zerio', 1, 4.7, 'Je serais prêt à me faire lobotomiser pour oublier ce jeu et le redécouvrir', '2021-05-14'),

('BlazedSora', 6, 3.9, 'J''ai eu un bon perso dès le début ducoup c''est forcément un bon jeu 👍', '2023-06-12'),
('Gammandi', 6, 4.8, 'C''est un banger absolu, une histoire incroyable avec un système de combat particulier et une D.A magnifique.', '2021-01-06'),
('Zerio', 6, 4.9, 'J''adore le systèle de dispense qui permet d''avoir le perso que tu souhaites en F2P même si tu es malchanceux. Meilleur Gacha.', '2022-02-12'),

('BlazedSora', 3, 3.1, 'Le gameplay est intéressant pour certains perso mais reste tout de même limité. En plus, le jeu n''est pas très très beau.', '2021-05-02'),
('Gammandi', 3, 4.9, 'Bien que le gameplay soit désagréable par moment, le jeu reste incroyable au niveau de l''histoire et du développement du personnage principal. Le héros évolue bien au fil du jeu et la tension est palpable par moment. Certains artwork sont magnifiques et embeillissent le design de plusieurs personnages.', '2021-07-11'),
('Zerio', 3, 4.1, 'Quelques musiques sont bien, l''histoire très cool. Le gameplay est cool de manière général. Malheureusement le jeu est parfois beau mais pas toujours.', '2021-11-12'),

('BlazedSora', 11, 4.3, 'League Of Legends c''est caca mais ce jeu est très bien. Validé par la street', '2022-08-02'),
('Gammandi', 11, 5, 'En tant que main Sylas, je dis haut et fort que ce jeu est un banger absolu et résume bien l''histoire de mon champion préféré. Des mécaniques de gameplay incroyable et des combat de boss que j''ai adoré.', '2024-05-11'),
('Zerio', 11, 4, 'Jsuis pas fan des graphismes mais le gameplay est sympa et l''histoire plutôt cool donc ça rattrape.', '2024-12-22'),

('Shing', 12, 4.7, 'Un Souls-like qui ne déçoit pas ! Bien qu''il soit assez différents des autres jeux fromsoftware, il a une belle histoire et des boss très satisfaisant à vaincre', '2024-01-10'),
('LeCrapuleux', 12, 3.6, 'Le jeu est trop dur pour moi donc j''ai beaucoup de mal mais ce n''est pas un mauvais jeu pour autant.  Je suis sûr qu''il va plaire à d''autres personnes', '2024-02-17'),
('RolandLover19', 12, 4.2, 'Je suis un grand fan du japon féodal, jouer à ce jeu qui respecte bien les mentalités de l''époque est un vrai plaisir. De plus, les décor sont magnifiques', '2024-02-18'),

('IsThatTheRedMist2', 4, 0.1, 'Cé tro dure. Je retourne sure roblox', '2023-11-19'),
('Gregor14', 4, 5.0, 'La difficulté est au rendez-vous (sauf si vous jouez mage) avec des tas de builds différents (sauf mage) et le jeu est fun et demande un peu de réflexion sur certains boss (sauf pour les mages).', '2023-08-21'),
('Rocinante', 4, 3.5, 'Le jeu offre une diversité tel que peu de joueurs auront une aventure très similaire. Bien que l''histoire de base reste la même pour tout les joueurs à quelques exception près. Vous décidez de où vous allez et de ce que VOUS jouez. Tracez votre propre route et profitez.', '2023-07-23'),

('KebabIsGood24', 13, 4.6, 'Le jeu est sympa visuellement, les combats sont cool avec des boss plus ou moins difficiles. En bref, c''est un bon jeu !', '2022-09-25'),
('LeCrapuleux', 13, 4.4, 'Les mécaniques de combats sont amusants à utiliser et l''histoire est assez prenante. Cependant le jeu est beaucoup trop court ! J''ai finis en mode difficile le jeu d''une traite et ça m''a pris moins d''une journée.', '2022-11-22'),
('RolandLover19', 13, 3.9, 'League Of Legends c''est toujours caca mais j''aime bien Ekko alors ça va', '2022-11-15'),

('BlazedSora', 14, 5.0,'Mon jeu préféré. L''histoire est incroyable, les personnages sont attachant et stylé, le système de combat est incroyable et détaillé. Le jeu devient progressivement très difficile ce qui force la réfléxion à certains moments. J''adore.','2021-09-10'),
('Gammandi', 14, 4.9,'Un banger trop peu connu. L''écriture des personnages, les musiques, l''histoire, tout est incroyable. Ceux qui disent que ce jeu est guez n''y ont jamais joué où sont éclatax au jeu. ','2022-10-10'),
('IsThatTheRedMist2', 14, 4.5,'A l''aide, j''ai finit le jeu depuis plusieurs mois et je n''arrive pas à me sortir "That''s that and this is this" de ma tête.  J''en suis au point où j''ai rétorqué ça à ma femme lorsqu''elle est partie avec les gosses... Cependant le jeu est bien','2023-11-13'),
('david', 14, 4.7,'Les musiques sont tellement banger que maintenant j''ai besoin d''en écouter une quotidiennement.','2022-08-07'),
('Gregor14', 14, 4.8,'Je n''arrive plus à progresser dans le jeu tant il est difficile. Ce n''est pas pour autant déplaisant puisque le système de combat fait beaucoup réfléchir et j''aime ça.','2023-12-09'),


('david', 2, 5, 'Je pleure sur le poulet que c''est DR, jouer à ce jeu svp', '2024-11-25'),
('david', 10, 5, 'Chiaki une reine putain, je pleure snif.', '2024-11-25');

-- Partages de jeux entre joueurs
INSERT INTO partage (pseudo1, pseudo2, id_jeu, date_partage) VALUES
('BlazedSora', 'Gammandi', 1, '2024-11-03'),
('Zerio', 'Shing', 3, '2024-11-07'),
('LeCrapuleux', 'RolandLover19', 5, '2024-11-12'),
('IsThatTheRedMist2', 'Gregor14', 7, '2024-11-16'),
('Rocinante', 'KebabIsGood24', 9, '2024-11-22');

-- Déblocages supplémentaires de succès
INSERT INTO debloquer (pseudo, id_jeu, code, date_obtention) VALUES
('BlazedSora', 1, 'S011', '2024-11-04'),
('Gammandi', 2, 'S012', '2024-11-07'),
('Zerio', 3, 'S013', '2024-11-10'),
('Shing', 4, 'S014', '2024-11-13'),
('LeCrapuleux', 5, 'S015', '2024-11-16'),
('RolandLover19', 6, 'S016', '2024-11-18'),
('IsThatTheRedMist2', 7, 'S017', '2024-11-20'),
('Gregor14', 8, 'S018', '2024-11-22'),
('Rocinante', 9, 'S019', '2024-11-24'),
('KebabIsGood24', 10, 'S020', '2024-11-27'),
('david', 2, 'S012', '2024-11-24'),
('david', 2, 'S013', '2024-11-24'),
('david', 10, 'S022', '2024-11-24');

