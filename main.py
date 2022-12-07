import random

from characters import Character


def main():
    party1 = [Character('Manster Wipower', 30, 10, 10, 0, 8, False), Character('Abayes Satano\'brien', 50, 14, 10, 0, 10, False)]
    party2 = [Character('Blelduth Chestsplitter', 60, 14, 10, 0, 8, False), Character('Washingtonlotus Toadstallchardson', 30, 8, 14, 0, 8, True)]
    all_characters = {c.name: c for c in party1 + party2}
    initiative = {n: c.roll_initiative() for n, c in all_characters.items()}
    initiative_order = sorted(all_characters.keys(), key=lambda i: initiative[i], reverse=True)

    print(f'Initiative order is {initiative_order} (scores are {initiative})')
    while True:
        for name in initiative_order:
            character = all_characters[name]
            if character.hp <= 0:
                continue
            other_party = party2 if any(c.name == name for c in party1) else party1
            opponent = random.choice(other_party)
            while opponent.hp <= 0:
                opponent = random.choice(other_party)

            to_hit = character.roll_to_hit()
            if to_hit >= opponent.ac:
                damage = character.roll_damage()
                opponent.hp -= damage
                print(f'{name} hit {opponent.name} for {damage} damage (they have {opponent.hp} HP left)')
                if opponent.hp <= 0:
                    print(f'{opponent.name} is DEAD')
        if all(c.hp <= 0 for c in party1):
            print('Freak the Mighty wins!')
            break
        if all(c.hp <= 0 for c in party2):
            print('Hell Raisers win!')
            break


if __name__ == '__main__':
    main()
