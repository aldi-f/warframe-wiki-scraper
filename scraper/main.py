import requests
import luadata
import json


def convert_lua_to_json(lua_string):
    """Convert a Lua table string to a JSON object."""
    start_idx = lua_string.find("{")
    end_idx = lua_string.rfind("}") + 1
    lua_table = lua_string[start_idx:end_idx]

    # Patches for compatibility with Python
    # 1. math.huge replaced by 1e308
    lua_table = lua_table.replace("math.huge", '"1e308"')

    data = luadata.unserialize(lua_table)

    # Final replaces
    def convert_inf(obj):
        if isinstance(obj, dict):
            return {k: convert_inf(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_inf(x) for x in obj]
        elif obj == "1e308":
            return float("inf")
        return obj

    return convert_inf(data)

SAVE_FOLDER = "../data/"

WIKI_URL_BASE = "https://wiki.warframe.com/api.php"

BODY = {
    # "ability.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Ability",
    #     "content": "return require('Module:LuaSerializer')._serialize('Ability/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "arcane.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Arcane",
    #     "content": "return require('Module:LuaSerializer')._serialize('Arcane/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "blueprints.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Blueprints",
    #     "content": "return require('Module:LuaSerializer')._serialize('Blueprints/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "companions.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Companions",
    #     "content": "return require('Module:LuaSerializer')._serialize('Companions/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "enemies.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Enemies",
    #     "content": "return require('Module:LuaSerializer')._serialize('Enemies/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "mods.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Mods",
    #     "content": "return require('Module:LuaSerializer')._serialize('Mods/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "tennogen.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:TennoGen",
    #     "content": "return require('Module:LuaSerializer')._serialize('TennoGen/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "void.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Void",
    #     "content": "return require('Module:LuaSerializer')._serialize('Void/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "warframes.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Warframes",
    #     "content": "return require('Module:LuaSerializer')._serialize('Warframes/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "weapons.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Weapons",
    #     "content": "return require('Module:LuaSerializer')._serialize('Weapons/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # "factions.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Factions",
    #     "content": "return require('Module:LuaSerializer')._serialize('Factions/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    # To fix
    # "missions.json": {
    #     "action": "scribunto-console",
    #     "format": "json",
    #     "title": "Module:Missions",
    #     "content": "return require('Module:LuaSerializer')._serialize('Missions/data')",
    #     "question": "=p",
    #     "clear": 1,
    #     "token": "+\\",
    #     "formatversion": "2",
    # },
    "enemies.json": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Enemies",
        "content": "return require('Module:LuaSerializer')._serialize('Enemies/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2",
    },
    "blueprints.json": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Blueprints",
        "content": "return require('Module:LuaSerializer')._serialize('Blueprints/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2",
    },
    "cosmetics.json": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:Cosmetics",
        "content": "return require('Module:LuaSerializer')._serialize('Cosmetics/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2",
    },
    "damage_types.json": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:DamageTypes",
        "content": "return require('Module:LuaSerializer')._serialize('DamageTypes/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2",
    },
    "drop_tables.json": {
        "action": "scribunto-console",
        "format": "json",
        "title": "Module:DropTables",
        "content": "return require('Module:LuaSerializer')._serialize('DropTables/data')",
        "question": "=p",
        "clear": 1,
        "token": "+\\",
        "formatversion": "2",
    },

}


for save_path, body in BODY.items():
    print(f"Fetching and saving {save_path}...")
    response = requests.post(WIKI_URL_BASE, data=body).json()
    data = convert_lua_to_json(response["return"])
    with open(SAVE_FOLDER + save_path, "w") as f:
        json.dump(data, f, indent=2)