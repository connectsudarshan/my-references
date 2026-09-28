"""Dev helper: print executed output for one module.  python peek.py 3"""
import sys, build
mods, qs = build.load()
for q in qs:
    if q["module"] == int(sys.argv[1]) and q["run"]:
        print("###", q["question"][:95]); print(build.execute(q)); print()
