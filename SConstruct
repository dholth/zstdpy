# Starter SConstruct for enscons
# (filled by enscons.setup2toml)

import enscons
import pytoml as toml

metadata = dict(toml.load(open("pyproject.toml")))["tool"]["enscons"]

full_tag = enscons.get_universal_tag()

env = Environment(
    tools=["default", "packaging", enscons.generate],
    PACKAGE_METADATA=metadata,
    WHEEL_TAG=full_tag,
    ROOT_IS_PURELIB=full_tag.endswith("-any"),
)

# Only *.py is included automatically by setup2toml.
# Add extra 'purelib' files or package_data here.
py_source = ['zstddec.py', 'zstddec.wasm']

purelib = env.Whl("purelib", py_source, root='')
whl = env.WhlFile(purelib)

# Add automatic source files, plus any other needed files.
sdist_source = FindSourceFiles() + ["PKG-INFO"]

sdist = env.SDist(source=sdist_source)

env.NoClean(sdist)
env.Alias("sdist", sdist)

# needed for pep517 / enscons.api to work
env.Default(whl, sdist)
