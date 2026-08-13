phrase = "je dois reussir ma carrière d'ingénieur ia"
voyelles = "aeiou"

def compter(texte,letter):
    total = 0
    for t in texte:
        if t in letter:
            total+=1
    return total
# decouper le texte
mots = phrase.split()
taille = [len(m) for m in mots]
inventaire = {}
for t in phrase:
    if t in voyelles:
        inventaire[t]=inventaire.get(t,0)+1
print(taille)
print(inventaire)

resultat=compter(phrase,voyelles)
print("nombre de voyelles: ",resultat)