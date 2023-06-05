$(document).ready(function () {
    var table = $("#file-table").DataTable({
      paging: true,
      searching: true,
      ordering: true,
      info: true,
      "select.items": "row",
      pageLength: 25,
      columnDefs: [
        {
          targets: 8,
          orderable: false,
        },
      ],
      //"language": {
      //    "lengthMenu": "_MENU_"
      //}
    });
    $('#file-table').on( 'draw.dt', function () {
      enable_disable_best_buttons();
    } );
    // Check if row is selected
    $("#file-table tbody").on("click", "tr", function () {
      if ($(this).hasClass("selected")) {
        $(this).removeClass("selected");
      } else {
        table
          .$("tr.selected")
          .removeClass("selected");
        $(this).addClass("selected");
      }
    });
    // Show file with doubleclick
    $("#file-table tbody").on("dblclick", "tr", function () {
      showFile($(this).attr("id"));
    });
    $(document).ajaxStart(function () {
      $("body").addClass("ajaxLoading");
    });
    $(document).ajaxStop(function () {
      $("body").removeClass("ajaxLoading");
    });
  $('#compare').change(function () {
      $.ajax({
        type:'POST',
        url:'/results/set_compare',
        data: JSON.stringify({"compare": $("#compare").is(":checked")}),
        contentType: "application/json",
        dataType: 'json',
        success: function(data){
          if (data.success) {
            enable_disable_best_buttons();
          } else {
            alert(data.file);
          }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          alert(XMLHttpRequest.responseText);
        }
      });
    });
    enable_disable_best_buttons();
  });
  function enable_disable_best_buttons(){
    if ($('#compare').is(':checked')) {
      $("[name='best_buttons']").addClass("tag is-link is-normal");
      $("[name='best_buttons']").removeAttr("hidden");
      } else {
        $("[name='best_buttons']").removeClass("tag is-link is-normal");
        $("[name='best_buttons']").attr("hidden", true);
      }
  }
  function showFile(selectedFile) {
    location.href = "/results/show/" + selectedFile;
  }
  function excel() {
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
    var compare = $("#compare").is(":checked");
    excelFiles(selectedFiles, compare);
  }
  function setCheckBoxes(value) {
    var checkbox = document.getElementsByName("selected_files");
    for (i = 0; i < checkbox.length; i++) {
      checkbox[i].checked = value;
    }
  }
  function redirectDouble(route, parameter) {
    location.href = "/"+ route + "/" + parameter + "/" + $("#compare").is(":checked");
  }
  function redirectSimple(route) {
    location.href = "/" + route + "/" + $("#compare").is(":checked");
  }