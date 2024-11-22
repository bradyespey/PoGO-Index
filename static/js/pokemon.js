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

    // Attach change event listeners to specific checkbox classes only
    $(document).on('change', '.matt-have-checkbox', function () {
        console.log("Matt Have checkbox changed"); // Debug
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed
        const isChecked = $(this).is(':checked') ? 'Yes' : 'No';
        $(this).closest('td').attr('data-filter', isChecked);
    });

    $(document).on('change', '.matt-lucky-checkbox', function () {
        console.log("Matt Lucky checkbox changed"); // Debug
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed
        const isChecked = $(this).is(':checked') ? 'Yes' : 'No';
        $(this).closest('td').attr('data-filter', isChecked);
    });

    $(document).on('change', '.ipad-lucky-checkbox', function () {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed

        // Update the data-filter attribute
        const isChecked = $(this).is(':checked') ? 'Yes' : 'No';
        $(this).closest('td').attr('data-filter', isChecked);
    });

    $(document).on('input', '.note-edit', function() {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed
        console.log("Note input changed:", this); // Debug log
    });

    // Track changes on "Select All" checkboxes
    $('#selectAllMatt, #selectAllMattLucky, #selectAlliPadLucky').on('change', function () {
        const isChecked = $(this).is(':checked');
        let columnIndex;
    
        // Explicitly map each checkbox by ID
        if (this.id === 'selectAllMatt') {
            columnIndex = 7; // Matt 👤 column index
            console.log("Select All Matt triggered. isChecked:", isChecked);
        } else if (this.id === 'selectAllMattLucky') {
            columnIndex = 8; // Matt 🎲 column index
            console.log("Select All Matt Lucky triggered. isChecked:", isChecked);
        } else if (this.id === 'selectAlliPadLucky') {
            columnIndex = 10; // iPad 🎲 column index
            console.log("Select All iPad Lucky triggered. isChecked:", isChecked);
        }
    
        // If columnIndex is correctly determined, update only the relevant column
        if (columnIndex !== undefined) {
            updateColumnCheckboxes(columnIndex, isChecked);
        }
    });

    // Update all checkboxes in a column when "Select All" is toggled
    function updateColumnCheckboxes(columnIndex, isChecked) {
        const table = window.pokemonTable;
        const checkboxClass = getCheckboxClassByColumnIndex(columnIndex);
    
        console.log(`Updating columnIndex: ${columnIndex}, isChecked: ${isChecked}, class: ${checkboxClass}`); // Debug log
    
        table.rows({ page: 'current' }).every(function () {
            const $checkboxCell = $(this.node()).find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find(`input.${checkboxClass}`);
            if (!$checkbox.length) {
                console.warn(`No checkbox found for class: ${checkboxClass}, columnIndex: ${columnIndex}`);
                return; // Exit if no matching checkbox
            }
    
            console.log(`Processing checkbox in columnIndex: ${columnIndex}, row: ${this.index()}, isChecked: ${isChecked}`);
            $checkbox
                .off('change') // Temporarily suppress change event
                .prop('checked', isChecked) // Check/uncheck the checkbox
                .attr('data-filter', isChecked ? 'Yes' : 'No') // Update the filter attribute
                .attr('data-changed', 'true'); // Mark as changed

            console.log(
                `Processing checkbox in columnIndex: ${columnIndex}, row: ${this.index()}, isChecked: ${isChecked}, data-changed: true`
            );

            // Rebind the change event listener to ensure future manual changes are captured
            $checkbox.on('change', function () {
                markChanged();
                $(this).attr('data-changed', 'true');
            });
            $checkbox.trigger('change');
        });
    }
    
    // Helper function to map column indices to the correct checkbox class
    function getCheckboxClassByColumnIndex(columnIndex) {
        if (columnIndex === 7) return 'matt-have-checkbox'; // Matt 👤
        if (columnIndex === 8) return 'matt-lucky-checkbox'; // Matt 🎲
        if (columnIndex === 10) return 'ipad-lucky-checkbox'; // iPad 🎲
        console.warn(`Invalid columnIndex: ${columnIndex}`);
        return ''; // Default to no class
    }

    // Collect changes from notes and checkboxes to send to the backend
    function collectChanges() {
        const notesData = [];
        const checkboxesData = [];
    
        // Collect changes from note edits
        $('.note-edit[data-changed]').each(function () {
            const pokemonId = $(this).closest('tr').find('.hidden-pokemon-id').data('pokemon-id');
            const noteText = $(this).val();
            if (pokemonId !== undefined && noteText !== undefined) {
                notesData.push({ pokemon_id: pokemonId, note: noteText });
            }
        });
    
        // Collect checkbox changes marked with data-changed attribute
        $('.matt-have-checkbox[data-changed], .matt-lucky-checkbox[data-changed], .ipad-lucky-checkbox[data-changed]').each(function () {
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
    
        console.log("Collected changes:", { notes: notesData, checkboxes: checkboxesData }); // Debug log
        return { notes: notesData, checkboxes: checkboxesData };
    }

    // Save changes when "Save Changes" button is clicked
    $('#saveAllChangesButton').on('click', function () {
        if (!hasChanges) {
            alert("No changes to save!");
            return;
        }
    
        const changes = collectChanges();
        console.log("Changes being sent to backend:", changes); // Debug log
    
        if (changes.checkboxes.length === 0 && changes.notes.length === 0) {
            alert("No changes to save!");
            return;
        }
    
        $.ajax({
            url: '/pogo/save-all-changes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(changes),
            success: function () {
                alert('Changes saved successfully!');
                hasChanges = false;
                
                // Update the DataTable to reflect changes
                updateDataTableAfterChanges();
                
                console.log("Changes saved, hasChanges reset to:", hasChanges);
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });

    // Invalidate and redraw DataTable rows after changes are saved
    function updateDataTableAfterChanges() {
        // For each changed checkbox, invalidate the DataTable row
        $('.matt-have-checkbox[data-changed], .matt-lucky-checkbox[data-changed], .ipad-lucky-checkbox[data-changed]').each(function () {
            const $checkbox = $(this);
            const rowElement = $checkbox.closest('tr');
            const dataTableRow = window.pokemonTable.row(rowElement);
            dataTableRow.invalidate();
            $checkbox.removeAttr('data-changed');
        });
    
        // Redraw the DataTable to reflect changes
        window.pokemonTable.draw(false);
    }

    // === DATA TABLE INITIALIZATION AND FILTERING ===

    function applyFilter(dataTable, filter, value) {
        const columnIndex = filter.columnIndex;

        if (filter.type === 'select') {
            if (value) {
                dataTable.column(columnIndex)
                    .search('^' + $.fn.dataTable.util.escapeRegex(value) + '$', true, false)
                    .draw();
            } else {
                dataTable.column(columnIndex).search('', true, false).draw();
            }
        } else if (filter.type === 'numberExact') {
            dataTable.column(columnIndex).search(value ? '^' + value + '$' : '', true, false).draw();
        } else {
            dataTable.column(columnIndex).search(value).draw();
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
        responsive: false,
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
            { title: 'Type', filterType: 'select', options: ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water'] },
            { title: 'Brady 👤', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Brady ✨', filterType: 'select', options: ['Yes', 'No'] }, // New column for Brady ✨
            { title: 'Brady 🎲', filterType: 'select', options: ['Yes', 'No'] },
            { 
                title: 'Matt 👤', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, val, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return $(row[meta.col]).html();
                }
            },
            { 
                title: 'Matt 🎲', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, val, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return $(row[meta.col]).html();
                }
            },
            { title: 'iPad', filterType: 'select', options: ['Yes', 'No'] },
            { 
                title: 'iPad 🎲', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, val, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return $(row[meta.col]).html();
                }
            },
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
            { title: 'Ultra Beast', filterType: null },
            { title: 'Category', filterType: null } // New hidden column if needed
        ],
        columnDefs: [
            { targets: "_all", width: "100px" },
            { targets: [6, 7, 9], orderable: false },
            { targets: [11, 12, 13], visible: false, searchable: true }
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 2, type: 'text' },
            { selector: '#filterType', columnIndex: 3, type: 'select' },
            { selector: '#filterLegendary', columnIndex: 12, type: 'select' },
            { selector: '#filterMythical', columnIndex: 13, type: 'select' },
            { selector: '#filterUltraBeast', columnIndex: 14, type: 'select' }
        ]
    });

    // === CUSTOM SEARCH FUNCTION TO HANDLE HIDDEN COLUMNS ===

    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        const legendaryFilter = $('#filterLegendary').val();
        const mythicalFilter = $('#filterMythical').val();
        const ultraBeastFilter = $('#filterUltraBeast').val();
    
        const legendaryValue = data[12]; // Hidden Legendary column
        const mythicalValue = data[13];  // Hidden Mythical column
        const ultraBeastValue = data[14]; // Hidden Ultra Beast column
    
        // Check Legendary filter
        if (legendaryFilter && legendaryFilter !== legendaryValue) {
            return false;
        }
    
        // Check Mythical filter
        if (mythicalFilter && mythicalFilter !== mythicalValue) {
            return false;
        }
    
        // Check Ultra Beast filter
        if (ultraBeastFilter && ultraBeastFilter !== ultraBeastValue) {
            return false;
        }
    
        return true;
    });    

    // === PREVENT SORTING ON HEADER CHECKBOXES ===

    // Prevent click events on header checkboxes from triggering sort
    $('#selectAllMatt, #selectAllMattLucky, #selectAlliPadLucky').on('click', function (e) {
        e.stopPropagation();
    });

    // === SELECT ALL CHECKBOXES FUNCTIONALITY ===

    // Function to update checkboxes in a column when "Select All" is used
    function updateColumnCheckboxes(columnIndex, isChecked) {
        const table = window.pokemonTable;
        const checkboxClass = getCheckboxClassByColumnIndex(columnIndex);
    
        console.log(`Updating columnIndex: ${columnIndex}, isChecked: ${isChecked}, class: ${checkboxClass}`); // Debug log
    
        table.rows({ page: 'current' }).every(function () {
            const $checkboxCell = $(this.node()).find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find(`input.${checkboxClass}`);
            if (!$checkbox.length) {
                console.warn(`No checkbox found for class: ${checkboxClass}, columnIndex: ${columnIndex}`);
                return; // Exit if no matching checkbox
            }
    
            console.log(`Processing checkbox in columnIndex: ${columnIndex}, row: ${this.index()}, isChecked: ${isChecked}`);
            
            // Apply changes and mark checkbox as changed
            $checkbox
                .off('change') // Temporarily suppress change event
                .prop('checked', isChecked) // Check/uncheck the checkbox
                .attr('data-filter', isChecked ? 'Yes' : 'No') // Update the filter attribute
                .attr('data-changed', 'true'); // Mark as changed
            
            console.log(`Checkbox updated: row ${this.index()}, columnIndex ${columnIndex}, data-changed set to true`);
    
            // Rebind the change event listener
            $checkbox.on('change', function () {
                markChanged();
                $(this).attr('data-changed', 'true');
            });
    
            // Trigger change event programmatically
            $checkbox.trigger('change');
        });
    }

    // Event listeners for "Select All" checkboxes
    $('#selectAllMatt').on('change', function () {
        const isChecked = $(this).is(':checked');
        console.log("Select All Matt triggered. isChecked:", isChecked); // Debug
        updateColumnCheckboxes(7, isChecked); // Matt 👤 column index
    });
    
    $('#selectAllMattLucky').on('change', function () {
        const isChecked = $(this).is(':checked');
        console.log("Select All Matt Lucky triggered. isChecked:", isChecked); // Debug
        console.trace(); // To trace where this event originates
        updateColumnCheckboxes(8, isChecked); // Matt 🎲 column index
    });
    
    $('#selectAlliPadLucky').on('change', function () {
        const isChecked = $(this).is(':checked');
        console.log("Select All iPad Lucky triggered. isChecked:", isChecked); // Debug
        updateColumnCheckboxes(10, isChecked); // iPad 🎲 column index
    });

    // === UPDATE HEADER CHECKBOX STATE ===

    // Ensure the header checkbox is updated based on row checkbox states
    function updateHeaderCheckboxState(columnIndex, headerCheckboxId) {
        const table = window.pokemonTable;
        const checkboxClass = getCheckboxClassByColumnIndex(columnIndex); // Resolve class by columnIndex
        let allChecked = true;
        let anyChecked = false;
    
        table.rows({ page: 'current' }).every(function () {
            const $checkboxCell = $(this.node()).find('td').eq(columnIndex);
            const $checkbox = $checkboxCell.find(`input.${checkboxClass}`); // Target only the column's checkboxes
    
            if ($checkbox.length) {
                if ($checkbox.is(':checked')) {
                    anyChecked = true;
                } else {
                    allChecked = false;
                }
            }
        });
    
        const $headerCheckbox = $('#' + headerCheckboxId);
        console.log(`Updating header checkbox state for columnIndex: ${columnIndex}, allChecked: ${allChecked}, anyChecked: ${anyChecked}`);
        $headerCheckbox.prop('checked', allChecked);
        $headerCheckbox.prop('indeterminate', !allChecked && anyChecked);
    }

    // Update header checkbox state on table redraw
    window.pokemonTable.on('draw', function () {
        updateHeaderCheckboxState(7, 'selectAllMatt'); // Matt 👤
        updateHeaderCheckboxState(8, 'selectAllMattLucky'); // Matt 🎲
        updateHeaderCheckboxState(10, 'selectAlliPadLucky'); // iPad 🎲
    });

    // Event listeners for individual checkboxes to update header checkbox state
    window.pokemonTable.on('draw', function () {
        $('input.matt-have-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(7, 'selectAllMatt'); // Matt 👤
        });

        $('input.matt-lucky-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(8, 'selectAllMattLucky'); // Matt 🎲
        });

        $('input.ipad-lucky-checkbox').off('change').on('change', function () {
            updateHeaderCheckboxState(10, 'selectAlliPadLucky'); // iPad 🎲
        });
    });

    window.pokemonTable.draw();
});