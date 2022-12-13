import random
from matplotlib import pyplot as plt
import numpy as np

from characters import Character
from estimators import *


def display_plots(mod_est, ac_est):
    fig, axs = plt.subplots(2, len(mod_est))
    for idx, (name, est) in enumerate(mod_est.items()):
        axs[0, idx].hist(est.xvals, bins=est.noptions, weights=est.current_estimate)
        axs[0, idx].set(xlabel='Modifier')
        axs[0, idx].set_title(name)
        if idx == 0:
            axs[0, idx].set(ylabel='Probability')
    for idx, (name, est) in enumerate(ac_est.items()):
        axs[1, idx].hist(est.xvals, bins=est.noptions, weights=est.current_estimate)
        axs[1, idx].set(xlabel='AC')
        if idx == 0:
            axs[1, idx].set(ylabel='Probability')
    plt.show()


def main():
    party1 = [Character('Manster Wipower', 30, 10, 10, 0, 8, False), Character('Abayes Satano\'brien', 50, 14, 10, 0, 10, False)]
    party2 = [Character('Blelduth Chestsplitter', 60, 14, 10, 0, 8, False), Character('Washingtonlotus Toadstallchardson', 30, 8, 14, 0, 8, True)]
    mod_est = {c.name: ModifierEstimator() for c in party2}
    ac_est = {c.name: ACEstimator() for c in party2}
    all_characters = {c.name: c for c in party1 + party2}
    initiative = {n: c.roll_initiative() for n, c in all_characters.items()}
    initiative_order = sorted(all_characters.keys(), key=lambda i: initiative[i], reverse=True)

    print(f'Initiative order is {initiative_order} (scores are {initiative})')
    while True:
        for name in initiative_order:
            character = all_characters[name]
            is_party1 = any(c.name == name for c in party1)
            if character.hp <= 0:
                continue
            other_party = party2 if is_party1 else party1
            opponent = random.choice(other_party)
            while opponent.hp <= 0:
                opponent = random.choice(other_party)

            to_hit = character.roll_to_hit()
            hit = to_hit >= opponent.ac
            if hit:
                damage = character.roll_damage()
                opponent.hp -= damage
                print(f'{name} hit {opponent.name} for {damage} damage (they have {opponent.hp} HP left)')
                if opponent.hp <= 0:
                    print(f'{opponent.name} is DEAD')

            if is_party1:
                ac_est[opponent.name].update((to_hit, hit))
            else:
                mod_est[name].update(to_hit)
        display_plots(mod_est, ac_est)
        if all(c.hp <= 0 for c in party1):
            print('Freak the Mighty wins!')
            break
        if all(c.hp <= 0 for c in party2):
            print('Hell Raisers win!')
            break


if __name__ == '__main__':
    main()
