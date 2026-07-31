
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
});
/* 
$(function updateTotalPrice() {
        var $form = $('form.needs-validation').first();
        if (!$form.length) {
            return;
        }

        $.ajax({
            url: '/bank/compute-total-price/',
            method: 'GET',
            data: $form.serialize(),
            cache: false,
            success: function(data) {
                var total = data.total_price;
                if (total === null || total === undefined || total === '') {
                    $('#total-price').val('');
                } else {
                    $('#total-price').val(parseFloat(total).toFixed(2));
                }
            },
            error: function() {
                $('#total-price').val('Ошибка загрузки');
            }
        });
    });

var $orderForm = $('form.needs-validation').first();
if ($orderForm.length) {
    $orderForm.on('input change', 'input, select', function() {
        updateTotalPrice();
    });
    updateTotalPrice();
} */

