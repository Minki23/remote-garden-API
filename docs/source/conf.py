
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../agent_app'))
sys.path.insert(0, os.path.abspath('../../common_db'))
sys.path.insert(0, os.path.abspath('../../delivery_app'))

project = 'Agent App'
author = 'Your Team'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',]


autodoc_mock_imports = [
    "services",
    "services.agent",
    "api",
    "api.core",
]

suppress_warnings = ["ref.ref"]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
