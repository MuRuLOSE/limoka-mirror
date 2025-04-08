import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from tqdm import tqdm
import numpy as np

# Тренировочные данные (48 модулей)
training_data = {
    "MuRuLOSE/HikkaModulesRepo/filters.py": ["Tools", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/autogiveawayjoin.py": ["Automation", "Social"],
    "MuRuLOSE/HikkaModulesRepo/HTTPCat.py": ["Fun"],
    "MuRuLOSE/HikkaModulesRepo/CustomPing.py": ["Tools", "Networking"],
    "MuRuLOSE/HikkaModulesRepo/FuckTagOne.py": ["Moderation"],
    "MuRuLOSE/HikkaModulesRepo/InlineButtons.py": ["Tools", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/YoutubeDL.py": ["Media"],
    "MuRuLOSE/HikkaModulesRepo/youtubesearcher.py": ["Media", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/INumber.py": ["Fun", "Info"],
    "MuRuLOSE/HikkaModulesRepo/RandomDog.py": ["Fun"],
    "MuRuLOSE/HikkaModulesRepo/RemoveLinks.py": ["Moderation", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/SteamClient.py": ["Games", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/PinMoreChats.py": ["Chat", "Productivity"],
    "MuRuLOSE/HikkaModulesRepo/MindGameCheat.py": ["Games", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/NasaImages.py": ["Media", "Info"],
    "MuRuLOSE/HikkaModulesRepo/autoreader.py": ["Automation", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/K.py": ["Fun"],
    "MuRuLOSE/HikkaModulesRepo/Genshin.py": ["Games"],
    "MuRuLOSE/HikkaModulesRepo/compliments.py": ["Social", "Fun"],
    "MuRuLOSE/HikkaModulesRepo/AutoLeave.py": ["Automation", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/ToTHosting.py": ["Tools", "Admin"],
    "MuRuLOSE/HikkaModulesRepo/PasswordUtils.py": ["Security", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/FuckJoins.py": ["Security", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/SpyEVO.py": ["Tools", "Info"],
    "MuRuLOSE/HikkaModulesRepo/FindID.py": ["Tools", "Admin"],
    "MuRuLOSE/HikkaModulesRepo/ChannelCheck.py": ["Tools", "Social"],
    "MuRuLOSE/HikkaModulesRepo/controlspam.py": ["Chat", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/VKMusic.py": ["Media"],
    "MuRuLOSE/HikkaModulesRepo/morse.py": ["Tools", "Fun"],
    "MuRuLOSE/HikkaModulesRepo/YamiManager.py": ["Chat", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/SearchersGenQuery.py": ["Tools", "Info"],
    "MuRuLOSE/HikkaModulesRepo/Limoka.py": ["Utilities", "Tools"],
    "MuRuLOSE/HikkaModulesRepo/CheckTime.py": ["Productivity", "Info"],
    "MuRuLOSE/HikkaModulesRepo/ReplaceWords.py": ["Chat", "Customization"],
    "MuRuLOSE/HikkaModulesRepo/TempJoinChannel.py": ["Chat", "Automation"],
    "MuRuLOSE/HikkaModulesRepo/timer.py": ["Productivity", "Tools"],
    "den4ikSuperOstryyPer4ik/astro-modules/astroafk.py": ["Automation", "Customization"],
    "den4ikSuperOstryyPer4ik/astro-modules/akinator.py": ["Games"],
    "den4ikSuperOstryyPer4ik/astro-modules/Emotions.py": ["Social", "Fun"],
    "den4ikSuperOstryyPer4ik/astro-modules/RandomStatuses.py": ["Social", "Fun"],
    "den4ikSuperOstryyPer4ik/astro-modules/RandomTrack.py": ["Media", "Fun"],
    "den4ikSuperOstryyPer4ik/astro-modules/minesweeper.py": ["Games"],
    "den4ikSuperOstryyPer4ik/astro-modules/inline_bot_manager.py": ["Tools", "Automation"],
    "MuRuLOSE/HikkaModulesRepo/ReplaceWords.py": ["Customization", "Chat"],
    "MuRuLOSE/HikkaModulesRepo/CheckTime.py": ["Productivity"],
    "MuRuLOSE/HikkaModulesRepo/SearchersGenQuery.py": ["Utilities", "Info"]
}

all_categories = [
    "Utilities", "Fun", "Admin", "Media", "Games", "Tools", "Security", "Social",
    "Automation", "Info", "Chat", "Moderation", "Productivity", "Customization",
    "Networking", "Education", "Finance", "Health", "Creative", "Other"
]

def get_module_text(module_path, module_data):
    name = module_data.get("name", "").lower()
    description = (module_data.get("description", "") or module_data.get("meta", {}).get("desc", "")).lower()
    if not description or description == "desc":
        description = ""
    commands_text = " ".join([f"{cmd} {desc}".lower() for func in module_data.get("commands", []) for cmd, desc in func.items()])
    new_commands_text = " ".join([f"{cmd} {data.get('doc', '')} {data.get('ru_doc', '') or ''}".lower()
                                 for func in module_data.get("new_commands", []) for cmd, data in func.items()])
    file_path = module_path.lower()
    file_name = file_path.split("/")[-1]
    return f"{file_name} {name} {description} {file_path} {commands_text} {new_commands_text}".strip()


with open("modules.json", "r", encoding="utf-8") as f:
    modules = json.load(f)

# Подготовка тренировочных данных
train_texts = [get_module_text(path, modules[path]) for path in training_data.keys() if path in modules]
train_labels = [training_data[path] for path in training_data.keys() if path in modules]

# Векторизация текста
vectorizer = TfidfVectorizer(max_features=2000)
X_train = vectorizer.fit_transform(train_texts)

# Преобразование меток
mlb = MultiLabelBinarizer(classes=all_categories)
y_train = mlb.fit_transform(train_labels)

# Обучение модели с балансировкой классов
base_clf = LogisticRegression(class_weight="balanced", max_iter=1000)
clf = OneVsRestClassifier(base_clf)
clf.fit(X_train, y_train)

# Обработка всех модулей
print("Classifying all modules...")
texts = [get_module_text(path, data) for path, data in modules.items()]
X_all = vectorizer.transform(texts)

# Предсказание вероятностей
probs = clf.predict_proba(X_all)

# Присваивание категорий
threshold = 0.2  # Снижаем порог для большего разнообразия
for module_path, prob_vector in tqdm(zip(modules.keys(), probs), total=len(modules), desc="Assigning categories"):
    module_data = modules[module_path]
    sorted_indices = np.argsort(prob_vector)[::-1]
    sorted_probs = prob_vector[sorted_indices]
    sorted_labels = mlb.classes_[sorted_indices]
    
    selected_categories = [label for label, prob in zip(sorted_labels, sorted_probs) if prob >= threshold][:2]
    
    if not selected_categories:
        selected_categories = ["Other"]
    
    module_data["category"] = selected_categories
    print(f"Module: {module_path} -> Categories: {selected_categories} (top probs: {[f'{p:.2f}' for p in sorted_probs[:3]]})")

# Сохранение результата
with open("modules.json", "w", encoding="utf-8") as f:
    json.dump(modules, f, ensure_ascii=False, indent=2)

print("Done! Check modules_categorized.json.")