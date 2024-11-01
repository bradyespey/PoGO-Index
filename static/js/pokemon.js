$(document).ready(function () {
    // === EDIT MODE FUNCTIONS ===

    let editMode = false;

    function enableEditMode() {
        editMode = true;
        $('.note-display').hide();
        $('.note-edit').show();
        $('#editNotesButton').text('Cancel Editing');
        $('#saveAllChangesButton').show();
    }

    function disableEditMode() {
        editMode = false;
        $('.note-display').show();
        $('.note-edit').hide();
        $('#editNotesButton').text('Edit Notes');
        $('#saveAllChangesButton').hide();
    }

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

    if (window.location.search.includes('edit=true')) {
        enableEditMode();
    }

    function collectChanges() {
        const notesData = [];
        const checkboxesData = [];

        $('.note-edit').each(function () {
            const pokemonId = $(this).closest('tr').find('.hidden-pokemon-id').data('pokemon-id');
            const noteText = $(this).val();
            if (pokemonId !== undefined && noteText !== undefined) {
                notesData.push({ pokemon_id: pokemonId, note: noteText });
            }
        });

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

    $('#saveAllChangesButton').on('click', function () {
        const changes = collectChanges();
        $.ajax({
            url: '/pogo/save-all-changes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(changes),
            success: function () {
                alert('Changes saved successfully!');
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

    // === SELECT ALL/DESELECT ALL CHECKBOXES ===

    $('#selectAllButton').on('click', function () {
        $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', true);
    });

    $('#deselectAllButton').on('click', function () {
        $('.matt-have-checkbox:visible, .ipad-lucky-checkbox:visible').prop('checked', false);
    });

    // === DATA TABLE INITIALIZATION AND FILTERING ===

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
            window.pokemonTable.search('').columns().search('').draw();
            $('#searchName, #filterType, #filterLegendary, #filterMythical, #filterUltraBeast').val('');
            const clonedHeader = window.pokemonTable.table().header();
            $(clonedHeader).find('input, select').val('');
            $('#showEntries').val('10');
            window.pokemonTable.page.len(10).draw();
        }
    });

    // === INITIALIZE ALL TABLES ===

    window.pokemonTable = initializeDataTable({
        tableSelector: '#pokemonTable',
        responsive: true,
        scrollX: true,
        autoWidth: false,
        paging: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        stateSave: true,
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
        columnDefs: [{ targets: [11, 12, 13], visible: false, searchable: true }],
        extraFilters: [
            { selector: '#searchName', columnIndex: 2, type: 'text' },
            { selector: '#filterType', columnIndex: 3, type: 'select' },
            { selector: '#filterLegendary', columnIndex: 11, type: 'select' },
            { selector: '#filterMythical', columnIndex: 12, type: 'select' },
            { selector: '#filterUltraBeast', columnIndex: 13, type: 'select' }
        ]
    });
});
