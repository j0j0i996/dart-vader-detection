// Take picture in background over javascript to ajax to python and reload image
$(function() {
    $('a#before').on('click', function(e) {
        e.preventDefault()
        console.log('Camera is taking picture');

        $.ajax({
            url: '/take_picture/before',
            type: 'GET',
            success: function(response){
                var obj = JSON.parse(response)
                console.log(obj.path);
                document.getElementById("img_bf_elmnt").src = obj.path + "?" + new Date().getTime()
            },
            error: function(error){
                console.log(error);
            }
        });
        return false;
    });

    $('a#after').on('click', function(e) {
        e.preventDefault()
        console.log('Camera is taking picture');

        $.ajax({
            url: '/take_picture/after',
            type: 'GET',
            success: function(response){
                var obj = JSON.parse(response)
                console.log(obj.path);
                document.getElementById("img_af_elmnt").src = obj.path + "?" + new Date().getTime()
            },
            error: function(error){
                console.log(error);
            }
        });
        return false;
    });
});

