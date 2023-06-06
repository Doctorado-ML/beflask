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