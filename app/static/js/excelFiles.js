function excelFiles(selectedFiles, compare) {
    var data = {
        "selectedFiles": selectedFiles,
        "compare": compare
    };
    // send data to server with ajax post
    $.ajax({
        type:'POST',
        url:'/excel',
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(data){
            if (data.success) {
                if (data.output == "local") {
                    alert("Se ha generado el archivo " + data.file);
                } else {
                    window.open('/download/' + data.file, "_blank");
                }
            } else {
                alert(data.file);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            var mensaje = JSON.parse(xhr.responseText || '{\"mensaje\": \"Error indeterminado\"}');
            alert(mensaje.mensaje);
        }
    });
}