data = {"msgs":[{"title":"A frilled lizard.","body":"A lizard with a giant and colourful fringe folded \
            around its neck. It flares its impressive frill at its victims while hissing angrily.\u000a\u000aMax HP: about 2\u000aAC \u000aEV +++ (about 60% to evade your +0 dagger)\u000aMR \u000a\u000aIt looks harmless.\u000aIt is cold-blooded and may be sl \
            owed by cold attacks.\u000aIt is tiny.\u000a It can bite for up to 3 damage.\u000aIt can travel through water.","quote":""," \
            spellset":[],"fg_idx":5065,"flag":0,"doll":[[5065,32]],"mcache":None,"msg":"ui-push","type":"describe-monster","ui-centred" \
            :False,"generation_id":4}]}


import re

body_string = data['msgs'][0]['body']

print("Starting test:\n\n")

print(body_string)

re.sub("\u000a", "\n", data['msgs'][0]['body'])

print("Doing special char substitution:\n\n")

monster_health = -1
AC_level = 0
EV_level = 0
MR_level = 0

danger_rating = "error"

i = 0
for line in body_string.split('\n'):
    if 'AC' in line:
        AC_level = line.split(' ')[1].count('+')
    elif 'EV' in line:
        EV_level = line.split(' ')[1].count('+')
    elif 'MR' in line:
        MR_level = line.split(' ')[1].count('+')
    elif 'looks' in line:
        danger_rating = line.split(' ')[-1]
    elif 'Max HP:' in line:
        monster_health = line.split(' ')[-1]


    print("  {}:{}".format(i, line))
    i+=1


print("health: {}".format(monster_health))
print("AC: {}".format(AC_level))
print("EV: {}".format(EV_level))
print("MR: {}".format(MR_level))
print("dange_rating: {}".format(danger_rating))