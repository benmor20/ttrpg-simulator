import json
import random
from matplotlib import pyplot as plt
import numpy as np

from characters import Character
from estimators import *


def display_est_plots(mod_est, ac_est):
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


def display_hp_plot(p1hp, p2hp):
    plt.plot(p1hp, '-')
    plt.plot(p2hp, '-')
    plt.xlabel('Rounds')
    plt.ylabel('Total Party HP')
    plt.legend(['Party 1', 'Party 2'])
    plt.title('HP Over Time for Two Parties in Combat')
    plt.show()


def display_range_plots(acrange, modrange):
    if np.any(acrange == 1):
        time_till_ac_one = np.where(acrange == 1)[0][0]
    else:
        time_till_ac_one = len(acrange)
    if np.any(modrange == 1):
        time_till_mod_one = np.where(modrange == 1)[0][0]
    else:
        time_till_mod_one = len(modrange)
    end = 75
    if end > len(acrange):
        acrange = np.concatenate([acrange, acrange[-1] * np.ones((end - len(acrange),))])
    if end > len(modrange):
        modrange = np.concatenate([modrange, modrange[-1] * np.ones((end - len(modrange), ))])

    plt.plot(acrange[:end])
    plt.plot(modrange[:end])
    plt.xlabel('Number of attacks')
    plt.ylabel('Number of possiblities')
    plt.title('Uncertainty of AC and Modifier Over the Course of a Battle')
    plt.legend(['AC', 'Modifier'])
    plt.show()


def simulate_battle(verbose: bool = False, plot: bool = False):
    party1 = [Character('Manster Wipower', 90, 10, 10, 0, 8, False),
              Character('Abayes Satano\'brien', 150, 14, 10, 0, 10, False)]
    party2 = [Character('Blelduth Chestsplitter', 240, 14, 10, 0, 8, False), ]
              #Character('Washingtonlotus Toadstallchardson', 90, 8, 14, 0, 8, True)]
    mod_est = {c.name: ModifierEstimator() for c in party2}
    ac_est = {c.name: ACEstimator() for c in party2}
    all_characters = {c.name: c for c in party1 + party2}
    initiative = {n: c.roll_initiative() for n, c in all_characters.items()}
    initiative_order = sorted(all_characters.keys(), key=lambda i: initiative[i], reverse=True)

    ac_full_range = ac_est[party2[0].name].xvals
    acrange = [max(ac_full_range) - min(ac_full_range) + 1]
    mod_full_range = ac_est[party2[0].name].xvals
    modrange = [max(mod_full_range) - min(mod_full_range) + 1]
    p1hp = [sum(c.hp for c in party1)]
    p2hp = [sum(c.hp for c in party2)]

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
                ac_est[opponent.name].update((to_hit, hit))
                poss = ac_est[opponent.name].xvals[ac_est[opponent.name].current_estimate > 0]
                acrange.append(max(poss) - min(poss) + 1)
            else:
                mod_est[name].update(to_hit)
                poss = mod_est[name].xvals[mod_est[name].current_estimate > 0]
                modrange.append(max(poss) - min(poss) + 1)
        p1hp.append(sum(c.hp for c in party1))
        p2hp.append(sum(c.hp for c in party2))
        # if verbose:
        #     display_est_plots(mod_est, ac_est)
        if all(c.hp <= 0 for c in party1):
            if verbose:
                print('Freak the Mighty wins!')
            break
        if all(c.hp <= 0 for c in party2):
            if verbose:
                print('Hell Raisers win!')
            break
        if acrange[-1] == 1 and modrange[-1] == 1:
            acest = ac_est[party2[0].name]
            modest = mod_est[party2[0].name]
            assert acest.xvals[acest.current_estimate > 0][0] == party2[0].ac
            assert modest.xvals[modest.current_estimate > 0][0] == party2[0].weapon_bonus + party2[0].prof
            break
    if plot:
        display_hp_plot(p1hp, p2hp)
        display_range_plots(np.array(acrange), np.array(modrange))
    return np.array(acrange), np.array(modrange)


def main(simulate: bool = False):
    if simulate:
        acto0 = []
        modto0 = []
        nsims = 10000
        for i in range(nsims):
            acrange, modrange = simulate_battle(plot=i == nsims - 1)
            acto0.append(np.where(acrange == 1)[0][0])
            modto0.append(np.where(modrange == 1)[0][0])

        with open('results.json', 'w') as file:
            json.dump({'ac': [int(i) for i in acto0], 'mod': [int(i) for i in modto0]}, file)
    else:
        with open('results.json', 'r') as file:
            res = json.load(file)
        acto0 = res['ac']
        modto0 = res['mod']

        acto0 = np.array(acto0)
        acmean = np.mean(acto0)
        acstdev = np.std(acto0)
        skew = np.mean(((acto0 - acmean) / acstdev) ** 3)
        kurtosis = np.mean(((acto0 - acmean) / acstdev) ** 4) - 3
        print(f'Mean is {acmean:.3f}, stdev is {acstdev:.3f}')
        print(f'Median is {int(np.median(acto0))}')
        print(f'Skew is {skew:.2f}, kurtosis is {kurtosis:.2f}')

    bins = np.arange(0, 250, 10)
    acres = plt.hist(acto0, bins=bins)[0]
    plt.xlabel('Number of Attacks')
    plt.ylabel('Frequency')
    plt.title('Number of Attacks until AC is Known')
    plt.show()

    modres, resbins, _ = plt.hist(modto0, bins=bins)
    plt.xlabel('Number of Attacks')
    plt.ylabel('Frequency')
    plt.title('Number of Attacks until Modifier is Known')
    plt.show()


if __name__ == '__main__':
    simulate_battle(verbose=True, plot=True)
