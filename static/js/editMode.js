$(document).ready(function () {
    // Track the current state of edit mode
    let editMode = false;

    // Enable edit mode by showing editable fields and adjusting button text
    function enableEditMode() {
        editMode = true;
        $('.note-display').hide();
        $('.note-edit').show();
        $('#editNotesButton').text('Cancel Editing');
        $('#saveAllChangesButton').show(); // Show the Save button
    }

    // Disable edit mode by hiding editable fields and resetting button text
    function disableEditMode() {
        editMode = false;
        $('.note-display').show();
        $('.note-edit').hide();
        $('#editNotesButton').text('Edit Notes');
        $('#saveAllChangesButton').hide(); // Hide the Save button
    }

    // Toggle edit mode on button click
    $('#editNotesButton').on('click', function () {
        if (!editMode) {
            $.get('/pogo/is_authenticated', function (response) {
                if (response.authenticated) {
                    enableEditMode();
                } else {
                    const currentUrl = window.location.pathname + window.location.search;
                    window.location.href = '/pogo/login?next=' + encodeURIComponent(currentUrl) + '&edit=true';
                }
            }).fail(function () {
                alert('Failed to check authentication status.');
            });
        } else {
            disableEditMode();
        }
    });

    // Auto-enable edit mode if redirected with ?edit=true
    if (window.location.search.includes('edit=true')) {
        enableEditMode();
    }

    // Collect all notes and checkboxes data for saving
    function collectChanges() {
        const notesData = [];
        const checkboxesData = [];

        // Collect notes
        $('.note-edit').each(function () {
            const pokemonId = $(this).closest('tr').find('.hidden-pokemon-id').data('pokemon-id');
            const noteText = $(this).val();

            if (pokemonId !== undefined && noteText !== undefined) {
                notesData.push({ pokemon_id: pokemonId, note: noteText });
            }
        });

        // Collect checkboxes (Matt and iPad)
        $('.matt-have-checkbox, .ipad-lucky-checkbox').each(function () {
            const pokemonId = $(this).data('pokemon-id');
            const checkboxType = $(this).hasClass('matt-have-checkbox') ? 'matt_have' : 'ipad_lucky';
            const checkedValue = $(this).is(':checked') ? 'Yes' : 'No';

            if (pokemonId !== undefined) {
                checkboxesData.push({
                    pokemon_id: pokemonId,
                    type: checkboxType,
                    value: checkedValue
                });
            }
        });

        return { notes: notesData, checkboxes: checkboxesData };
    }

    // Save all changes (both notes and checkboxes)
    $('#saveAllChangesButton').on('click', function () {
        const changes = collectChanges();

        $.ajax({
            url: '/pogo/save-all-changes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(changes),
            success: function () {
                alert('Changes saved successfully!');

                // Update the note displays and disable edit mode without reloading
                $('.note-edit').each(function () {
                    const noteText = $(this).val();
                    $(this).hide();
                    $(this).siblings('.note-display').text(noteText).show();
                });

                disableEditMode();
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });

    // Select All and Deselect All buttons for checkboxes
    $('#selectAllButton').on('click', function () {
        $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', true);
    });

    $('#deselectAllButton').on('click', function () {
        $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', false);
    });
});