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
            document.getElementById("score").innerHTML = obj.score
            document.getElementById("event").innerHTML = obj.event
            document.getElementById("line_detection").src = "static/jpg/line_detection.jpg" + "?" + new Date().getTime();
            
            repeated_ajax_check();
        },
        error: function(error){
            console.log(error);
        }
    });

}