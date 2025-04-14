import json
str = """
 [
  {"text": "kingdomhearts-release-P72978", "bounding_box": [29, 847, 43, 972]},
  {"text": "UNDERWORLD", "bounding_box": [126, 685, 147, 786]},
  {"text": "GANG WARS", "bounding_box": [153, 693, 175, 777]},
  {"text": "As Guest", "bounding_box": [252, 711, 270, 759]},
  {"text": "Google", "bounding_box": [373, 716, 391, 754]},
  {"text": "I have read and agree to the", "bounding_box": [658, 696, 671, 801]},
  {"text": "Terms Of Service", "bounding_box": [691, 696, 704, 759]},
  {"text": "Privacy Policies.", "bounding_box": [754, 666, 767, 730]},
  {"text": "Help", "bounding_box": [927, 62, 941, 80]}
]
"""

jarray = json.loads(str)
for obj in jarray:
    for key in obj:
        # print("key:", key, " value:", obj[key])
        if key == "text" and obj[key] == "Google":
            print(obj["bounding_box"])