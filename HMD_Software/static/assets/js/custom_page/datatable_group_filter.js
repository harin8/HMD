$(document).ready( function () {
    $.ajax({
        url: '/group_filter_list',
        method: "GET",
        success: function(data) {
            var groupSelect = $('#groupSelect');
            groupSelect.empty();
            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    groupSelect.append('<option value="' + data[key] + '">' + data[key] + '</option>');
                }
            }
            groupSelect.selectpicker('refresh');
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });
});