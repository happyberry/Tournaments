from django.contrib import admin
from .models import Tournament, Logo, Participation, Game

# Register your models here.


admin.site.register(Tournament)
admin.site.register(Logo)
admin.site.register(Participation)
admin.site.register(Game)
