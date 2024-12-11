import os
import random
images = []
for fichier in os.listdir('static/img/avatar/'):
    images.append(fichier)
for i in range(8):
    avatar = random.choice(images)
    print('../static/img/avatar/' + avatar)