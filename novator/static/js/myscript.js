$(function() {
    // Safe balance loader
    function loadBalance(teamId) {
        if (!teamId) {
            $('#myText').val('');
            return;
        }
        $.get('/bank/get-balance/' + teamId + '/', function(data) {
            $('#myText').val(data && data.text ? data.text : '0');
        }).fail(function() {
            $('#myText').val('Ошибка загрузки');
        });
    }

    $('#team-select').on('change', function() {
        loadBalance($(this).val());
    }).trigger('change');

    // Sum item prices (rows should have class `item-row`, price cell/input `.item-price`, qty input `.item-qty`)
    function sumPrices() {
        var total = 0;
        $('.item-row').each(function() {
            var $row = $(this);
            var priceText = $row.find('.item-price').first().text();
            if (!priceText) priceText = $row.find('.item-price').first().val();
            var qtyText = $row.find('.item-qty').first().val();
            if (!qtyText) qtyText = $row.find('.item-qty').first().text();

            var price = parseFloat(String(priceText).replace(/[^0-9.,-]/g, '').replace(',', '.')) || 0;
            var qty = parseFloat(String(qtyText).replace(/[^0-9.,-]/g, '').replace(',', '.')) || 1;
            total += price * qty;
        });

        var formatted = total.toFixed(2);
        if ($('#totalPrice').length) {
            $('#totalPrice').text(formatted);
        } else if ($('#myText').length) {
            // fallback: put total into the balance input if no dedicated total element
            $('#myText').val(formatted);
        }
    }

    // Recalculate on changes to price/qty inputs or on page load
    $(document).on('input change', '.item-price, .item-qty', sumPrices);
    sumPrices();
});
