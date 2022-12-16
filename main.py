import json
import random
from matplotlib import pyplot as plt
import numpy as np

from characters import Character
from estimators import *


def display_plots(mod_est, ac_est):
    fig, axs = plt.subplots(2, len(mod_est))
    for idx, (name, est) in enumerate(mod_est.items()):
        ax_idx = 0 if len(mod_est) == 1 else (0, idx)
        axs[ax_idx].hist(est.xvals, bins=est.noptions, weights=est.current_estimate)
        axs[ax_idx].set(xlabel='Modifier')
        axs[ax_idx].set_title(name)
        if idx == 0:
            axs[ax_idx].set(ylabel='Probability')
    for idx, (name, est) in enumerate(ac_est.items()):
        ax_idx = 1 if len(mod_est) == 1 else (1, idx)
        axs[ax_idx].hist(est.xvals, bins=est.noptions, weights=est.current_estimate)
        axs[ax_idx].set(xlabel='AC')
        if idx == 0:
            axs[ax_idx].set(ylabel='Probability')
    plt.show()


def simulate_battle(verbose: bool = False):
    party1 = [Character('Manster Wipower', 600, 10, 10, 0, 8, False),
              Character('Abayes Satano\'brien', 1000, 14, 10, 0, 10, False)]
    party2 = [Character('Blelduth Chestsplitter', 1200, 14, 10, 0, 8,
                        False)]  # , Character('Washingtonlotus Toadstallchardson', 30, 8, 14, 0, 8, True)]
    mod_est = {c.name: ModifierEstimator() for c in party2}
    ac_est = {c.name: ACEstimator() for c in party2}
    all_characters = {c.name: c for c in party1 + party2}
    initiative = {n: c.roll_initiative() for n, c in all_characters.items()}
    initiative_order = sorted(all_characters.keys(), key=lambda i: initiative[i], reverse=True)

    ac_full_range = ac_est[party2[0].name].xvals
    acrange = [max(ac_full_range) - min(ac_full_range) + 1]
    mod_full_range = ac_est[party2[0].name].xvals
    modrange = [max(mod_full_range) - min(mod_full_range) + 1]

    if verbose:
        print(f'Initiative order is {initiative_order} (scores are {initiative})')
    while True:
        for name in initiative_order:
            character = all_characters[name]
            is_party1 = any(c.name == name for c in party1)
            if character.hp <= 0:
                continue
            other_party = party2 if is_party1 else party1
            if all(c.hp <= 0 for c in other_party):
                break
            opponent = random.choice(other_party)
            while opponent.hp <= 0:
                opponent = random.choice(other_party)

            to_hit = character.roll_to_hit()
            hit = to_hit >= opponent.ac
            if hit:
                damage = character.roll_damage()
                opponent.hp -= damage
                if verbose:
                    print(f'{name} hit {opponent.name} for {damage} damage (they have {opponent.hp} HP left)')
                    if opponent.hp <= 0:
                        print(f'{opponent.name} is DEAD')

            if is_party1:
                est = ac_est[opponent.name]
                est.update((to_hit, hit))
                poss = est.xvals[est.current_estimate > 0]
                acrange.append(max(poss) - min(poss) + 1)
            else:
                est = mod_est[name]
                est.update(to_hit)
                poss = est.xvals[est.current_estimate > 0]
                modrange.append(max(poss) - min(poss) + 1)
        if verbose:
            display_plots(mod_est, ac_est)
        if all(c.hp <= 0 for c in party1):
            if verbose:
                print('Freak the Mighty wins!')
            break
        if all(c.hp <= 0 for c in party2):
            if verbose:
                print('Hell Raisers win!')
            break
        if not verbose and acrange[-1] == 1 and modrange[-1] == 1:
            acest = ac_est[party2[0].name]
            modest = mod_est[party2[0].name]
            assert acest.xvals[acest.current_estimate > 0][0] == party2[0].ac
            assert modest.xvals[modest.current_estimate > 0][0] == party2[0].weapon_bonus + party2[0].prof
            break
    return np.array(acrange), np.array(modrange)


def main():
    acto0 = []
    modto0 = []
    nsims = 10000
    for i in range(nsims):
        acrange, modrange = simulate_battle()
        acto0.append(np.where(acrange == 1)[0][0])
        modto0.append(np.where(modrange == 1)[0][0])

        if i == nsims - 1:
            plt.plot(acrange[:30])
            plt.plot(modrange[:30])
            plt.xlabel('Number of attacks')
            plt.ylabel('Number of possiblities')
            plt.title('Uncertainty of AC and Modifier Over the Course of a Battle')
            plt.legend(['AC', 'Modifier'])
            plt.show()

    bins = np.arange(0, 250, 10)
    acres = plt.hist(acto0, bins=bins)[0]
    acres /= nsims
    plt.xlabel('Number of Attacks')
    plt.ylabel('Frequency')
    plt.title('Number of Attacks until AC is Known')
    plt.show()

    modres, resbins, _ = plt.hist(modto0, bins=bins)
    modres /= nsims
    plt.xlabel('Number of Attacks')
    plt.ylabel('Frequency')
    plt.title('Number of Attacks until Modifier is Known')
    plt.show()

    print(acres.tolist())
    print(modres.tolist())
    print(resbins.tolist())

    # with open('results.json', 'w') as file:
    #     json.dump({'ac': [int(i) for i in acto0], 'mod': [int(i) for i in modto0]}, file)

    with open('results.json', 'r') as file:
        res = json.load(file)
    acto0 = res['ac']
    modto0 = res['mod']

    acto0 = np.array(acto0)
    acmean = np.mean(acto0)
    acstdev = np.std(acto0)
    skew = np.mean(((acto0 - acmean) / acstdev) ** 3)
    kurtosis = np.mean(((acto0 - acmean) / acstdev) ** 4) - 3
    print(f'Mean is {acmean}, stdev is {acstdev}')
    print(f'Median is {np.median(acto0)}')
    print(f'Skew is {skew}, kurtosis is {kurtosis}')


if __name__ == '__main__':
    main()
