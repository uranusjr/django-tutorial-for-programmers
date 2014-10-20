(function ($) {

$('.menu-item-add').click(function (e) {
  e.preventDefault();

  var lastElement = $('.menu-item:last');
  var totalForms = $('#id_menu_items-TOTAL_FORMS');
  var total = totalForms.val();

  var newElement = lastElement.clone(true);
  newElement.find(':input').each(function() {
    var name = $(this).attr('name').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    );
    var id = 'id_' + name;
    $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
  });
  newElement.find('label').each(function() {
    $(this).attr('for', $(this).attr('for').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    ));
  });

  totalForms.val(total + 1);
  newElement.insertAfter(lastElement);
});

})(jQuery);
