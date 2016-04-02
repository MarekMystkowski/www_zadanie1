from django.contrib import admin
from wybory.models import Województwo, RodzajGminy, Gmina, Kandydat, Rapor

@admin.register(Województwo, RodzajGminy, Gmina, Kandydat, Rapor)
class Model(admin.ModelAdmin): pass
