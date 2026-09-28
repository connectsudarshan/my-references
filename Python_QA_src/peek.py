"""Dev helper: print question + executed output for one section. python peek.py 3"""
import sys, build
sec = int(sys.argv[1])
for q in build.load():
    if q["section"] == sec and q["run"]:
        print("###", q["question"][:90]); print(build.execute(q)); print()
