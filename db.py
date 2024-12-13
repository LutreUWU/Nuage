import psycopg2
import psycopg2.extras

## ATTENTION, MODIFIER LE NOM DE LA BASE DE DONNEE
def connect():
  conn = psycopg2.connect(
  host = "localhost",
  dbname = "postgres", ## nom de la BDD locale sur mon ordi (A MODIFIER SI ON CHANGE d'ORDI)
  cursor_factory = psycopg2.extras.NamedTupleCursor ## Pour avoir les tuples nommés
  )
  conn.autocommit = True ## Permet d'actualiser les données sur le site si on modifie la BDD
  return conn



'''
def connect():
  conn = psycopg2.connect(
  host = "localhost",
  dbname = "projet_bdd", ## nom de la BDD locale sur mon ordi (A MODIFIER SI ON CHANGE d'ORDI)
  user = "root",
  cursor_factory = psycopg2.extras.NamedTupleCursor ## Pour avoir les tuples nommés
  )
  conn.autocommit = True ## Permet d'actualiser les données sur le site si on modifie la BDD
  return conn
'''

'''
Si on est sur les ordis de la Fac
def connect():
  conn = psycopg2.connect(
  host = "sqledu.univ-eiffel.fr",
  dbname = "david_db",
  password = "mdp",
  cursor_factory = psycopg2.extras.NamedTupleCursor 
  )
  conn.autocommit = True
  return conn

)
'''