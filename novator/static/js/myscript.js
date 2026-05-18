$(function() {
    $('#team-select').on('change', function() {
        var id = $(this).val();
        if (id) {
            $.get('/bank/get-balance/' + selectedId + '/', function(data) {
                $('#myText').val(data.text);
            }).fail(function() {
                $('#myText').val('Ошибка');
            });
        } else {
            $('#myText').val('');
        }
    }).trigger('change'); // эмулируем событие change для начальной загрузки
});


$('#team-select').change(function() {
    var selectedId = $(this).val();
    if (selectedId) {
        $.get('/bank/get-balance/' + selectedId + '/', function(data) {
            $('#myText').val(data.text);
        }).fail(function() {
            $('#myText').val('Ошибка загрузки');
        });
    } else {
        $('#myText').val('');
            }
});


