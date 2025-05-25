########################################################################################
# FINAL                                                                                #  
# clean, merged, and modular Python program that integrates:                           # 
# Human- and machine-readable display for any Pokémon (default: Pikachu),              #    
# Type distribution for the first 151 Pokémon,                                         #
# Type-based average base experience and speed stats,                                  #
# Grouping of Pokémon by primary type and analysis of distinct & most common moves     #
########################################################################################


import requests
from collections import defaultdict, Counter

# Constants
BASE_URL = "https://pokeapi.co/api/v2"
FIRST_GEN_LIMIT = 151

# --- Helper Functions ---

def get_pokemon_data(name_or_id):
    response = requests.get(f"{BASE_URL}/pokemon/{name_or_id.lower()}")
    if response.status_code != 200:
        raise Exception(f"Error fetching data for Pokémon: {name_or_id}")
    return response.json()

def display_pokemon_readable(data):
    name = data["name"].title()
    abilities = [a["ability"]["name"] for a in data["abilities"]]
    types = [t["type"]["name"] for t in data["types"]]
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}

    print(f"Name: {name}")
    print(f"Abilities: {', '.join(abilities)}")
    print(f"Types: {', '.join(types)}")
    print("Base Stats:")
    for stat, value in stats.items():
        print(f"  {stat.title()}: {value}")

def display_pokemon_machine(data):
    abilities = [a["ability"]["name"] for a in data["abilities"]]
    types = [t["type"]["name"] for t in data["types"]]
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
    return {
        "name": data["name"],
        "abilities": abilities,
        "types": types,
        "base_stats": stats
    }

def get_first_gen_pokemon_data():
    response = requests.get(f"{BASE_URL}/pokemon?limit={FIRST_GEN_LIMIT}")
    results = response.json()["results"]
    all_pokemon = []
    print("Fetching data for 151 Pokémon. Please wait...")
    for pokemon in results:
        pokemon_data = get_pokemon_data(pokemon["name"])
        all_pokemon.append(pokemon_data)
    return all_pokemon

# --- Challenge Functions ---

def challenge_1():
    data = get_pokemon_data("pikachu")
    print("\nHuman-readable format:")
    display_pokemon_readable(data)
    print("\nMachine-readable format:")
    print(display_pokemon_machine(data))

def challenge_2():
    name = input("Enter the name of a Pokémon: ")
    data = get_pokemon_data(name)
    print("\nHuman-readable format:")
    display_pokemon_readable(data)
    print("\nMachine-readable format:")
    print(display_pokemon_machine(data))

def challenge_3(pokemon_list):
    print("\nPokémon count by type (descending):")
    counts = count_pokemon_by_type(pokemon_list)
    for t, c in counts.items():
        print(f"{t.title()}: {c}")

def challenge_4(pokemon_list):
    avg_exp, max_speed_type, max_speed = avg_base_experience_by_type(pokemon_list)
    print("\nAverage base experience per type:")
    for t, exp in avg_exp.items():
        print(f"{t.title()}: {exp:.2f}")
    print(f"\nType with highest average base speed: {max_speed_type.title()} ({max_speed:.2f})")

def challenge_5(pokemon_list):
    abilities_count, moves_count = count_distinct_abilities_and_moves(pokemon_list)
    print(f"\nDistinct Abilities: {abilities_count}")
    print(f"Distinct Moves: {moves_count}")

def challenge_6(pokemon_list):
    print("\nDistinct moves and most common move by primary type:")
    grouped = group_by_type_and_moves(pokemon_list)
    for t, data in grouped.items():
        print(f"{t.title()}:")
        print(f"  Distinct Moves: {data['distinct_moves']}")
        print(f"  Most Common Move: {data['most_common_move']} ({data['occurrences']} times)")

def challenge_7(pokemon_list):
    analysis, most_diverse_type = top_3_by_total_stats_and_move_analysis(pokemon_list)
    for t, data in analysis.items():
        print(f"\n{t.title()} Type:")
        print(f"  Top 3 Pokémon: {', '.join(data['top_3'])}")
        print(f"  Average Moves: {data['average_moves']:.2f}")
        print(f"  Move Diversity: {data['move_diversity']}")
    print(f"\nType with most diverse move set among top 3 Pokémon: {most_diverse_type.title()}")

# --- Aggregation Helpers ---

