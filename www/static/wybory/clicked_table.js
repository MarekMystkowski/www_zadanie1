/**
 * Created by Marek on 2016-05-09.
 */
var myWindow = null;

function openTable(category, value) {
    myWindow = window.open("", "Gminy", "width=800px,height=600px");
     $.ajax({
        url : "/load_gmin", // the endpoint
        type : "GET", // http method
        data : {kategoria : category, wartos : value}, // data sent with the post request
        success : function(json) {
             myWindow.document.write(json);
        },
    });
}

function saveRow(id_gmin) {
    var mieszkancow =  parseInt($('#miesz_' + id_gmin).val());
    var uprawnionych =  parseInt($('#upraw_' + id_gmin).val());
    var wydanych =   parseInt($('#wydan_' + id_gmin).val());
    var odanych =   parseInt($('#oddan_' + id_gmin).val());
    var na_pierwszego =   parseInt($('#naPi_' + id_gmin).val());
    var na_drugiego =   parseInt($('#naDr_' + id_gmin).val());
    var date =  $('#date_' + id_gmin).val();

  /* Napisać walidacje !*/
    var blad_walidacji = "";
    if (na_pierwszego < 0) {
        blad_walidacji = 'Ujemna liczba glosow!';
    } else if (na_drugiego < 0) {
        blad_walidacji =  'Ujemna liczba glosow!'
    } else if (na_pierwszego + na_drugiego > odanych) {
        blad_walidacji = 'Suma glosow oddanych na kandydatow wieksza niz ilosc glosow oddanych.';
    } else if (odanych < wydanych) {
        blad_walidacji = 'Mniej wydanych kart niz oddanych glosow.';
    } else if (wydanych > uprawnionych) {
        blad_walidacji = 'Wydano wiecej kart niz uprawnionych.';
    } else if (mieszkancow < uprawnionych) {
        blad_walidacji = 'Wiecej upranionych niz mieszkancow.';
    }

    if (blad_walidacji != "") {
        $('#error_' + id_gmin).html(blad_walidacji);
        console.log('walidator error');
        return;
    }
      $('#error_' + id_gmin).html('');


    $.ajax({
        url : "/save_data", // the endpoint
        type : "GET", // http method
        data : {id : id_gmin, na_pierwszego : na_pierwszego, na_drugiego : na_drugiego, date : date, odanych : odanych, wydanych:wydanych, uprawnionych: uprawnionych, mieszkancow:mieszkancow},
        success : function(json) {
            var dane = JSON.parse(json);
             $('#date_' + id_gmin).get(0).value = dane.date;
            if(dane.sukces)
            {
                $('#naPP_' + id_gmin).first().text(dane.naPP + "%");
                $('#naPa_' + id_gmin).width(dane.naPP + "%") ;
                $('#naDP_' + id_gmin).first().text(dane.naDP  + "%");
            } else {

                var OknoKomunikatu = window.open("", "Komunikat", "width=200px,height=200px");
                OknoKomunikatu.document.write("Dane zmieniły się na :" +
                    "<button onclick='window.opener.postMessage(false, '*')'>Tak</button> " +
                    "<button onclick='window.opener.postMessage(true, '*')'>Nie</button>");

                window.onmessage = function (e) {
                    if (! e.data) {
                        saveRow(id_gmin);
                    } else {
                        $('#miesz_' + id_gmin).val(dane.miesz);
                        $('#upraw_' + id_gmin).val(dane.upraw);
                        $('#wydan_' + id_gmin).val(dane.wydan);
                        $('#oddan_' + id_gmin).val(dane.oddan);
                        $('#naPi_' + id_gmin).val(dane.naPi);
                        $('#naDr_' + id_gmin).val(dane.naDr);
                        $('#naPP_' + id_gmin).first().text(dane.naPP + "%");
                        $('#naPa_' + id_gmin).width(dane.naPP + "%");
                        $('#naDP_' + id_gmin).first().text(dane.naDP + "%");
                    }
                }

            }

        },
    });
    
}
