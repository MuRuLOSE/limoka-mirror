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
    "https://github.com/TheKsenon/MyHikkaModules",
]


def update_subtree(repo_url):
    """Обновляет subtree в локальной папке."""
    repo_path = repo_url.replace("https://github.com/", "")
    owner, repo_name = repo_path.split("/")
    local_path = f"{owner}/{repo_name}"

    if not os.path.exists(local_path):
        print(f"Пропускаем {repo_name}, так как папка не найдена")
        return

    print(f"Обновляем {repo_name}...")
    try:
        subprocess.run(
            [
                "git",
                "subtree",
                "pull",
                "--prefix",
                local_path,
                repo_url,
                "main",
                "--squash",
            ],
            check=True,
        )
        print(f"✅ {repo_name} успешно обновлён!")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(
                [
                    "git",
                    "subtree",
                    "pull",
                    "--prefix",
                    local_path,
                    repo_url,
                    "master",
                    "--squash",
                ],
                check=True,
            )
            print(f"✅ {repo_name} успешно обновлён (ветка master)!")
        except subprocess.CalledProcessError:
            print(f"❌ Ошибка обновления {repo_name}, пропускаем.")


if __name__ == "__main__":
    for repo in repos:
        update_subtree(repo)
