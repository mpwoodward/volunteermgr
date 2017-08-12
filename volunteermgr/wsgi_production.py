import os
from sys import path


SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path.append(SITE_ROOT)


from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
