// static/js/all_pokemon.js

$(document).ready(function () {
    // === DATA TABLE INITIALIZATION AND FILTERING ===

    // Function to apply filters from extra filters
    function applyFilter(dataTable, filter, value) {
        if (filter.type === 'select') {
            // Apply regular select filter
            dataTable
                .column(filter.columnIndex)
                .search(value ? '^' + $.fn.dataTable.util.escapeRegex(value) + '$' : '', true, false)
                .draw();
        } else if (filter.type === 'numberExact') {
            dataTable.column(filter.columnIndex).search(value ? '^' + value + '$' : '', true, false).draw();
        } else {
            dataTable.column(filter.columnIndex).search(value).draw();
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
            columnDefs: [
                { targets: [3], searchable: true } // Enable built-in search for Generation column
            ],
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

    // === INITIALIZE ALL POKÉMON TABLE ===

    window.allPokemonTable = initializeDataTable({
        tableSelector: '#allPokemonTable',
        paging: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
        stateSave: false,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: 'Dex #', filterType: 'numberExact' },     // Index 0
            { title: 'Name', filterType: 'text' },             // Index 1
            { title: 'Category', filterType: 'select', options: ['Starter', 'Legendary', 'Mythical', 'Fossil', 'Baby', 'Ultra Beast', 'Paradox'] }, // Index 2
            { title: 'Generation', filterType: 'select', options: ['1', '2', '3', '4', '5', '6', '7', '8', '9'] }, // Index 3
            { title: 'Released', filterType: 'select', options: ['Yes', 'No'] }  // Index 4
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 1, type: 'text' },
            { selector: '#searchCategory', columnIndex: 2, type: 'select' },
            { selector: '#filterReleased', columnIndex: 4, type: 'select' }
        ]
    });

    // === RESET FILTERS ===

    $('#resetFiltersButton').on('click', function () {
        if (window.allPokemonTable) {
            // Clear all search filters from columns and redraw the table
            window.allPokemonTable.search('').columns().search('').draw();

            // Clear the inputs and selectors
            const clonedHeader = window.allPokemonTable.table().header();
            $(clonedHeader).find('input, select').val('').trigger('change');

            // Reset all custom filters as well
            [
                '#searchName',
                '#searchCategory',
                '#filterReleased',
            ].forEach(selector => {
                $(selector).val('').trigger('change');
            });

            // Reset page length
            $('#showEntries').val('10');
            window.allPokemonTable.page.len(10).draw();
        }
    });

    // Handle changes in the show entries selector
    $('#showEntries').on('change', function () {
        const entries = $(this).val();
        window.allPokemonTable.page.len(entries).draw();
    });
});
