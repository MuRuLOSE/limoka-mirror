import json

trusted = [
    "https://github.com/iamnalinor/FTG-modules", # trust
    "https://github.com/vsecoder/hikka_modules", # trust 
    "https://github.com/sqlmerr/hikka_mods", # trust
    "https://github.com/N3rcy/modules", # trust
    "https://github.com/KorenbZla/HikkaModules", # trust
    "https://github.com/coddrago/modules", # trust
    "https://github.com/MoriSummerz/ftg-mods", # trust
    "https://github.com/anon97945/hikka-mods", # trust
    "https://github.com/dorotorothequickend/DorotoroModules", # trust
    "https://github.com/idiotcoders/idiotmodules", # trust
    "https://github.com/C0dwiz/H.Modules", # trust
    "https://github.com/GD-alt/mm-hikka-mods", # trust
    "https://github.com/hikariatama/ftg", # trust
    "https://github.com/fajox1/famods", # trust
    "https://github.com/TheKsenon/MyHikkaModules", # trust
    "https://github.com/Den4ikSuperOstryyPer4ik/Astro-modules"
]

def get_repo_path(repo_url):
    return repo_url.replace("https://github.com/", "")

prefixes = []
for dev in trusted:
    prefixes.append(get_repo_path(dev))

developers_dict = {
    "trusted": prefixes
}

with open("trusted.json", "w", encoding="utf-8") as json_file:
   json.dump(developers_dict, json_file, ensure_ascii=False, indent=2)