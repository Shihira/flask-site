import importlib

from common.utils import (
        find_modules,
        BlueprintSet
    )

bps = BlueprintSet()

for pkgname in find_modules(__file__):
    submod = importlib.import_module("." + pkgname, __name__)
    if hasattr(submod, "blueprint"):
        bps.add_blueprint(pkgname, submod.blueprint)

