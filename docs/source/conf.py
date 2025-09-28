
import os
import sys
import types

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../agent_app'))
sys.path.insert(0, os.path.abspath('../../common_db'))
sys.path.insert(0, os.path.abspath('../../delivery_app'))
sys.path.insert(0, os.path.abspath('../../api_app'))

project = 'Remote Garden App'
author = 'MK`s Team'
release = '1.0.0'

autodoc_typehints = "none"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',]


autodoc_mock_imports = [
    "core.db_context",
    "fastapi",
    "sqlalchemy",
    "sqlalchemy.ext.asyncio"
    "aiomqtt",
    "redis",
    "celery",
    "firebase_admin",
    "core",
    "controllers",
    "sqlalchemy",
    "aiosqlite",
    "api_app.core.db_context",
]
html_static_path = ['_static']

redbeat_stub = types.ModuleType("redbeat")
redbeat_schedulers_stub = types.ModuleType("redbeat.schedulers")


class Dummy:
    pass


redbeat_stub.RedBeatSchedulerEntry = Dummy
redbeat_stub.RedBeatScheduler = Dummy

sys.modules["redbeat"] = redbeat_stub
sys.modules["redbeat.schedulers"] = redbeat_schedulers_stub

suppress_warnings = ["ref.ref"]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
