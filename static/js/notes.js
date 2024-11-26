// static/js/notes.js

$(document).ready(function () {
    // === DATA TABLE INITIALIZATION AND FILTERING ===

    // Function to apply filters from extra filters
    function applyFilter(dataTable, filter, value) {
        if (filter.type === 'select') {
            if (value) {
                dataTable
                    .column(filter.columnIndex)
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

        if (options.extraFilters) {
            options.extraFilters.forEach(filter => {
                $(filter.selector).on('keyup change clear', function () {
                    applyFilter(dataTable, filter, this.value);
                });
            });
        }

        return dataTable;
    }

    // === INITIALIZE NOTES TABLE ===

    window.notesTable = initializeDataTable({
        tableSelector: '#notesTable',
        paging: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
        stateSave: false,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: '#', filterType: 'numberExact' },    // Index 0
            { title: 'Name', filterType: 'text' },        // Index 1
            { title: 'Note', filterType: 'text' },        // Index 2
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 1, type: 'text' },
            { selector: '#searchNote', columnIndex: 2, type: 'text' },
        ],
    });

    // === RESET FILTERS ===

    $('#resetFiltersButton').on('click', function () {
        if (window.notesTable) {
            // Clear DataTables filters
            window.notesTable.search('').columns().search('').draw();

            // Reset cloned header inputs and selects
            const clonedHeader = window.notesTable.table().header();
            $(clonedHeader).find('input, select').val('');

            // Reset additional filter elements outside the table
            [
                '#searchName',
                '#searchNote',
            ].forEach(selector => {
                $(selector).val('');
            });

            // Reset entries per page to default
            $('#showEntries').val('10');
            window.notesTable.page.len(10).draw();
        }
    });

    // Handle changes in the show entries selector
    $('#showEntries').on('change', function () {
        const entries = $(this).val();
        window.notesTable.page.len(entries).draw();
    });
});
