import random

from collections import defaultdict


source = [n.strip().title() for n in open("names.txt")]
chains = defaultdict(list)

for name in source:
    name = "^" + name + "|"

    for count in range(2, 4):
        for i in range(len(name)):
            seq = name[i:i+count]

            if len(seq) < 2:
                break

            prefix = seq[:-1]

            chains[prefix].append(seq[-1])


def generate_char(current):
    while True:
        if current in chains:
            return random.choice(chains[current])
        
        # If no chain is found for bigram try unigram
        current = current[1:]


def generate_name(minlen, maxlen):
    ok = False

    while not ok:
        name = "^"

        while len(name) < maxlen:
            next = generate_char(name)
        
            if next == "|":
                if len(name) > minlen:
                    ok = True
                break
            
            name += next
    
    return name.replace("^", "")