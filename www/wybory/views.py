from django.template import loader
from django.http import HttpResponse
from wybory.models import Kandydat, Rapor, Województwo, Gmina, RodzajGminy
import functools;

def index(request):
    def add2(a, b):
        return a[0] + b[0], a[1] + b[1]
    def add4(a, b):
        return a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]

    def procrnt(a, b):
        if b == 0:
            return '0/0'
        else:
            return str(round(a / b * 100, 2))

    liczba_mieszkańców, liczba_uprawnionych, liczba_wydanych_kart, liczba_głosów_oddanych =\
        functools.reduce(add4,
                            [(raport.liczba_mieszkańców, raport.liczba_uprawnionych, raport.liczba_wydanych_kart,
                                raport.liczba_głosów_oddanych) for raport in Rapor.objects.all()],
                            (0,0,0,0)
                         )

    def glosy_na(*args, **kwargs):
        liczba_głosów_na_pierwszego = 0
        liczba_głosów_na_drugiego = 0
        for gmina in Gmina.objects.filter(*args, **kwargs):
            raport = Rapor.objects.filter(gmina=gmina)
            if len(raport) == 0:
                pass
            else:
                raport = raport[0]
                liczba_głosów_na_pierwszego += raport.liczba_głosów_na_pierwszego_kandydata
                liczba_głosów_na_drugiego += raport.liczba_głosów_na_drugiego_kandydata
        return (liczba_głosów_na_pierwszego, liczba_głosów_na_drugiego)

    class SetDateToTabe:
        def __init__(self, nazwa, na_pierwszego, na_drugiego):
            self.nazwa, self.licz_na_pi, self.licz_na_dr = nazwa, na_pierwszego, na_drugiego
            self.licz_wazny = na_pierwszego + na_drugiego
            self.proc_na_pi = procrnt(na_pierwszego, self.licz_wazny)
            self.proc_na_dr = procrnt(na_drugiego, self.licz_wazny)

    tabela_wejewodztw = map(lambda t: SetDateToTabe(t[0], t[1][0], t[1][1]),
                         [(wojwództwo.nazwa, glosy_na(wojwództwo=wojwództwo)) for wojwództwo in Województwo.objects.all()]
                             )

    po_kategorjach = map(lambda t : SetDateToTabe(t[0],t[1][0],t[1][1]),
                         [(rodzaj.rodzaj, glosy_na(rodzaj=rodzaj))for rodzaj in RodzajGminy.objects.all()]
                         )
    po_rozmiarze = functools.reduce(lambda ac, t: (ac[0] + t[0] + ', ', ac[1] + t[1][0], ac[2] + t[1][1]),
                                    [(rodzaj.rodzaj, glosy_na(rodzaj=rodzaj)) for rodzaj in RodzajGminy.objects.filter(z_województwem=False)],
                                     ('',0,0)
                                     )
    po_rozmiarze = [SetDateToTabe(po_rozmiarze[0][:-2], po_rozmiarze[1], po_rozmiarze[2])]
    if po_rozmiarze[0].nazwa == '': po_rozmiarze = []
    przedziały = [(0,100), (101,200),(201, 1000)]
    for przedział in przedziały:
        a,b = functools.reduce( add2,
                        [(raport.liczba_głosów_na_pierwszego_kandydata, raport.liczba_głosów_na_drugiego_kandydata)for raport in
                         Rapor.objects.filter(liczba_mieszkańców__gte=przedział[0], liczba_mieszkańców__lte=przedział[1])],
                        (0,0)
                        )
        po_rozmiarze.append(SetDateToTabe(str(przedział[0]) + ' - ' + str(przedział[1]),a,b))

    licz_na_pi, licz_na_dr = glosy_na()
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
        'proc_na_dr': procrnt(licz_na_dr, licz_na_pi + licz_na_dr),
        'tabela_wejewodztw' : tabela_wejewodztw,
        'po_kategorjach' : po_kategorjach,
        'po_rozmiarze' : po_rozmiarze,
    }
    return HttpResponse(template.render(context, request))