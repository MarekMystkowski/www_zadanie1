from datetime import timezone

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from wybory.models import Kandydat, Rapor, Województwo, Gmina, RodzajGminy
import re, json, datetime, functools
from django.contrib.auth.decorators import login_required


# przedziały jakie mają się pojawić w tabeli:
przedziały = [(0, 5000), (5001, 10000), (10001, 20000), (20001, 50000), (50001, 100000), (100001, 200000),
              (200001, 500000), (500001, 5000000)]

# kolory do tabeli:
kolor_dla_równych = "#f2f1f6"
kolory = [('#e7deeb', '#fdeae2'), ('#d9cce0', '#fcded3'), ('#c6b2d1', '#fbcdbc'), ('#a180b2', '#f8ac90'),
          ('#8e67a3', '#f79c7a'),
          ('#7b4d94', '#f58b64'), ('#693485', '#f47b4e'), ('#5a2079', '#f26a38'), ('#4d0e6e', '#f15a22'),
          ('#410360', '#f54200')]

# nazwa województwa a id na mapie
mapa_pola = {"Dolnośląskie": "land1", "Kujawsko-Pomorskie": "land2", "Łódzkie": "land3", "Lubelskie": "land4",
             "Lubuskie": "land5",
             "Małopolskie": "land6", "Mazowieckie": "land7", "Opolskie": "land8", "Podkarpackie": "land9",
             "Podlaskie": "land10",
             "Pomorskie": "land11", "Śląskie": "land12", "Świętokrzyskie": "land13", "Warmińsko-Mazurskie": "land14",
             "Wielkopolskie": "land15", "Zachodniopomorskie": "land16"}


# funkcje i klasy pomocnicze:
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
    def __init__(self, nazwa, na_pierwszego, na_drugiego, id ='' ):
        self.nazwa, self.licz_na_pi, self.licz_na_dr = nazwa, na_pierwszego, na_drugiego
        self.licz_wazny = na_pierwszego + na_drugiego
        self.proc_na_pi = procent(na_pierwszego, self.licz_wazny)
        self.proc_na_dr = procent(na_drugiego, self.licz_wazny)
        self.id = id

class SetDateWithRaportToTabe:
    def __init__(self, raport ):
        self.nazwa = str(raport.gmina)
        self.licz_na_pi = raport.liczba_głosów_na_pierwszego_kandydata
        self.licz_na_dr = raport.liczba_głosów_na_drugiego_kandydata
        self.licz_wazny = self.licz_na_pi + self.licz_na_dr
        self.proc_na_pi = procent(self.licz_na_pi, self.licz_wazny)
        self.proc_na_dr = procent(self.licz_na_dr, self.licz_wazny)
        self.id = raport.gmina.id
        self.licz_miesz = raport.liczba_mieszkańców
        self.licz_upraw = raport.liczba_uprawnionych
        self.licz_wydan = raport.liczba_wydanych_kart
        self.licz_oddan = raport.liczba_głosów_oddanych

def index(request):

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



def load_gmin(request ) :
    if request.method == 'GET':
        kategoria = request.GET.get('kategoria')
        wartos = request.GET.get('wartos')

        gminy = []
        pod_tytul = '...'
        def select_gmin(*args, **kwargs):
            for elem in map(lambda raport: SetDateWithRaportToTabe(raport),
                            [(Rapor.objects.all().filter(gmina=gmina)[0]) for gmina in
                             Gmina.objects.all().filter(*args, **kwargs)]
                            ):
                gminy.append(elem)

        if kategoria == 'wojewodztwo':
            select_gmin(wojwództwo = wartos)
            pod_tytul = 'Gminy z województwa ' + wartos

        if kategoria == 'kategoria':
            select_gmin(rodzaj=wartos)
            pod_tytul = 'Gminy rodzaju ' + wartos

        if kategoria == 'rozmiar':
            reg = re.compile(r"(\d+) - (\d+)")
            mat = reg.match(wartos)
            if mat == None:
                pod_tytul = 'Wybrałes kategorię po rozmarze <\br> a to sa gminy których się nie dotyczy rozmiar'
                for rodzaj in  RodzajGminy.objects.all().filter(z_województwem=False):
                    select_gmin(rodzaj = rodzaj)
            else:
                od, do = mat.group(1) , mat.group(2)
                pod_tytul = 'Gminy o zamieszkalności od ' + od + ' do ' + do + 'mieszkańców'
                for raport in Rapor.objects.all().filter(liczba_mieszkańców__gte = int(od), liczba_mieszkańców__lte = int(do)):
                    gminy.append(SetDateWithRaportToTabe(raport))

        context = {
            'gminy' : gminy,
            'pod_tytul' : pod_tytul,
            'kand_pierw': str(Kandydat.objects.all()[0]),
            'kand_drugi': str(Kandydat.objects.all()[1]),
            'czas_danych' : str(datetime.datetime.now()),

            }
        return render(request, 'wybory/load_gmin.html', context)

    return HttpResponseRedirect("/")

