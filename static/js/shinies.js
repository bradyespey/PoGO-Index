// static/js/shinies.js

$(document).ready(function () {
    let hasChanges = false; // Track if changes were made

    // Centralized function to mark changes
    function markChanged() {
        hasChanges = true;
    }

    // Reset the change tracker after successful save
    function resetChanges() {
        hasChanges = false;
        $('.note-edit, .brady-own-checkbox, .brady-lucky-checkbox, .matt-own-checkbox, .matt-lucky-checkbox').removeAttr('data-changed');
    }

    // Attach change event listeners to all checkboxes
    $(document).on('change', '.brady-own-checkbox, .brady-lucky-checkbox, .matt-own-checkbox, .matt-lucky-checkbox', function() {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed

        // Update the data-filter attribute
        const isChecked = $(this).is(':checked') ? 'Yes' : 'No';
        $(this).closest('td').attr('data-filter', isChecked);
    });

    // Ensure the click event handler for "Save Changes" button is only attached once
    $('#saveAllChangesButton').off('click').on('click', function () {
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
            
                // Update the DataTable to reflect changes
                updateDataTableAfterChanges();
            
                console.log("Changes saved, hasChanges reset to:", hasChanges); // Debug log
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });    

    // Collect changes from checkboxes to send to the backend
    function collectChanges() {
        const checkboxesData = [];

        // Collect checkbox changes marked with data-changed attribute
        $('.brady-own-checkbox[data-changed], .brady-lucky-checkbox[data-changed], .matt-own-checkbox[data-changed], .matt-lucky-checkbox[data-changed]').each(function () {
            const shinyId = $(this).data('shiny-id');
            let checkboxType;

            if ($(this).hasClass('brady-own-checkbox')) checkboxType = 'shiny_brady_own';
            else if ($(this).hasClass('brady-lucky-checkbox')) checkboxType = 'shiny_brady_lucky';
            else if ($(this).hasClass('matt-own-checkbox')) checkboxType = 'shiny_matt_own';
            else if ($(this).hasClass('matt-lucky-checkbox')) checkboxType = 'shiny_matt_lucky';

            const checkedValue = $(this).is(':checked') ? 'Yes' : 'No';
            if (shinyId !== undefined && checkboxType !== undefined) {
                checkboxesData.push({
                    shiny_id: shinyId,
                    type: checkboxType,
                    value: checkedValue
                });
            }
        });

        return { checkboxes: checkboxesData };
    }

    // Invalidate and redraw DataTable rows after changes are saved
    function updateDataTableAfterChanges() {
        // For each changed checkbox, invalidate the DataTable row
        $('.brady-own-checkbox[data-changed], .brady-lucky-checkbox[data-changed], .matt-own-checkbox[data-changed], .matt-lucky-checkbox[data-changed]').each(function () {
            const $checkbox = $(this);
            const rowElement = $checkbox.closest('tr');
            const dataTableRow = window.shiniesTable.row(rowElement);
            dataTableRow.invalidate(); // Invalidate the row's cached data
            $checkbox.removeAttr('data-changed'); // Remove the data-changed attribute
        });
    
        // Redraw the DataTable to reflect changes
        window.shiniesTable.draw(false);
    }

    // === DATA TABLE INITIALIZATION AND FILTERING ===

    // Apply filters from extra filters
    function applyFilter(dataTable, filter, value) {
        const columnIndex = filter.columnIndex;

        if (filter.type === 'select') {
            if (value) {
                // Ensure case matches and spaces are trimmed
                dataTable.column(columnIndex)
                    .search('^' + $.fn.dataTable.util.escapeRegex(value.trim()) + '$', true, false)
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

    // Initialize filters in the cloned header row
    function initializeFilters(clonedHeader, options, dataTable) {
        clonedHeader.find('th').each(function (i) {
            const column = options.columns[i];
            const title = column.title || '';
            const filterType = column.filterType;

            // Generate filter input based on filterType
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
            } else {
                $(this).html(''); // No filter for columns without specified filterType
            }

            // Attach event listeners to filter inputs
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

    // Initialize a DataTable with custom settings
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
            lengthMenu: options.lengthMenu || [10, 25, 50, 100, -1],
            stateSave: false,
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

        // Attach event handlers for extra filters
        if (options.extraFilters) {
            options.extraFilters.forEach(filter => {
                $(filter.selector).on('keyup change clear', function () {
                    applyFilter(dataTable, filter, this.value);
                });
            });
        }

        return dataTable;
    }

    // === INITIALIZE SHINIES TABLE ===

    window.shiniesTable = initializeDataTable({
        tableSelector: '#shiniesTable',
        paging: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
        stateSave: false,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: '#', filterType: 'numberExact' },  // Index 0
            { title: 'Name', filterType: 'text' },      // Index 1
            { title: 'Form', filterType: 'text' },      // Index 2
            { title: 'Method', filterType: 'text' },    // Index 3
            // Brady 👤 column (Index 4)
            { 
                title: 'Brady 👤', 
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
            // Brady 🎲 column (Index 5)
            { 
                title: 'Brady 🎲', 
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
            // Matt 👤 column (Index 6)
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
            // Matt 🎲 column (Index 7)
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
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 1, type: 'text' },
            { selector: '#searchMethod', columnIndex: 3, type: 'text' },
        ],
    });

    // === RESET FILTERS ===
    $('#resetFiltersButton').on('click', function () {
        if (window.pokemonTable || window.shiniesTable) {
            const activeTable = window.pokemonTable ? window.pokemonTable : window.shiniesTable;

            // Clear all column filters and search fields in DataTable
            activeTable.search('').columns().search('').draw();

            // Reset internal filters in the header of the table
            const clonedHeader = activeTable.table().header();
            $(clonedHeader).find('input, select').each(function () {
                $(this).val(''); // Clear the value
            });

            // Reset custom filters outside of the DataTable (search fields for Name, Method, etc.)
            $('#searchName, #searchMethod').val('').trigger('change'); // Specific IDs for your external filters

            // Reset entries to the default value of 10
            $('#showEntries').val('10').trigger('change');
            activeTable.page.len(10).draw();

            // Reset sorting to the default sorting (first column ascending)
            activeTable.order([0, 'asc']).draw();
        }
    });

    // === SELECT ALL / DESELECT ALL ===

    function updateColumnCheckboxes(columnClass, isChecked) {
        $(`.${columnClass}`).each(function () {
            $(this).prop('checked', isChecked);
            $(this).attr('data-changed', 'true');
            $(this).trigger('change'); // Trigger the change event
            markChanged();
        });
    }

    $('#selectAllBradyOwn').on('change', function () {
        const isChecked = $(this).is(':checked');
        updateColumnCheckboxes('brady-own-checkbox', isChecked);
    });

    $('#selectAllBradyLucky').on('change', function () {
        const isChecked = $(this).is(':checked');
        updateColumnCheckboxes('brady-lucky-checkbox', isChecked);
    });

    $('#selectAllMattOwn').on('change', function () {
        const isChecked = $(this).is(':checked');
        updateColumnCheckboxes('matt-own-checkbox', isChecked);
    });

    $('#selectAllMattLucky').on('change', function () {
        const isChecked = $(this).is(':checked');
        updateColumnCheckboxes('matt-lucky-checkbox', isChecked);
    });
});

