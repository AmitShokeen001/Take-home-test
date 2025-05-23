########################################################################################
# FINAL                                                                                #  
# clean, merged, and modular Python program that integrates:                           # 
# Human- and machine-readable display for any Pokémon (default: Pikachu),              #    
# Type distribution for the first 151 Pokémon,                                         #
# Type-based average base experience and speed stats,                                  #
# Grouping of Pokémon by primary type and analysis of distinct & most common moves     #
########################################################################################


import requests
import json
import time
from collections import defaultdict, Counter

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"
LIMIT_151 = 151

# ----------- Fetch Functions -----------

def fetch_pokemon_data(pokemon_name):
    """Fetch data for a single Pokémon by name or ID."""
    url = f"{POKEAPI_BASE_URL}/{pokemon_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        print(f"Error: Could not fetch data for '{pokemon_name}'")
        return None

def fetch_first_151_pokemon():
    """Fetch list of the first 151 Pokémon."""
    response = requests.get(f"{POKEAPI_BASE_URL}?limit={LIMIT_151}")
    response.raise_for_status()
    return response.json()['results']

def fetch_pokemon_details(url):
    """Fetch full details for a Pokémon from a given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# ----------- Display Functions -----------

def display_human_readable(data):
    print("\n=== Human-Readable Pokémon Data ===")
    print(f"Name: {data['name'].capitalize()}")
    
    print("\nTypes:")
    for type_info in data['types']:
        print(f"- {type_info['type']['name'].capitalize()}")
    
    print("\nAbilities:")
    for ability in data['abilities']:
        print(f"- {ability['ability']['name'].capitalize()}")
    
    print("\nBase Stats:")
    for stat in data['stats']:
        name = stat['stat']['name'].replace('-', ' ').capitalize()
        print(f"- {name}: {stat['base_stat']}")

def display_machine_readable(data):
    print("\n=== Machine-Readable Pokémon Data ===")
    structured = {
        'name': data['name'],
        'types': [t['type']['name'] for t in data['types']],
        'abilities': [a['ability']['name'] for a in data['abilities']],
        'stats': {s['stat']['name']: s['base_stat'] for s in data['stats']}
    }
    print(json.dumps(structured, indent=2))

# ----------- Analysis Functions -----------

def display_type_distribution():
    print("\nFetching type distribution for first 151 Pokémon...")
    type_counts = defaultdict(int)

    pokemon_list = fetch_first_151_pokemon()
    for pokemon in pokemon_list:
        try:
            data = fetch_pokemon_details(pokemon['url'])
            for t in data['types']:
                type_counts[t['type']['name']] += 1
            time.sleep(0.2)
        except:
            continue

    print("\nPokémon Type Distribution:")
    print("---------------------------")
    for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{type_name.capitalize():<12} : {count}")

def display_type_statistics():
    print("\nCalculating average base experience and speed by type...")
    exp_by_type = defaultdict(list)
    speed_by_type = defaultdict(list)

    pokemon_list = fetch_first_151_pokemon()
    for pokemon in pokemon_list:
        try:
            data = fetch_pokemon_details(pokemon['url'])
            base_exp = data.get('base_experience', 0)
            speed = next((s['base_stat'] for s in data['stats'] if s['stat']['name'] == 'speed'), 0)

            for t in data['types']:
                tname = t['type']['name']
                exp_by_type[tname].append(base_exp)
                speed_by_type[tname].append(speed)

            time.sleep(0.2)
        except:
            continue

    print("\nAverage Base Experience by Type:")
    for t, values in sorted(exp_by_type.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True):
        print(f"{t.capitalize():<12} : {sum(values) / len(values):.1f}")

    fastest = max(speed_by_type.items(), key=lambda x: sum(x[1]) / len(x[1]))
    print("\nType with Highest Average Speed:")
    print(f"{fastest[0].capitalize()} with {sum(fastest[1]) / len(fastest[1]):.1f} speed")

def display_moves_by_primary_type():
    print("\nGrouping Pokémon by primary type and analyzing moves...")
    type_to_moves = defaultdict(list)

    pokemon_list = fetch_first_151_pokemon()
    for pokemon in pokemon_list:
        try:
            details = fetch_pokemon_details(pokemon['url'])

            types = sorted(details['types'], key=lambda x: x['slot'])
            if not types:
                continue
            primary_type = types[0]['type']['name']

            move_names = [move['move']['name'] for move in details['moves']]
            type_to_moves[primary_type].extend(move_names)

            time.sleep(0.2)
        except:
            continue

    for ptype, moves in sorted(type_to_moves.items()):
        distinct_moves = set(moves)
        most_common, count = Counter(moves).most_common(1)[0]

        print(f"\nType: {ptype.capitalize()}")
        print(f"  Distinct Moves: {len(distinct_moves)}")
        print(f"  Most Common Move: {most_common} (used {count} times)")

# ----------- Main CLI -----------

def main():
    print("Pokémon CLI Tool")
    print("----------------")

    pokemon_name = input("Enter a Pokémon name (default: Pikachu): ").strip() or "pikachu"
    data = fetch_pokemon_data(pokemon_name)
    if not data:
        return

    while True:
        print("\nSelect an option:")
        print("1. Display human-readable Pokémon data")
        print("2. Display machine-readable Pokémon data (JSON)")
        print("3. Show type distribution for first 151 Pokémon")
        print("4. Show average base experience & speed by type")
        print("5. Group Pokémon by type and analyze moves")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            display_human_readable(data)
        elif choice == '2':
            display_machine_readable(data)
        elif choice == '3':
            display_type_distribution()
        elif choice == '4':
            display_type_statistics()
        elif choice == '5':
            display_moves_by_primary_type()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()


