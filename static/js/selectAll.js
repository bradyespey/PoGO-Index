// Select all checkboxes for Matt and iPad columns
$('#selectAllButton').on('click', function () {
    $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', true);
});

// Deselect all checkboxes for Matt and iPad columns
$('#deselectAllButton').on('click', function () {
    $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', false);
});