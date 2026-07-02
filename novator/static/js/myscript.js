
$(function() {
    if ($('#team-select').length) {
        $('#team-select').on('change', function() {
            var id = $(this).val();
            if (id) {
                $.get('/bank/get-balance/' + id + '/', function(data) {
                    $('#myText').val(data.text);
                }).fail(function() {
                    $('#myText').val('Ошибка');
                });
            } else {
                $('#myText').val('');
            }
        }).trigger('change');
    }

    if ($('#id_auto').length) {
        $('#id_auto').on('input change', function() {
            var quantity = $(this).val();

            if (quantity) {
                $.get('/bank/check-total-price/52/' + quantity + '/', function(data) {
                    $('#total-price').val(data.total_price);
                }).fail(function() {
                    $('#total-price').val('Ошибка загрузки');
                });
            } else {
                $('#total-price').val('');
            }
        })
    }
});
