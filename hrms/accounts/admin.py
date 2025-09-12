from django.contrib import admin
from django.apps import apps

# Get all models from the current app
app = apps.get_app_config('accounts')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Skip if already registered
