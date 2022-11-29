import launch, os, json
self_dir = os.path.dirname(os.path.realpath(__file__))

if not launch.is_installed("dokithemejupyter"):
    launch.run_pip("install doki-theme-jupyter", "doki-theme-jupyter")

# Just install it. I tried using the original theme definition files
# to avoid installing jupyter, but it gets messy quickly so I decided to bail.

# The below code does not work.

# if not os.path.isfile(os.path.join(self_dir, "themes.json")):
#     theme_repo = os.environ.get('DOKI_REPO', 'https://github.com/doki-theme/doki-master-theme.git')
#     theme_repo_dir = os.path.join(self_dir, "doki_themes")
#     launch.git_clone(theme_repo, theme_repo_dir, "Doki Theme", None)

#     theme_build_dir = os.path.join(theme_repo_dir, "definitions")

#     themes = {}

#     for (root, _, files) in os.walk(theme_build_dir):
#         for file in files:
#             try:
#                 if file.endswith(".json"):
#                     with open(os.path.join(root, file), encoding = "utf-8") as fp:
#                         theme_data = json.load(fp)
                    
#                     if "errorColor" not in theme_data["colors"]:
#                         print("WARNING: No error color!")
#                     if "lineNumberColor" not in theme_data["colors"]:
#                         print("WARNING: No line number color!")
#                     if "foregroundColorEditor" not in theme_data["colors"]:
#                         print("WARNING: No foregroundColorEditor!")

#                     theme_name = "{group}: {name}".format(**theme_data)
#                     themes[theme_name] = theme_data

#             except (IOError, KeyError, json.JSONDecodeError):
#                 pass
    
#     with open(os.path.join(self_dir, "themes.json"), "w", encoding = "utf-8") as fp:
#         json.dump(themes, fp)