import os
import subprocess

repos = [
    "https://github.com/DziruModules/hikkamods",
    "https://github.com/kamolgks/Hikkamods",
    "https://github.com/thomasmod/hikkamods",
    "https://github.com/SkillsAngels/Modules",
    "https://github.com/Sad0ff/modules-ftg",
    "https://github.com/Yahikoro/Modules-for-FTG",
    "https://github.com/KeyZenD/modules",
    "https://github.com/AlpacaGang/ftg-modules",
    "https://github.com/trololo65/Modules",
    "https://github.com/Ijidishurka/modules",
    "https://github.com/Fl1yd/FTG-Modules",
    "https://github.com/D4n13l3k00/FTG-Modules",
    "https://github.com/iamnalinor/FTG-modules",
    "https://github.com/SekaiYoneya/modules",
    "https://github.com/GeekTG/FTG-Modules",
    "https://github.com/Den4ikSuperOstryyPer4ik/Astro-modules",
    "https://github.com/vsecoder/hikka_modules",
    "https://github.com/sqlmerr/hikka_mods",
    "https://github.com/N3rcy/modules",
    "https://github.com/KorenbZla/HikkaModules",
    "https://github.com/MuRuLOSE/HikkaModulesRepo",
    "https://github.com/C0dwiz/H.Modules",
    "https://github.com/coddrago/modules",
    "https://github.com/1jpshiro/hikka-modules",
    "https://github.com/MoriSummerz/ftg-mods",
    "https://github.com/anon97945/hikka-mods",
    "https://github.com/dorotorothequickend/DorotoroModules",
    "https://github.com/den4ikSuperOstryyPer4ik/astro-modules",
    "https://github.com/shadowhikka/sh.modules",
    "https://github.com/AmoreForever/amoremods",
    "https://github.com/dekkusudev/mm-hikka-mods",
    "https://github.com/idiotcoders/idiotmodules",
    "https://github.com/CakesTwix/Hikka-Modules",
    "https://github.com/Codwizer/ReModules",
    "https://github.com/GD-alt/mm-hikka-mods",
    "https://github.com/HitaloSama/FTG-modules-repo",
    "https://github.com/SekaiYoneya/Friendly-telegram",
    "https://github.com/blazedzn/ftg-modules",
    "https://github.com/hikariatama/ftg",
    "https://github.com/m4xx1m/FTG",
    "https://github.com/skillzmeow/skillzmods_hikka",
    "https://github.com/fajox1/famods",
    "https://github.com/HikkTutor/HT",
    "https://github.com/unneyon/hikka-mods",
]

for repo_url in repos:
    repo_path = repo_url.replace("https://github.com/", "")
    owner, repo_name = repo_path.split("/")
    local_path = f"{owner}/{repo_name}"

    # Создаем каталог для владельца, если его нет
    if not os.path.exists(owner):
        os.makedirs(owner)

    try:
        # Используем git subtree для добавления репозитория
        subprocess.run(
            [
                "git",
                "subtree",
                "add",
                "--prefix",
                local_path,
                repo_url,
                "main",
                "--squash",
            ],
            check=True,
        )

        print(f"Добавлен subtree: {repo_url} -> {local_path}")
    except subprocess.CalledProcessError:
        pass
