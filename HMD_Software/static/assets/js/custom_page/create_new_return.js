function get_all_data() {
        var data_dict = {};
        data_dict['it_no'] = document.getElementById('it_no');
        data_dict['c_name'] = document.getElementById('c_name');
        data_dict['accepted_by'] = document.getElementById('accepted_by');
        data_dict['accepted_date'] = document.getElementById('accepted_date');
        data_dict['ay'] = document.getElementById('ay');
        data_dict['type'] = document.getElementById('r_type');
        data_dict['remarks'] = document.getElementById('remarks');
        return data_dict;
    };

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$("#save_button").click(function(e){
    e.preventDefault();
    it_no = $("#it_no").val();
    c_name = $("#c_name").val();
    accepted_by = $("#accepted_by").val();
    accepted_date = $("#accepted_date").val();
    ay = $("#ay").val();
    r_type = $("#r_type").val();
    remarks = $("#remarks").val();
    $.ajax({
        type: "POST",
        url: "{% url 'Submit New Return' %}",
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        data: {
            it_no: it_no,
            name: c_name,
            acceptedBy: accepted_by,
            acceptedDate: accepted_date,
            AY: ay,
            type: r_type,
            remarks: remarks,
            save_ini: false
        },
        success: function(result){
            alert("Details Saved");
            location.href = window.location.origin + '/new_it_return?A.Y=' + ay + '&Type=' + r_type;
        }
    });
});
