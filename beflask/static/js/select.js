$(document).ready(function () {
    // Check if row is selected
    $('#file-table tbody').on('click', 'tr', function () {
      if ($(this).hasClass('selected')) {
          $(this).removeClass('selected');
      } else {
          $('#file-table tbody tr.selected').removeClass("selected")
          $(this).addClass('selected');
      }
    });
    // Show file with doubleclick
    $("#file-table tbody").on("dblclick", "tr", function () {
      location.href="/results/report/"+ $(this).attr("id");
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
  function setCheckBoxes(value) {
    var checkbox = document.getElementsByName("selected_files");
    for (i = 0; i < checkbox.length; i++) {
      checkbox[i].checked = value;
    }
  }