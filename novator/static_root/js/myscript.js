
$(function() {
    function loadTeamData(teamId) {
        var hasBalanceField = $('#myText').length > 0;
        var hasCreditsField = $('#credits_team').length > 0;

        if (!teamId) {
            if (hasBalanceField) {
                $('#myText').val('');
            }
            if (hasCreditsField) {
                $('#credits_team').val('');
            }
            return;
        }

        if (hasBalanceField) {
            $.get('/bank/get-balance/' + teamId + '/', function(data) {
                $('#myText').val(data.text);
            }).fail(function() {
                $('#myText').val('Ошибка');
            });
        }

        if (hasCreditsField) {
            $.get('/bank/credit/check-credit/' + teamId + '/', function(data) {
                $('#credits_team').val(data.text);
            }).fail(function() {
                $('#credits_team').val('Ошибка');
            });
        }
    }

    function bindBalanceLookup() {
        var $teamSelect = $('#team-select, #team_select');

        if ($teamSelect.length) {
            $(document).on('change', '#team-select, #team_select', function() {
                loadTeamData($(this).val());
            });
            $teamSelect.trigger('change');
            return;
        }

        var teamId = $('#team_id').val() || $('input[name="team"]').val();
        if (teamId) {
            loadTeamData(teamId);
        }
    }

    bindBalanceLookup();
});

function updateTotalPrice() {
    var $form = $('form.needs-validation').first();
    if (!$form.length || !$('#total-price').length) {
        return;
    }

    $.ajax({
        url: '/bank/compute-total-price/',
        method: 'POST',
        data: $form.serialize(),
        cache: false,
        success: function(data) {
            var $totalPrice = $('#total-price');
            var total = data.total_price;
            var balanceText = $('#myText').val() || '';
            var balanceValue = parseFloat(String(balanceText).replace(/[^0-9.-]/g, ''));

            if (total === null || total === undefined || total === '') {
                $totalPrice.val('');
                $totalPrice.removeClass('text-danger border-danger');
                return;
            }

            var totalValue = parseFloat(total);
            $totalPrice.val(totalValue.toFixed(2));

            if (!isNaN(balanceValue) && !isNaN(totalValue) && totalValue > balanceValue) {
                $totalPrice.addClass('text-danger border-danger');
            } else {
                $totalPrice.removeClass('text-danger border-danger');
            }
        },
        error: function() {
            var $totalPrice = $('#total-price');
            $totalPrice.val('Ошибка загрузки');
            $totalPrice.removeClass('text-danger border-danger');
        }
    });
}

$(function() {
    var $orderForm = $('form.needs-validation').first();
    if ($orderForm.length) {
        $orderForm.on('input change', 'input, select', function() {
            updateTotalPrice();
        });
        updateTotalPrice();
    }
});

