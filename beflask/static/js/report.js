$(document).ready(function () {
    // Check if row is selected
    $('#report-table tbody').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            $('#report-table tbody tr.selected').removeClass("selected")
            $(this).addClass('selected');
        }
    });
    $(document).ajaxStart(function(){ 
        $("body").addClass('ajaxLoading');
    });
    $(document).ajaxStop(function(){ 
        $("body").removeClass('ajaxLoading');
    });
});
function remove_plus(a, b) {
  var aa = a.split('±')[0]
  var bb = b.split('±')[0]
  return aa - bb
}
function remove_dot(a, b) {
    var aa = a.replace(',', '').replace('.', '')
    var bb = b.replace(',', '').replace('.', '')
    return aa - bb
}