# main.py
from __init__ import app 

if __name__ == "__main__":
    with open("target.txt", "r", encoding="utf-8") as f:
        txt = f.read()
    result = app.process(txt)

    print("=== Result ===")

    if result["success"]:
        print("Success!")
        print(result["data"])
    else:
        print("Failed!")
        print(result["error"])