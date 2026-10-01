"""iss_kids.py - Mode educatif pour enfants"""
import random

FAITS = [
    "L'ISS voyage a 27600 km/h, soit 100 fois plus vite qu'une voiture !",
    "Les astronautes grandissent de 3 cm dans l'espace (mais ils rapetissent en revenant).",
    "Il faut 45 minutes pour voir un lever de soleil depuis l'ISS.",
    "Les astronautes dorment dans des sacs de couchage accroches au mur.",
    "Dans l'ISS, l'eau flotte en boule a cause de l'apesanteur.",
    "Les astronautes font 2 heures de sport par jour pour garder leurs muscles.",
    "L'ISS est visible depuis la Terre comme une etoile tres brillante.",
    "Les toilettes de l'ISS aspirent tout avec de l'air, pas d'eau !",
    "Depuis l'ISS, on peut voir la Grande Muraille de Chine ? FAUX ! C'est une legende.",
    "L'ISS a coute environ 150 milliards de dollars a construire.",
    "Un lever de soleil vu de l'ISS dure seulement 10 secondes.",
    "Les astronautes perdent le gout dans l'espace a cause des fluides.",
    "Il y a environ 400 km entre la Terre et l'ISS (comme Paris-Marseille).",
    "L'ISS fait le tour de la Terre 16 fois par jour.",
    "Le premier touriste de l'espace a paye 20 millions de dollars.",
]

QUIZ_KIDS = [
    {"q": "Combien de fois l'ISS fait-elle le tour de la Terre par jour ?",
     "opts": ["3 fois", "16 fois", "100 fois"], "ans": 1},
    {"q": "A quelle vitesse va l'ISS ?",
     "opts": ["100 km/h", "27600 km/h", "1 million km/h"], "ans": 1},
    {"q": "Combien de temps dure un jour sur l'ISS ?",
     "opts": ["24 heures", "90 minutes", "1 semaine"], "ans": 1},
    {"q": "Que font les astronautes pour rester en forme ?",
     "opts": ["Ils dorment", "Ils font du sport 2h/jour", "Ils mangent beaucoup"], "ans": 1},
    {"q": "Comment l'ISS est-elle visible depuis la Terre ?",
     "opts": ["Comme la Lune", "Comme une etoile brillante", "On ne la voit pas"], "ans": 1},
    {"q": "Quelle est la taille de l'ISS ?",
     "opts": ["Comme une voiture", "Comme un terrain de foot", "Comme une ville"], "ans": 1},
]


def fait_aleatoire():
    return random.choice(FAITS)


def quiz_kids_start():
    qs = random.sample(QUIZ_KIDS, 3)
    return qs


def message_bienvenue(prenom="ami"):
    return f"""🌟 *Salut {prenom} !*

Je suis *MAP-CI Kid*, ton guide de l'espace ! 🚀

*Ce que je peux faire :*
• 💡 Te raconter des *faits rigolos* sur l'ISS
• 🎮 Te poser des *quiz* super cools
• 🛰️ Te dire *où est l'ISS* maintenant
• 🌍 T'envoyer une *photo de la Terre*

Envoie *"fait"* pour un fait,
*"quiz"* pour jouer,
*"ou est l'iss"* pour la position !

Amuse-toi bien ! 🎉"""


if __name__ == "__main__":
    print(message_bienvenue("Tchabio"))
    print()
    print("FAIT :", fait_aleatoire())
