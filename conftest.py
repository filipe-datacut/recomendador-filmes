import os
import tempfile

# Aponta o app para um banco temporario descartavel ANTES de importar a app,
# para os testes nunca tocarem no banco real.
_fd, _path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.remove(_path)
os.environ["RECOMMENDER_DB"] = _path