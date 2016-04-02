# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError

class Województwo(models.Model):
    nazwa = models.CharField(max_length=50, primary_key=True)
    class Meta:
        ordering = ['nazwa']
        verbose_name_plural = 'województwa'
    def __str__(self):
        return self.nazwa

class RodzajGminy(models.Model):
    rodzaj = models.CharField(max_length=50, primary_key=True)
    z_województwem = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'Rodzaj gminy'
        verbose_name_plural = 'rodzaje gmin'
    def __str__(self):
        return self.rodzaj

class Gmina(models.Model):
    nazwa = models.CharField(max_length=50)
    rodzaj = models.ForeignKey(RodzajGminy)
    wojwództwo = models.ForeignKey(Województwo, blank=True, null=True) # np. statki nei posiadają województwa
    class Meta:
        unique_together = ('nazwa', 'rodzaj', 'wojwództwo')
        verbose_name_plural = 'gminy'
    def clean(self):
        if self.rodzaj.z_województwem:
            if self.wojwództwo is None:
                raise ValidationError({'wojwództwo': 'Wymagane podanie województwa gdy rodzaj gminy to ' +
                                                str(self.rodzaj) + '.'})
        else:
            if self.wojwództwo is not None:
                raise ValidationError({'wojwództwo': str(self.rodzaj) + ' nie potrzebuje określania województwa.'})
    def __str__(self):
        return self.nazwa + u'  (' + self.rodzaj.rodzaj + u')'

class Kandydat(models.Model):
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    class Meta:
        unique_together = ('imie', 'nazwisko')
        verbose_name_plural = 'kandydaci'
        ordering = ['nazwisko', 'imie']
    def clean(self):
        if len(Kandydat.objects.all()) == 3 or \
                (len(Kandydat.objects.all()) == 2 and not self in Kandydat.objects.all()):
            raise ValidationError({'imie' : 'Za dużo kandydatów.', 'imie' : 'Za dużo kandydatów.'})
    def __str__(self):
        return self.imie + u' ' + self.nazwisko

class Rapor(models.Model):
    def __nazwa_kandydata(nr):
        if nr > len(Kandydat.objects.all()) :
            if nr == 1 : return 'kandydata pierwszego';
            else : return 'kandydata drugiego';
        return str(list(Kandydat.objects.all())[nr - 1])
    gmina = models.OneToOneField(Gmina, primary_key=True)
    liczba_mieszkańców = models.IntegerField()
    liczba_uprawnionych = models.IntegerField()
    liczba_wydanych_kart = models.IntegerField()
    liczba_głosów_oddanych = models.IntegerField()
    liczba_głosów_na_pierwszego_kandydata = models.IntegerField(verbose_name= 'Liczba głosów na ' + __nazwa_kandydata(1))
    liczba_głosów_na_drugiego_kandydata = models.IntegerField(verbose_name= 'Liczba głosów na ' + __nazwa_kandydata(2))
    class Meta:
        verbose_name_plural = 'raporty (wyniki głosowań z gmin)'
    def clean(self):
        if len(Kandydat.objects.all()) == 1 :
            raise ValidationError({'liczba_głosów_na_drugiego_kandydata': 'Jest tylko jeden kandydat!.'
                                        ' Nie można wprowadzać tych danych przed ustaleniem kandydatów.'})
        if len(Kandydat.objects.all()) == 0 :
            raise ValidationError({'liczba_głosów_na_pierwszego_kandydata': 'Nie ma  kandydatów!.'
                                        'Nie można wprowadzać tych danych przed ustaleniem kandydatów.'})
        if self.liczba_głosów_na_drugiego_kandydata < 0:
            raise ValidationError({'liczba_głosów_na_drugiego_kandydata': 'Ujemna liczba głosów!'})
        if self.liczba_głosów_na_pierwszego_kandydata < 0:
            raise ValidationError({'liczba_głosów_na_pierwszego_kandydata': 'Ujemna liczba głosów!'})
        if self.liczba_głosów_na_drugiego_kandydata + self.liczba_głosów_na_pierwszego_kandydata > self.liczba_głosów_oddanych :
            raise ValidationError({'liczba_głosów_oddanych': 'Suma głosów oddanych na kandydatów większa niż ilość głosów oddanych.'})
        if self.liczba_wydanych_kart < self.liczba_głosów_oddanych:
            raise ValidationError({'liczba_wydanych_kart': 'Mniej wydanych kart niż oddanych głosów.'})
        if self.liczba_uprawnionych < self.liczba_wydanych_kart:
            raise ValidationError({'liczba_wydanych_kart': 'Wydano więcej kart niż uprawnionych.'})
        if self.liczba_mieszkańców < self.liczba_uprawnionych:
            raise ValidationError({'liczba_uprawnionych': 'Więcej upranionych niż mieszkańców.'})
    def __str__(self):
        return u'Raport z gminy: ' + str(self.gmina);
