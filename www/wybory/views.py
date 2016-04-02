from django.template import loader
from django.http import HttpResponse
from wybory.models import Kandydat, Rapor

def index(request):
    liczba_mieszkańców = 0
    liczba_uprawnionych = 0
    liczba_wydanych_kart = 0
    liczba_głosów_oddanych = 0
    for raport in Rapor.objects.all():
        liczba_mieszkańców += raport.liczba_mieszkańców
        liczba_wydanych_kart += raport.liczba_wydanych_kart
        liczba_głosów_oddanych += raport.liczba_głosów_oddanych
        liczba_uprawnionych += raport.liczba_uprawnionych

    # Dać dekord do zapisywania zmian (by bazy nie przeciążać)
    def glosy_na(*args, **kwargs):
        liczba_głosów_na_pierwszego = 0
        liczba_głosów_na_drugiego = 0
        for raport in Rapor.objects.filter(*args, **kwargs):
            liczba_głosów_na_pierwszego += raport.liczba_głosów_na_pierwszego_kandydata
            liczba_głosów_na_drugiego += raport.liczba_głosów_na_drugiego_kandydata
        return (liczba_głosów_na_pierwszego, liczba_głosów_na_drugiego)

    def procrnt(a, b):
        if b == 0: return '0/0'
        else: return str((a / b * 100) + 0.005)[:5] + ' %'

    licz_na_pi = glosy_na()[0]
    licz_na_dr = glosy_na()[1]
    template = loader.get_template('wybory/index.html')
    context = {
        'kand_pierw': str(Kandydat.objects.all()[0]),
        'kand_drugi': str(Kandydat.objects.all()[1]),
        'licz_miesz' : liczba_mieszkańców,
        'licz_upraw' : liczba_uprawnionych,
        'licz_wydan' : liczba_wydanych_kart,
        'licz_oddan' : liczba_głosów_oddanych,
        'licz_na_pi' : licz_na_pi,
        'licz_na_dr' : licz_na_dr,
        'licz_wazny' : licz_na_pi + licz_na_dr,
        'frekwencja' : procrnt(liczba_głosów_oddanych, liczba_uprawnionych),
        'proc_na_pi' : procrnt(licz_na_pi, licz_na_pi + licz_na_dr),
        'proc_na_dr': procrnt(licz_na_dr, licz_na_pi + licz_na_dr)
    }
    return HttpResponse(template.render(context, request))