def save_data(request):
    if request.method == 'GET':
        gmina = Gmina.objects.all().filter(id = request.GET.get('id'))[0]
        na_pierwszego = int(request.GET.get('na_pierwszego'))
        na_drugiego = int(request.GET.get('na_drugiego'))
        odanych = int(request.GET.get("odanych"))
        wydanych = int(request.GET.get("wydanych"))
        uprawnionych = int(request.GET.get("uprawnionych"))
        mieszkancow = int(request.GET.get("mieszkancow"))
        date_str = request.GET.get("date")

        sukces = True
        komunikat = ''
        raport = Rapor.objects.all().filter(gmina=gmina)[0]
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(hours=2)

        except ValueError:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=2)
        if raport.data_modyfikacji.astimezone(datetime.timezone.utc).replace(tzinfo=None) < date:
            raport.liczba_głosów_na_pierwszego_kandydata = na_pierwszego
            raport.liczba_głosów_na_drugiego_kandydata = na_drugiego
            raport.liczba_głosów_oddanych = odanych
            raport.liczba_wydanych_kart = wydanych
            raport.liczba_uprawnionych = uprawnionych
            raport.liczba_mieszkańców = mieszkancow
            raport.save()
        else:
            print ( "<")
            sukces = False;

            context = {
                'datazmiany': raport.data_modyfikacji.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                'zmieniajacy': '',
                'kand_pierw': str(Kandydat.objects.all()[0]),
                'kand_drugi': str(Kandydat.objects.all()[1]),
                'str_mirsz': mieszkancow,
                'str_upraw': uprawnionych,
                'str_wydan': wydanych,
                'str_oddan': odanych,
                'str_pierw': na_pierwszego,
                'str_pi_pr': '',
                'str_dr_pr': '',
                'str_drugi': na_drugiego,
                'now_mirsz': raport.liczba_mieszkańców,
                'now_upraw': raport.liczba_uprawnionych,
                'now_wydan': raport.liczba_wydanych_kart,
                'now_oddan': raport.liczba_głosów_oddanych,
                'now_pierw': raport.liczba_głosów_na_pierwszego_kandydata,
                'now_pi_pr': '',
                'now_dr_pr': '',
                'now_drugi': raport.liczba_głosów_na_drugiego_kandydata,
            }
            komunikat = "<h4>Dane zostały zmienione o " + str(raport.data_modyfikacji.astimezone(datetime.timezone.utc).replace(tzinfo=None)) +\
                        " </h4> <h5>" + str(gmina) + "</h5><div class=\"tabela\"><div><div>wersja</div><div>Liczba mieszkańców</div><div>Liczba uprawinionych</div><div>Liczba wydanych kart</div><div>Liczba oddanych</div><div>"+  str(Kandydat.objects.all()[0]) +"""</div><div></div><div>Proporcje</div><div></div><div>"""+ str(Kandydat.objects.all()[1])+ """</div><div> </div></div > <div > <div > moja </div ><div > """+str(mieszkancow)+""" </div > <div > """+str(uprawnionych)+""" </div ><div > """+str(wydanych)+""" </div ><div > """+str(odanych)+""" </div ><div > """+str(na_pierwszego)+""" </div ><div >"""+\
                 procent(na_pierwszego, na_drugiego+na_pierwszego) +"% </div><div><div class =\"mapbar2\" ><img src = \"/static/wybory/pasekA.png\"  width = \""+procent(na_pierwszego, na_drugiego+na_pierwszego)+"%\"class =\"bark1\" ></div ></div> <div> "+procent(na_drugiego, na_drugiego+na_pierwszego)+"%</div>" +\
                "<div> "+str(na_drugiego)+" </div><div><button onclick = \"upDateMy("+ str(gmina.id) + ") " +\
                """">Nadpisz mojmi.</button>
                        </div>
                    </div>
                    <div>
                        <div>Nowsze dane</div>
                        <div>"""+str(raport.liczba_mieszkańców)+"""</div>
                        <div>"""+str(raport.liczba_uprawnionych)+"""</div>
                        <div>"""+str(raport.liczba_wydanych_kart)+"""</div>
                        <div>"""+str(raport.liczba_głosów_oddanych)+"""</div>
                        <div>"""+str(raport.liczba_głosów_na_pierwszego_kandydata)+"""</div>
                        <div>"""+procent(raport.liczba_głosów_na_pierwszego_kandydata, raport.liczba_głosów_na_pierwszego_kandydata + raport.liczba_głosów_na_drugiego_kandydata)+"""%</div>
                        <div>
                            <div class="mapbar2">
                                <img src="/static/wybory/pasekA.png" width="""+procent(raport.liczba_głosów_na_pierwszego_kandydata, raport.liczba_głosów_na_pierwszego_kandydata + raport.liczba_głosów_na_drugiego_kandydata)+"""% class="bark1">
                            </div>
                        </div>
                        <div>"""+procent(raport.liczba_głosów_na_drugiego_kandydata, raport.liczba_głosów_na_pierwszego_kandydata + raport.liczba_głosów_na_drugiego_kandydata)+"""%</div>
                        <div>"""+str(raport.liczba_głosów_na_drugiego_kandydata)+"""</div>
                        <div>
                             <button onclick="upDate("""+str(gmina.id)+""", """+str(raport.liczba_mieszkańców)+""", """+str(raport.liczba_uprawnionych)+""", """+str(raport.liczba_wydanych_kart)+""", """+str(raport.liczba_głosów_oddanych)+""", """+str(raport.liczba_głosów_na_pierwszego_kandydata)+""", """+procent(raport.liczba_głosów_na_pierwszego_kandydata, raport.liczba_głosów_na_drugiego_kandydata + raport.liczba_głosów_na_pierwszego_kandydata)+""", """+str(raport.liczba_głosów_na_drugiego_kandydata)+""", """+procent(raport.liczba_głosów_na_drugiego_kandydata, raport.liczba_głosów_na_drugiego_kandydata + raport.liczba_głosów_na_pierwszego_kandydata)+""")">Zakceptuj te dane.</button>
                         </div>
                    </div>
                </div>
            """





        out = {
            'sukces' : sukces,
            'wazn' : na_pierwszego + na_drugiego,
            'naPP' : procent(na_pierwszego, na_pierwszego + na_drugiego),
            'naDP' : procent(na_drugiego, na_pierwszego + na_drugiego),
            'date' : str(datetime.datetime.now()),
            'miesz': raport.liczba_mieszkańców,
            'upraw': raport.liczba_uprawnionych,
            'wydan': raport.liczba_wydanych_kart,
            'oddan': raport.liczba_głosów_oddanych,
            'miesz': raport.liczba_mieszkańców,
            'naPi' : raport.liczba_głosów_na_pierwszego_kandydata,
            'naDr' : raport.liczba_głosów_na_drugiego_kandydata,
            'komunikat' : komunikat,

        }

        return HttpResponse({json.dumps(out)})
    return HttpResponseRedirect("/")