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
    var na_pierwszego = $('#naPi_' + id_gmin).get(0).value;
    var na_drugiego = $('#naDr_' + id_gmin).get(0).value;
    var date =  $('#date_' + id_gmin).get(0).value;

    $.ajax({
        url : "/save_data", // the endpoint
        type : "GET", // http method
        data : {id : id_gmin, na_pierwszego : na_pierwszego, na_drugiego : na_drugiego, date : date},
        success : function(json) {
            var dane = JSON.parse(json);
             $('#date_' + id_gmin).get(0).value = dane.date;
            if(dane.sukces)
            {
                console.log($('#naPa_' + id_gmin).width());
                $('#wazn_' + id_gmin).first().text(dane.wazn);
                $('#naPP_' + id_gmin).first().text(dane.naPP + "%");
                $('#naPa_' + id_gmin).width(dane.naPP + "%") ;
                $('#naDP_' + id_gmin).first().text(dane.naDP  + "%");
            } else {

            }

        },
    });
    
}
