// Take picture in background over javascript to ajax to python and reload image
$(function() {
    $('a#get_score').on('click', function(e) {
        e.preventDefault()
        console.log('Score is being calculated');

        $.ajax({
            url: '/get_score',
            type: 'GET',
            success: function(response){
                var obj = JSON.parse(response)
                console.log(obj.score);
                document.getElementById("score").innerHTML = obj.score
                document.getElementById("rec_dart").src = "static/jpg/rec_dart.jpg" + "?" + new Date().getTime()
                document.getElementById("contours").src = "static/jpg/contours.jpg" + "?" + new Date().getTime()
                document.getElementById("features").src = "static/jpg/features.jpg" + "?" + new Date().getTime()
            },
            error: function(error){
                console.log(error);
            }
        });
        return false;
    });
});

