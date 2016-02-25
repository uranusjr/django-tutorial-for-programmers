(function ($) {

$('.menu-item-add').click(function (e) {
  e.preventDefault();

  var lastElement = $('.menu-item:last');
  var totalForms = $('#id_menu_items-TOTAL_FORMS');
  var total = parseInt(totalForms.val());

  var newElement = lastElement.clone(true);
  newElement.find(':input').each(function() {
    var name = $(this).attr('name').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    );
    $(this).attr({'name': name}).val('').removeAttr('checked');
  });
  newElement.find('label').each(function() {
    $(this).attr('for', $(this).attr('for').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    ));
  });
  newElement.find('*').each(function() {
    var id = $(this).attr('id');
    if (id) {
      $(this).attr('id', id.replace(
        '-' + (total - 1) + '-',
        '-' + total + '-'
      ));
    }
  });

  totalForms.val(total + 1);
  newElement.insertAfter(lastElement);
});

})(jQuery);
