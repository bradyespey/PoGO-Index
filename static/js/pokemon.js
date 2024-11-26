// static/js/pokemon.js

$(document).ready(function () {
    let hasChanges = false; // Track if changes were made
    let changes = {
        notes: {},
        checkboxes: {}
    };

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
    }

    // === EVENT LISTENERS FOR CHECKBOXES ===
    // Attach change event listeners to specific checkbox classes only
    const checkboxClasses = [
        '.matt-have-checkbox',
        '.matt-shiny-checkbox',
        '.matt-lucky-checkbox',
        '.ipad-shiny-checkbox',
        '.ipad-lucky-checkbox'
    ];

    function getCheckboxTypeByClass($checkbox) {
        if ($checkbox.hasClass('matt-have-checkbox')) return 'matt_have';
        if ($checkbox.hasClass('matt-shiny-checkbox')) return 'matt_shiny';
        if ($checkbox.hasClass('matt-lucky-checkbox')) return 'matt_lucky';
        if ($checkbox.hasClass('ipad-shiny-checkbox')) return 'ipad_shiny';
        if ($checkbox.hasClass('ipad-lucky-checkbox')) return 'ipad_lucky';
        return null;
    }

    checkboxClasses.forEach(function (className) {
        $(document).on('change', className, function () {
            const $checkbox = $(this);
            const pokemonId = $checkbox.data('pokemon-id');
            const checkboxType = getCheckboxTypeByClass($checkbox);

            const checkedValue = $checkbox.is(':checked') ? 'Yes' : 'No';

            // Store change in the changes object
            changes.checkboxes[pokemonId + '_' + checkboxType] = {
                pokemon_id: pokemonId,
                type: checkboxType,
                value: checkedValue
            };

            // Update data attributes for filtering and sorting
            $checkbox.closest('td')
                .attr('data-filter', checkedValue)
                .attr('data-order', checkedValue);

            // Update header checkbox state
            const columnIndex = $checkbox.closest('td').index();
            updateHeaderCheckboxState(columnIndex);

            // Mark that changes have been made
            markChanged();
        });
    });

    // Event listener for note edits
    $(document).on('input', '.note-edit', function () {
        const $note = $(this);
        const pokemonId = $note.data('pokemon-id');
        const noteText = $note.val();

        // Store change in the changes object
        changes.notes[pokemonId] = {
            pokemon_id: pokemonId,
            note: noteText
        };

        // Update data attributes for filtering and sorting
        $note.closest('td')
            .attr('data-filter', noteText ? 'Has Notes' : 'No Notes')
            .attr('data-order', noteText); // Assuming you want to sort by note text

        // Mark that changes have been made
        markChanged();

        // Removed the scroll issue by not redrawing the table here
        // window.pokemonTable.row($note.closest('tr')).invalidate().draw(false);
    });

    // === SELECT ALL CHECKBOX DEFINITIONS ===
    const selectAllCheckboxes = [
        { id: 'selectAllMattLivingDex', columnIndex: 7, className: 'matt-have-checkbox' },
        { id: 'selectAllMattShiny', columnIndex: 8, className: 'matt-shiny-checkbox' },
        { id: 'selectAllMattLucky', columnIndex: 9, className: 'matt-lucky-checkbox' },
        { id: 'selectAlliPadShiny', columnIndex: 11, className: 'ipad-shiny-checkbox' },
        { id: 'selectAlliPadLucky', columnIndex: 12, className: 'ipad-lucky-checkbox' }
    ];

    // Helper function to map column indices to the correct checkbox class
    function getCheckboxClassByColumnIndex(columnIndex) {
        switch (columnIndex) {
            case 7:
                return 'matt-have-checkbox'; // Matt 👤
            case 8:
                return 'matt-shiny-checkbox'; // Matt ✨
            case 9:
                return 'matt-lucky-checkbox'; // Matt 🎲
            case 11:
                return 'ipad-shiny-checkbox'; // iPad ✨
            case 12:
                return 'ipad-lucky-checkbox'; // iPad 🎲
            default:
                return ''; // Default to no class
        }
    }

    function getCheckboxTypeByClassName(checkboxClass) {
        switch (checkboxClass) {
            case 'matt-have-checkbox':
                return 'matt_have';
            case 'matt-shiny-checkbox':
                return 'matt_shiny';
            case 'matt-lucky-checkbox':
                return 'matt_lucky';
            case 'ipad-shiny-checkbox':
                return 'ipad_shiny';
            case 'ipad-lucky-checkbox':
                return 'ipad_lucky';
            default:
                return null;
        }
    }

    // === UPDATE COLUMN CHECKBOXES FUNCTION ===
    function updateColumnCheckboxes(columnIndex, isChecked) {
        const table = window.pokemonTable;
        const checkboxClass = getCheckboxClassByColumnIndex(columnIndex);
        const checkboxType = getCheckboxTypeByClassName(checkboxClass);

        // Iterate over all visible rows on the current page
        table.rows({ search: 'applied', page: 'current' }).every(function () {
            const $row = $(this.node());
            const $checkboxCell = $row.find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find(`input.${checkboxClass}`);

            if ($checkbox.length) {
                $checkbox.prop('checked', isChecked);

                const pokemonId = $checkbox.data('pokemon-id');
                const checkedValue = isChecked ? 'Yes' : 'No';

                // Store change in the changes object
                changes.checkboxes[pokemonId + '_' + checkboxType] = {
                    pokemon_id: pokemonId,
                    type: checkboxType,
                    value: checkedValue
                };

                // Update data attributes for filtering and sorting
                $checkboxCell
                    .attr('data-filter', checkedValue)
                    .attr('data-order', checkedValue);
            }
        });

        // Update the header checkbox state
        updateHeaderCheckboxState(columnIndex);

        // Mark that changes have been made
        markChanged();
    }

    // === UPDATE HEADER CHECKBOX STATE FUNCTION ===
    function updateHeaderCheckboxState(columnIndex) {
        const table = window.pokemonTable;
        const checkboxClass = getCheckboxClassByColumnIndex(columnIndex);
        let allChecked = true;
        let anyChecked = false;

        table.rows({ search: 'applied', page: 'current' }).every(function () {
            const $checkboxCell = $(this.node()).find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find(`input.${checkboxClass}`);

            if ($checkbox.length) {
                if ($checkbox.is(':checked')) {
                    anyChecked = true;
                } else {
                    allChecked = false;
                }
            }
        });

        // Get the header checkbox
        const headerCell = table.column(columnIndex).header();
        const $headerCheckbox = $(headerCell).find('input[type="checkbox"]');

        if ($headerCheckbox.length) {
            $headerCheckbox.prop('checked', allChecked);
            $headerCheckbox.prop('indeterminate', !allChecked && anyChecked);
        }
    }

    // === COLLECT CHANGES FUNCTION ===
    function collectChanges() {
        const notesData = Object.values(changes.notes);
        const checkboxesData = Object.values(changes.checkboxes);

        return { notes: notesData, checkboxes: checkboxesData };
    }

    // === SAVE CHANGES BUTTON EVENT ===
    $('#saveAllChangesButton').on('click', function () {
        if (!hasChanges) {
            alert("No changes to save!");
            return;
        }

        const collectedChanges = collectChanges();

        if (collectedChanges.checkboxes.length === 0 && collectedChanges.notes.length === 0) {
            alert("No changes to save!");
            return;
        }

        $.ajax({
            url: '/pogo/save-all-changes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(collectedChanges),
            success: function () {
                alert('Changes saved successfully!');
                hasChanges = false;

                // Clear changes object
                changes.notes = {};
                changes.checkboxes = {};

                // Invalidate and redraw affected rows to update DataTable's cache
                updateDataTableAfterChanges();
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });

    // Invalidate and redraw DataTable rows after changes are saved
    function updateDataTableAfterChanges() {
        // Invalidate all rows and redraw the table
        window.pokemonTable.rows().invalidate().draw(false);
    }

    // === RESET FILTERS BUTTON EVENT ===
    $('#resetFiltersButton').on('click', function () {
        if (window.pokemonTable) {
            // Clear all column filters and search fields
            window.pokemonTable.search('').columns().search('').draw();

            // Reset dropdown filters
            $('#filterCategory').val('');
            $('#filterGeneration').val('');
            $('#filterType').val('');
            $('#filterShiny').val('');
            $('#showEntries').val('10');

            // Reset all "Select All" checkboxes
            selectAllCheckboxes.forEach(function (selectAll) {
                const headerCell = window.pokemonTable.column(selectAll.columnIndex).header();
                const $headerCheckbox = $(headerCell).find('input[type="checkbox"]');
                $headerCheckbox.prop('checked', false).prop('indeterminate', false);
            });

            // Reset header filters
            const clonedHeader = window.pokemonTable.table().header();
            $(clonedHeader).find('input, select').val('');

            // Reset entries to default value of 10
            window.pokemonTable.page.len(10).draw();

            // Reset sorting to first column in ascending order
            window.pokemonTable.order([0, 'asc']).draw();

            // Clear any unsaved changes
            hasChanges = false;
            changes = {
                notes: {},
                checkboxes: {}
            };
        }
    });

    // === DATA TABLE INITIALIZATION AND FILTERING ===

    function initializeFilters(filterRow, options, dataTable) {
        filterRow.find('th').each(function (i) {
            const column = options.columns[i];
    
            if (!column) {
                return; // Skip if column definition is missing
            }
    
            const title = column.title || '';
            const filterType = column.filterType;
    
            // Skip if filterType is null
            if (!filterType) {
                $(this).html('');
                return;
            }
    
            // Create appropriate filter input based on filterType
            if (filterType === 'text') {
                $(this).html('<input type="text" placeholder="Search ' + title + '" class="form-control form-control-sm" />');
            } else if (filterType === 'numberExact') {
                $(this).html('<input type="number" placeholder="Search ' + title + '" class="form-control form-control-sm" />');
            } else if (filterType === 'select') {
                let selectHtml = '<select class="form-control form-control-sm"><option value="">All</option>';
                if (column.options && Array.isArray(column.options)) {
                    column.options.forEach(opt => {
                        selectHtml += `<option value="${opt}">${opt}</option>`;
                    });
                }
                selectHtml += '</select>';
                $(this).html(selectHtml);
            }
    
            // Attach event listeners for filtering
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
                    // Use custom filter logic if defined
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

        const filterRow = table.find('thead tr#filterRow');

        const dataTable = table.DataTable({
            orderCellsTop: true,
            fixedHeader: false, // Set to false to resolve misalignment
            paging: options.paging !== false,
            pageLength: options.pageLength || 10,
            lengthMenu: options.lengthMenu || [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            stateSave: options.stateSave || false,
            searching: options.searching !== false,
            lengthChange: options.lengthChange !== false,
            columnDefs: options.columnDefs || [],
            responsive: options.responsive !== false,
            scrollX: options.scrollX !== false,
            autoWidth: options.autoWidth || false,
            columns: options.columns || [],
            initComplete: function () {
                const api = this.api();
                window.pokemonTable = api; // Assign before using in other functions
                initializeFilters(filterRow, options, api);

                // Bind event listeners for "Select All" checkboxes
                const header = api.table().header();
                $(header).find('input.select-all-checkbox').on('change', function (e) {
                    e.stopPropagation();
                    const isChecked = $(this).is(':checked');
                    const columnIndex = $(this).closest('th').index();
                    updateColumnCheckboxes(columnIndex, isChecked);
                });

                // Update header checkbox state after initialization
                selectAllCheckboxes.forEach(function (selectAll) {
                    updateHeaderCheckboxState(selectAll.columnIndex);
                });
            }
        });

        if (options.showEntriesSelector) {
            $(options.showEntriesSelector).on('change', function () {
                options.pageLength = parseInt(this.value, 10);
                window.pokemonTable.page.len(options.pageLength).draw();
            });
        }

        return dataTable;
    }

    // === INITIALIZE DATA TABLE INSTANCE ===
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
            { title: '#', filterType: 'numberExact' }, // Column 0
            { title: '📷', filterType: null }, // Image column - Column 1
            { title: 'Name', filterType: 'text' }, // Column 2
            { title: 'Shiny ✨', filterType: 'select', options: ['Yes', 'No'] }, // Column 3
            { title: 'Brady 👤', filterType: 'select', options: ['Yes', 'No'] }, // Column 4
            { title: 'Brady ✨', filterType: 'select', options: ['Yes', 'No'] }, // Column 5
            { title: 'Brady 🎲', filterType: 'select', options: ['Yes', 'No'] }, // Column 6
            // Matt 👤 with checkbox in header
            {
                title: 'Matt 👤<br><input type="checkbox" class="select-all-checkbox">',
                filterType: 'select',
                options: ['Yes', 'No']
            }, // Column 7
            // Matt ✨ with checkbox in header
            {
                title: 'Matt ✨<br><input type="checkbox" class="select-all-checkbox">',
                filterType: 'select',
                options: ['Yes', 'No']
            }, // Column 8
            // Matt 🎲 with checkbox in header
            {
                title: 'Matt 🎲<br><input type="checkbox" class="select-all-checkbox">',
                filterType: 'select',
                options: ['Yes', 'No']
            }, // Column 9
            { title: 'iPad 👤', filterType: 'select', options: ['Yes', 'No'] }, // Column 10
            // iPad ✨ with checkbox in header
            {
                title: 'iPad ✨<br><input type="checkbox" class="select-all-checkbox">',
                filterType: 'select',
                options: ['Yes', 'No']
            }, // Column 11
            // iPad 🎲 with checkbox in header
            {
                title: 'iPad 🎲<br><input type="checkbox" class="select-all-checkbox">',
                filterType: 'select',
                options: ['Yes', 'No']
            }, // Column 12
            {
                title: 'Notes',
                filterType: 'select',
                options: ['Has Notes', 'No Notes'],
                specialFilter: function (column, val) {
                    if (val === 'Has Notes') {
                        column.search('^(?!\\s*$).+', true, false).draw();
                    } else if (val === 'No Notes') {
                        column.search('^\\s*$', true, false).draw();
                    } else {
                        column.search('').draw();
                    }
                }
            }, // Column 13
            { title: 'Category', filterType: null }, // Hidden Column 14
            { title: 'Generation', filterType: null }, // Hidden Column 15
            { title: 'Type', filterType: null } // Hidden Column 16
        ],
        columnDefs: [
            { targets: "_all", width: "100px" },
            { targets: [7, 8, 9, 11, 12], orderable: false }, // Checkbox columns
            { targets: [14, 15, 16], visible: false, searchable: true } // Hidden columns
        ]
    });

    // === CUSTOM FILTERING FOR HIDDEN COLUMNS ===
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        const categoryFilter = $('#filterCategory').val();
        const generationFilter = $('#filterGeneration').val();
        const typeFilter = $('#filterType').val();
        const shinyFilter = $('#filterShiny').val();

        const categoryValue = data[14]?.trim(); // Hidden Category column
        const generationValue = data[15]?.trim(); // Hidden Generation column
        const typeValue = data[16]?.trim(); // Hidden Type column
        const shinyValue = data[3]?.trim(); // Shiny Released column

        // Check Category filter
        if (categoryFilter && categoryFilter !== categoryValue) {
            return false;
        }

        // Check Generation filter
        if (generationFilter && generationFilter !== generationValue) {
            return false;
        }

        // Check Type filter
        if (typeFilter && !typeValue.includes(typeFilter)) {
            return false;
        }

        // Check Shiny Released filter
        if (shinyFilter && shinyFilter !== shinyValue) {
            return false;
        }

        return true;
    });

    // === EVENT LISTENERS FOR CUSTOM FILTERS ===
    $('#filterCategory').on('change', function () {
        window.pokemonTable.draw();
    });

    $('#filterGeneration').on('change', function () {
        window.pokemonTable.draw();
    });

    $('#filterType').on('change', function () {
        window.pokemonTable.draw();
    });

    $('#filterShiny').on('change', function () {
        window.pokemonTable.draw();
    });

    // === UPDATE HEADER CHECKBOX STATE ON TABLE DRAW ===
    if (window.pokemonTable) {
        window.pokemonTable.on('draw', function () {
            selectAllCheckboxes.forEach(function (selectAll) {
                updateHeaderCheckboxState(selectAll.columnIndex);
            });
        });
    }

    // === PREVENT SORTING ON HEADER CHECKBOXES ===
    // Prevent click events on header checkboxes from triggering sort
    if (window.pokemonTable) {
        const header = window.pokemonTable.table().header();
        $(header).find('input.select-all-checkbox').on('click', function (e) {
            e.stopPropagation();
        });
    }
});