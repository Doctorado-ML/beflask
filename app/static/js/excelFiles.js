function excel_select() {
    var checkbox = document.getElementsByName("selected_files");
    var selectedFiles = [];
    for (var i = 0; i < checkbox.length; i++) {
      if (checkbox[i].checked) {
        selectedFiles.push(checkbox[i].value);
      }
    }
    if (selectedFiles.length == 0) {
      alert("Select at least one file");
      return;
    }
    excelSend(selectedFiles);
}
function excelSend(selectedFiles) {
    var data = {
        "selectedFiles": selectedFiles,
    };
    // send data to server with ajax post
    $.ajax({
        type:'POST',
        url:'/results/excel',
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(data){
            if (data.success) {
                window.open('/results/download/' + data.file, "_blank");
            } else {
                alert(data.file);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(XMLHttpRequest.responseText);
          }
    });
}