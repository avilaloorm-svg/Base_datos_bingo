from django.contrib import admin

# Register your models here.
from .models import TipoSocio, Socio, Prestamo,CuentaBancaria,Prestamo, Jugador, Carton, CartonPartidaBingo, PlataformaJuego, SesionJuego, Regalo, AporteSemanal


admin.site.register(TipoSocio)
admin.site.register(Socio)
admin.site.register(Prestamo)
admin.site.register(CuentaBancaria)
admin.site.register(Jugador)
admin.site.register(Carton)
admin.site.register(CartonPartidaBingo)
admin.site.register(PlataformaJuego)
admin.site.register(SesionJuego)
admin.site.register(Regalo)
admin.site.register(AporteSemanal)