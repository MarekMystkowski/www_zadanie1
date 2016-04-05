from django.shortcuts import render
from wybory.models import Kandydat, Rapor, Województwo, Gmina, RodzajGminy
import functools;

def index(request):

    #dane do ustawienia ręcznego:

    #przedziały jakie mają się pojawić w tabeli:
    przedziały = [(0, 100), (101, 200), (201, 1000)]

    #kolory do tabeli:
    kolor_dla_równych = "#f2f1f6"
    kolory= [('#e7deeb', '#fdeae2'), ('#d9cce0', '#fcded3'), ('#c6b2d1', '#fbcdbc'), ('#a180b2', '#f8ac90'), ('#8e67a3', '#f79c7a'),
             ('#7b4d94', '#f58b64'), ('#693485', '#f47b4e'), ('#5a2079', '#f26a38'), ('#4d0e6e', '#f15a22'), ('#410360', '#f54200')]

    #nazwa województwa a id na mapie
    mapa_pola = {"Dolnośląskie":"land1", "Kujawsko-Pomorskie":"land2", "Łódzkie":"land3", "Lubelskie":"land4", "Lubuskie":"land5",
                 "Małopolskie":"land6", "Mazowieckie":"land7", "Opolskie":"land8", "Podkarpackie":"land9", "Podlaskie":"land10",
                 "Pomorskie":"land11", "Śląskie":"land12", "Świętokrzyskie":"land13", "Warmińsko-Mazurskie":"land14",
                 "Wielkopolskie":"land15", "Zachodniopomorskie":"land16"}

    #funkcje i klasy pomocnicze:
    def add2(a, b):
        return a[0] + b[0], a[1] + b[1]

    def add4(a, b):
        return a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]

    def procent(a, b):
        if b == 0:
            return '0/0'
        else:
            return str(round(a / b * 100, 2))

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
            self.proc_na_pi = procent(na_pierwszego, self.licz_wazny)
            self.proc_na_dr = procent(na_drugiego, self.licz_wazny)


    #dane ogólne do wypisania:
    liczba_mieszkańców, liczba_uprawnionych, liczba_wydanych_kart, liczba_głosów_oddanych = \
        functools.reduce(add4,
                         [(raport.liczba_mieszkańców, raport.liczba_uprawnionych, raport.liczba_wydanych_kart,
                           raport.liczba_głosów_oddanych) for raport in Rapor.objects.all()],
                         (0, 0, 0, 0)
                         )
    licz_na_pi, licz_na_dr = glosy_na()


    #tabela po województwach:
    tabela_wejewodztw = []
    for elem in map(lambda t: SetDateToTabe(t[0], t[1][0], t[1][1]),
                         [(wojwództwo.nazwa, glosy_na(wojwództwo=wojwództwo)) for wojwództwo in Województwo.objects.all()]
                             ):
        tabela_wejewodztw.append(elem)


    #tabela po kategorjach:
    po_kategorjach =  []
    for elem in map(lambda t : SetDateToTabe(t[0],t[1][0],t[1][1]),
                         [(rodzaj.rodzaj, glosy_na(rodzaj=rodzaj))for rodzaj in RodzajGminy.objects.all()]
                         ):
        po_kategorjach.append(elem)


    #tabela po rozmiarach:
    po_rozmiarze = functools.reduce(lambda ac, t: (ac[0] + t[0] + ', ', ac[1] + t[1][0], ac[2] + t[1][1]),
                                    [(rodzaj.rodzaj, glosy_na(rodzaj=rodzaj)) for rodzaj in RodzajGminy.objects.filter(z_województwem=False)],
                                     ('',0,0)
                                     )
    po_rozmiarze = [SetDateToTabe(po_rozmiarze[0][:-2], po_rozmiarze[1], po_rozmiarze[2])]
    if po_rozmiarze[0].nazwa == '': po_rozmiarze = []
    for przedział in przedziały:
        a,b = functools.reduce( add2,
                        [(raport.liczba_głosów_na_pierwszego_kandydata, raport.liczba_głosów_na_drugiego_kandydata)for raport in
                         Rapor.objects.filter(liczba_mieszkańców__gte=przedział[0], liczba_mieszkańców__lte=przedział[1])],
                        (0,0)
                        )
        po_rozmiarze.append(SetDateToTabe(str(przedział[0]) + ' - ' + str(przedział[1]),a,b))


    # mapa wraz z tabelką:
    minimalny_procent = 50
    for iter in tabela_wejewodztw:
        if iter.licz_wazny != 0:
            minimalny_procent = min(minimalny_procent,
                                    100 * min(iter.licz_na_pi, iter.licz_na_dr) / iter.licz_wazny)
    if minimalny_procent == 50: minimalny_procent = 40
    skok = (50 - minimalny_procent) / len(kolory)

    class EleTabKol:
        def __init__(self, przedzial, kolorA, kolorB):
            self.przedzial, self.kolorA, self.kolorB = przedzial, kolorA, kolorB

    class EleTabKolNaMap:
        def __init__(self, land, kolor):
            self.land, self.color,  = land, kolor

    tmp = 50
    tab_kolorow = [EleTabKol("50", kolor_dla_równych, kolor_dla_równych)]
    for kolor in kolory:
        tmp += skok
        tab_kolorow.append(EleTabKol(procent(tmp, 100), kolor[0], kolor[1]))

    kolory_na_mapie = []
    def kolor(na_pierwszego):
        na_pierwszego = float(na_pierwszego)
        ile = int((max(na_pierwszego, 100 - na_pierwszego) - 50.00001)/skok)
        if na_pierwszego == 50: return kolor_dla_równych
        if na_pierwszego < 50: return tab_kolorow[ile + 1].kolorB
        return tab_kolorow[ile + 1].kolorA

    for iter in tabela_wejewodztw:
        try:
            kolory_na_mapie.append(EleTabKolNaMap(mapa_pola[iter.nazwa], kolor(iter.proc_na_pi)))
        except: pass



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
        'frekwencja' : procent(liczba_głosów_oddanych, liczba_uprawnionych),
        'proc_na_pi' : procent(licz_na_pi, licz_na_pi + licz_na_dr),
        'proc_na_dr': procent(licz_na_dr, licz_na_pi + licz_na_dr),
        'tabela_wejewodztw' : tabela_wejewodztw,
        'po_kategorjach' : po_kategorjach,
        'po_rozmiarze' : po_rozmiarze,
        'tab_kolorow' : tab_kolorow,
        'kolory_na_mapie' : kolory_na_mapie
    }
    return render(request, 'wybory/index.html', context)