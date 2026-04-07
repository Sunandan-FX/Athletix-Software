from django.apps import AppConfig

#app added in user folder
class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    
