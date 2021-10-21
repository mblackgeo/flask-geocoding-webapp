import bjoern
from webmap.main import app

bjoern.listen(wsgi_app=app, host="0.0.0.0", port=5000, reuse_port=True)
bjoern.run()
