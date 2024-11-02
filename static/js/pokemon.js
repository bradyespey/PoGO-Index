$(document).ready(function () {
    let hasChanges = false; // Track if changes were made

    // === INITIALIZE EDIT MODE (ALWAYS ON FOR LOGGED-IN USERS) ===
    function initializeEditMode() {
        $('.note-display').hide();
        $('.note-edit').show();
        $('#saveAllChangesButton').show();
    }

    initializeEditMode(); // Always in edit mode if logged in

    // Centralized function to mark changes
    function markChanged() {
        hasChanges = true;
        console.log("Change detected, hasChanges set to:", hasChanges); // Debug log
    }

    // Attach change event listeners to all checkboxes and note inputs
    $(document).on('change', '.matt-have-checkbox, .matt-lucky-checkbox, .ipad-lucky-checkbox', function() {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed
        console.log(`Checkbox changed:`, this); // Debug log
    });

    $(document).on('input', '.note-edit', function() {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed
        console.log("Note input changed:", this); // Debug log
    });

    // Track changes on "Select All" checkboxes
    $('#selectAllMatt, #selectAllMattLucky, #selectAlliPadLucky').on('change', function() {
        const isChecked = $(this).is(':checked');
        const columnIndex = $(this).attr('id') === 'selectAllMatt' ? 6
                        : $(this).attr('id') === 'selectAllMattLucky' ? 7
                        : 9;  // Adjust based on actual column indexes

        updateColumnCheckboxes(columnIndex, isChecked);
    });

    // Update all checkboxes in a column when "Select All" is toggled
    function updateColumnCheckboxes(columnIndex, isChecked) {
        const table = window.pokemonTable;

        table.rows({ page: 'current' }).every(function () {
            const $checkboxCell = $(this.node()).find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find('input[type="checkbox"]');

            if ($checkbox.length) {
                $checkbox.prop('checked', isChecked);
                $checkbox.attr('data-changed', 'true'); // Mark as changed
                markChanged(); // Track change for "Select All"
                console.log("Select All toggled, checkbox updated:", $checkbox); // Debug log
            }
        });
    }

    // Collect changes from notes and checkboxes to send to the backend
    function collectChanges() {
        const notesData = [];
        const checkboxesData = [];

        // Collect changes from note edits
        $('.note-edit[data-changed="true"]').each(function () {
            const pokemonId = $(this).closest('tr').find('.hidden-pokemon-id').data('pokemon-id');
            const noteText = $(this).val();
            if (pokemonId !== undefined && noteText !== undefined) {
                notesData.push({ pokemon_id: pokemonId, note: noteText });
            }
        });

        // Collect checkbox changes marked with data-changed="true"
        $('.matt-have-checkbox[data-changed="true"], .matt-lucky-checkbox[data-changed="true"], .ipad-lucky-checkbox[data-changed="true"]').each(function () {
            const pokemonId = $(this).data('pokemon-id');
            let checkboxType;
            if ($(this).hasClass('matt-have-checkbox')) checkboxType = 'matt_have';
            else if ($(this).hasClass('matt-lucky-checkbox')) checkboxType = 'matt_lucky';
            else if ($(this).hasClass('ipad-lucky-checkbox')) checkboxType = 'ipad_lucky';

            const checkedValue = $(this).is(':checked') ? 'Yes' : 'No';
            if (pokemonId !== undefined && checkboxType !== undefined) {
                checkboxesData.push({
                    pokemon_id: pokemonId,
                    type: checkboxType,
                    value: checkedValue
                });
            }
        });

        return { notes: notesData, checkboxes: checkboxesData };
    }

    // Save changes when "Save Changes" button is clicked
    $('#saveAllChangesButton').on('click', function () {
        if (!hasChanges) {
            alert("No changes to save!");
            return;
        }

        const changes = collectChanges();
        console.log("Changes being sent to backend:", changes);

        $.ajax({
            url: '/pogo/save-all-changes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(changes),
            success: function () {
                alert('Changes saved successfully!');
                hasChanges = false; // Reset change tracker

                // Reset `data-changed` attribute on all checkboxes and note edits after save
                $('.matt-have-checkbox, .matt-lucky-checkbox, .ipad-lucky-checkbox, .note-edit').removeAttr('data-changed');
                console.log("Changes saved, hasChanges reset to:", hasChanges); // Debug log
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });

    // === DATA TABLE INITIALIZATION AND FILTERING ===

    function applyFilter(dataTable, filter, value) {
        if (filter.type === 'select') {
            if (value) {
                dataTable.column(filter.columnIndex)
                         .search('^' + $.fn.dataTable.util.escapeRegex(value) + '$', true, false)
                         .draw();
            } else {
                dataTable.column(filter.columnIndex).search('', true, false).draw();
            }
        } else if (filter.type === 'numberExact') {
            dataTable.column(filter.columnIndex).search(value ? '^' + value + '$' : '', true, false).draw();
        } else {
            dataTable.column(filter.columnIndex).search(value).draw();
        }
    }

    function initializeFilters(clonedHeader, options, dataTable) {
        clonedHeader.find('th').each(function (i) {
            const column = options.columns[i];
            const title = column.title || '';
            const filterType = column.filterType;

            if (filterType === 'text') {
                $(this).html('<input type="text" placeholder="Search ' + title + '" />');
            } else if (filterType === 'numberExact') {
                $(this).html('<input type="number" placeholder="Search ' + title + '" />');
            } else if (filterType === 'select') {
                let selectHtml = '<select><option value="">All</option>';
                column.options.forEach(opt => {
                    selectHtml += `<option value="${opt}">${opt}</option>`;
                });
                selectHtml += '</select>';
                $(this).html(selectHtml);
            }

            $('input', this).on('keyup change clear', function () {
                const val = this.value;
                if (filterType === 'numberExact') {
                    dataTable.column(i).search(val ? '^' + val + '$' : '', true, false).draw();
                } else {
                    dataTable.column(i).search(val).draw();
                }
            });

            $('select', this).on('change', function () {
                const val = $(this).val();
                if (column.specialFilter) {
                    column.specialFilter(dataTable.column(i), val);
                } else {
                    if (val) {
                        dataTable.column(i).search('^' + $.fn.dataTable.util.escapeRegex(val) + '$', true, false).draw();
                    } else {
                        dataTable.column(i).search('', true, false).draw();
                    }
                }
            });
        });
    }

    function initializeDataTable(options) {
        const tableSelector = options.tableSelector;
        const table = $(tableSelector);
        if (table.length === 0) return null;

        table.find('thead tr.clone').remove();
        const originalHeader = table.find('thead tr').first();
        const clonedHeader = originalHeader.clone(true).addClass('clone').appendTo(table.find('thead'));

        const dataTable = table.DataTable({
            orderCellsTop: true,
            fixedHeader: true,
            paging: options.paging !== false,
            pageLength: options.pageLength || 10,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            stateSave: options.stateSave || false,
            searching: options.searching !== false,
            lengthChange: options.lengthChange !== false,
            columnDefs: options.columnDefs || [],
            stateSaveParams: (settings, data) => { data.search.search = ''; },
            initComplete: function () {
                const api = this.api();
                api.columns().visible(true);
                api.columns.adjust();
            }
        });

        initializeFilters(clonedHeader, options, dataTable);

        if (options.showEntriesSelector) {
            $(options.showEntriesSelector).on('change', function () {
                dataTable.page.len(this.value).draw();
            });
        }

        if (options.extraFilters) {
            options.extraFilters.forEach(filter => {
                $(filter.selector).on('keyup change clear', function () {
                    applyFilter(dataTable, filter, this.value);
                });
            });
        }

        return dataTable;
    }

    // === RESET FILTERS ===

    $('#resetFiltersButton').on('click', function () {
        if (window.pokemonTable) {
            // Clear all column filters and search fields
            window.pokemonTable.search('').columns().search('').draw();
    
            // Reset dropdown filters
            $('#searchName, #filterType, #filterLegendary, #filterMythical, #filterUltraBeast').val('');
            const clonedHeader = window.pokemonTable.table().header();
            $(clonedHeader).find('input, select').val('');
            
            // Reset entries to default value of 10
            $('#showEntries').val('10');
            window.pokemonTable.page.len(10).draw();
    
            // Reset sorting to first column in ascending order
            window.pokemonTable.order([0, 'asc']).draw();
        }
    });

    // === INITIALIZE ALL TABLES ===

    window.pokemonTable = initializeDataTable({
        tableSelector: '#pokemonTable',
        responsive: true,
        scrollX: true,
        autoWidth: false,
        paging: true,
        ordering: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        stateSave: false,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: '#', filterType: 'numberExact' },
            { title: 'Image', filterType: null },
            { title: 'Name', filterType: 'text' },
            { title: 'Type', filterType: 'select', options: ['Grass', 'Poison', 'Fire', 'Water', 'Electric', 'Ice', 'Fighting', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'] },
            { title: 'Brady', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Brady Lucky', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt Lucky', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'iPad', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'iPad Lucky', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Note', filterType: 'select', options: ['Has Notes', 'No Notes'], specialFilter: function (column, val) {
                if (val === 'Has Notes') {
                    column.search('^(?!\\s*$).+', true, false).draw();
                } else if (val === 'No Notes') {
                    column.search('^\\s*$', true, false).draw();
                } else {
                    column.search('').draw();
                }
            }},
            { title: 'Legendary', filterType: null },
            { title: 'Mythical', filterType: null },
            { title: 'Ultra Beast', filterType: null }
        ],
        columnDefs: [
            { targets: [6, 7, 9], orderable: false },
            { targets: [11, 12, 13], orderable: false, visible: false, searchable: true }
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 2, type: 'text' },
            { selector: '#filterType', columnIndex: 3, type: 'select' },
            { selector: '#filterLegendary', columnIndex: 11, type: 'select' },
            { selector: '#filterMythical', columnIndex: 12, type: 'select' },
            { selector: '#filterUltraBeast', columnIndex: 13, type: 'select' }
        ]
    });

    // === PREVENT SORTING ON HEADER CHECKBOXES ===

    // Prevent click events on header checkboxes from triggering sort
    $('#selectAllMatt, #selectAllMattLucky, #selectAlliPadLucky').on('click', function (e) {
        e.stopPropagation();
    });

    // === SELECT ALL CHECKBOXES FUNCTIONALITY ===

    // Function to update checkboxes in a column
    function updateColumnCheckboxes(columnIndex, isChecked) {
        var table = window.pokemonTable;

        table.rows({ page: 'current' }).every(function (rowIdx, tableLoop, rowLoop) {
            var data = this.data();
            var $row = $(this.node());

            var $checkboxCell = $row.find('td').eq(columnIndex);
            var $checkbox = $checkboxCell.find('input[type="checkbox"]');
            
            if ($checkbox.length) {
                $checkbox.prop('checked', isChecked);
                $checkboxCell.attr('data-filter', isChecked ? 'Yes' : 'No');
                hasChanges = true; // Track changes for "Select All"
            }
        });
    }

   // Event listeners for header checkboxes
    $('#selectAllMatt').on('change', function () {
        var isChecked = $(this).is(':checked');
        hasChanges = true; // Track changes when "Select All" is used
        updateColumnCheckboxes(6, isChecked);
    });

    $('#selectAllMattLucky').on('change', function () {
        var isChecked = $(this).is(':checked');
        hasChanges = true; // Track changes when "Select All" is used
        updateColumnCheckboxes(7, isChecked);
    });

    $('#selectAlliPadLucky').on('change', function () {
        var isChecked = $(this).is(':checked');
        hasChanges = true; // Track changes when "Select All" is used
        updateColumnCheckboxes(9, isChecked);
    });

    // Ensure that when a checkbox is manually changed, we update the header checkbox state
    function updateHeaderCheckboxState(columnIndex, headerCheckboxId) {
        var table = window.pokemonTable;

        var allChecked = true;
        var anyChecked = false;

        table.rows({ page: 'current' }).every(function (rowIdx, tableLoop, rowLoop) {
            var data = this.data();
            var $row = $(this.node());

            var $checkboxCell = $row.find('td').eq(columnIndex);
            var $checkbox = $checkboxCell.find('input[type="checkbox"]');
            if ($checkbox.length) {
                if (!$checkbox.is(':checked')) {
                    allChecked = false;
                } else {
                    anyChecked = true;
                }
            }
        });

        var $headerCheckbox = $('#' + headerCheckboxId);
        if (allChecked) {
            $headerCheckbox.prop('checked', true).prop('indeterminate', false);
        } else if (anyChecked) {
            $headerCheckbox.prop('checked', false).prop('indeterminate', true);
        } else {
            $headerCheckbox.prop('checked', false).prop('indeterminate', false);
        }
    }

    // Event listeners for individual checkboxes to update header checkbox state
    window.pokemonTable.on('draw', function () {
        updateHeaderCheckboxState(6, 'selectAllMatt');
        updateHeaderCheckboxState(7, 'selectAllMattLucky');
        updateHeaderCheckboxState(9, 'selectAlliPadLucky');

        $('input.matt-have-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(6, 'selectAllMatt');
        });

        $('input.matt-lucky-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(7, 'selectAllMattLucky');
        });

        $('input.ipad-lucky-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(9, 'selectAlliPadLucky');
        });
    });

    window.pokemonTable.draw();
});