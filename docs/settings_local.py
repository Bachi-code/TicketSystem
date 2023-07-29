DEBUG = True

SECRET_KEY = 'django-insecure-dg9to5au+vvb_-r7j8#cl@@%(5t!u=d88+j)jatjui=!8tlm$t'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = ''
    EMAIL_HOST = ''
    EMAIL_PORT = ''
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
