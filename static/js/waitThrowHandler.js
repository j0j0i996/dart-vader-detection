// Take picture in background over javascript to ajax to python and reload image
$(function() {
    $('a#get_score').on('click', function(e) {
        e.preventDefault()
        console.log('Waiting for throw');
        
        repeated_ajax_check();

        return false;
    });
});

function repeated_ajax_check() {

    $.ajax({
        url: '/wait_throw',
        type: 'GET',
        success: function(response){
            var obj = JSON.parse(response)
            console.log(obj.score);
            document.getElementById("score").innerHTML = obj.score
            document.getElementById("rec_dart").src = "static/jpg/rec_dart.jpg" + "?" + new Date().getTime();
            document.getElementById("contours").src = "static/jpg/contours.jpg" + "?" + new Date().getTime();
            document.getElementById("features").src = "static/jpg/features.jpg" + "?" + new Date().getTime();
            document.getElementById("img_bf_elmnt").src = "static/jpg/before.jpg" + "?" + new Date().getTime();
            document.getElementById("img_af_elmnt").src = "static/jpg/after.jpg" + "?" + new Date().getTime();
            document.getElementById("line_filtered").src = "static/jpg/features_line_filtered.jpg" + "?" + new Date().getTime();
            
            repeated_ajax_check();
        },
        error: function(error){
            console.log(error);
        }
    });

}