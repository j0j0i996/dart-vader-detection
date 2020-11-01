// Take picture in background over javascript to ajax to python and reload image
$(function() {
    $('a#take_pic').on('click', function(e) {
        e.preventDefault()
        console.log('TakePicture is running');

        $.ajax({
            url: '/take_picture',
            type: 'GET',
            success: function(response){
                var obj = JSON.parse(response)
                console.log(obj.path);
                document.getElementById("img_elmnt").src = "static/" + obj.path
            },
            error: function(error){
                console.log(error);
            }
        });
        return false;
    });
});

