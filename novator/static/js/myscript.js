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


document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('input.form-check-input[type="checkbox"]').forEach(function(cb) {
    function update() {
      var tr = cb.closest('tr');
      if (!tr) return;
      var countInput = tr.querySelector('input[name^="use_count_"]');
      var removeCountInput = tr.querySelector('input[name^="remove_count_"]');
      if (!countInput || !removeCountInput) return;
      if (cb.checked && cb.name.startsWith('use_')) {
        countInput.readOnly = false;
        countInput.classList.remove('opacity-50');
      }
        if (!cb.checked && cb.name.startsWith('use_')) {
        countInput.readOnly = true;
        countInput.value = '';
        countInput.classList.add('opacity-50');
      }
        if (cb.checked && cb.name.startsWith('remove_')) {
            removeCountInput.readOnly = false;
            removeCountInput.classList.remove('opacity-50');
        } 
        if (!cb.checked && cb.name.startsWith('remove_')) {
            removeCountInput.readOnly = true;
            removeCountInput.value = '';
            removeCountInput.classList.add('opacity-50');
        }
    }
    update();
    cb.addEventListener('change', update);
  });
});