def count_pokemon_by_type(pokemon_list):
    type_counts = defaultdict(int)
    for pokemon in pokemon_list:
        for t in pokemon["types"]:
            type_counts[t["type"]["name"]] += 1
    return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))

def avg_base_experience_by_type(pokemon_list):
    type_experience = defaultdict(list)
    type_speed = defaultdict(list)
    for p in pokemon_list:
        base_exp = p["base_experience"]
        speed = next(stat["base_stat"] for stat in p["stats"] if stat["stat"]["name"] == "speed")
        for t in p["types"]:
            type_name = t["type"]["name"]
            type_experience[type_name].append(base_exp)
            type_speed[type_name].append(speed)
    avg_experience = {k: sum(v)/len(v) for k, v in type_experience.items()}
    avg_speed = {k: sum(v)/len(v) for k, v in type_speed.items()}
    max_speed_type = max(avg_speed, key=avg_speed.get)
    return avg_experience, max_speed_type, avg_speed[max_speed_type]

def count_distinct_abilities_and_moves(pokemon_list):
    abilities = set()
    moves = set()
    for p in pokemon_list:
        for a in p["abilities"]:
            abilities.add(a["ability"]["name"])
        for m in p["moves"]:
            moves.add(m["move"]["name"])
    return len(abilities), len(moves)

def group_by_type_and_moves(pokemon_list):
    type_moves = defaultdict(list)
    for p in pokemon_list:
        primary_type = p["types"][0]["type"]["name"]
        move_names = [m["move"]["name"] for m in p["moves"]]
        type_moves[primary_type].extend(move_names)
    result = {}
    for type_, moves in type_moves.items():
        move_counts = Counter(moves)
        most_common = move_counts.most_common(1)[0]
        result[type_] = {
            "distinct_moves": len(set(moves)),
            "most_common_move": most_common[0],
            "occurrences": most_common[1]
        }
    return result

def top_3_by_total_stats_and_move_analysis(pokemon_list):
    type_groups = defaultdict(list)
    for p in pokemon_list:
        total_stats = sum(stat["base_stat"] for stat in p["stats"])
        move_count = len(p["moves"])
        primary_type = p["types"][0]["type"]["name"]
        type_groups[primary_type].append({
            "name": p["name"],
            "total_stats": total_stats,
            "move_count": move_count,
            "moves": set(m["move"]["name"] for m in p["moves"])
        })
    
    analysis = {}
    max_diverse_type = None
    max_move_variety = 0
    for type_, pokemons in type_groups.items():
        top3 = sorted(pokemons, key=lambda x: x["total_stats"], reverse=True)[:3]
        avg_moves = sum(p["move_count"] for p in top3) / 3
        all_moves = set()
        for p in top3:
            all_moves.update(p["moves"])
        move_diversity = len(all_moves)
        analysis[type_] = {
            "top_3": [p["name"] for p in top3],
            "average_moves": avg_moves,
            "move_diversity": move_diversity
        }
        if move_diversity > max_move_variety:
            max_move_variety = move_diversity
            max_diverse_type = type_
    return analysis, max_diverse_type

# --- Main CLI ---

def main():
    pokemon_list = []
    while True:
        print("\n--- PokeAPI CLI Challenge ---")
        print("1. Pikachu: Abilities, Types, Base Stats")
        print("2. Dynamic Pokémon Info by Name")
        print("3. Count Pokémon by Type")
        print("4. Average Base Experience + Highest Average Speed Type")
        print("5. Count Distinct Abilities and Moves")
        print("6. Group by Type & List Moves + Most Common")
        print("7. Top 3 Pokémon by Stats + Move Diversity")
        print("8. Exit")
        choice = input("Select an option (1-8): ")

        try:
            if choice == "1":
                challenge_1()
            elif choice == "2":
                challenge_2()
            elif choice in ["3", "4", "5", "6", "7"]:
                if not pokemon_list:
                    pokemon_list = get_first_gen_pokemon_data()
                if choice == "3":
                    challenge_3(pokemon_list)
                elif choice == "4":
                    challenge_4(pokemon_list)
                elif choice == "5":
                    challenge_5(pokemon_list)
                elif choice == "6":
                    challenge_6(pokemon_list)
                elif choice == "7":
                    challenge_7(pokemon_list)
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
