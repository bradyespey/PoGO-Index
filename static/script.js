$(document).ready(function () {
    // Function to initialize DataTables with custom settings
    function initializeDataTable(options) {
        var tableSelector = options.tableSelector;
        var table = $(tableSelector);

        if (table.length === 0) {
            return null; // Table not found on the page
        }

        // Remove existing cloned header rows to prevent duplication
        table.find('thead tr.clone').remove();

        // Clone the first header row to add filter inputs
        var originalHeader = table.find('thead tr').first();
        var clonedHeader = originalHeader.clone(true).addClass('clone').appendTo(table.find('thead'));

        // Initialize DataTable
        var dataTable = table.DataTable({
            orderCellsTop: true,
            fixedHeader: true,
            paging: options.paging !== false,
            pageLength: options.pageLength || 10,
            lengthMenu: options.lengthMenu || [10, 25, 50, 100],
            stateSave: options.stateSave || false,
            searching: options.searching !== false,
            lengthChange: options.lengthChange !== false,
            columnDefs: options.columnDefs || [],
            // Enable state saving for filters
            stateSaveParams: function (settings, data) {
                data.search.search = '';
            }
        });

        // Initialize filters in the cloned header
        initializeFilters(clonedHeader, options, dataTable);

        // Custom entries per page
        if (options.showEntriesSelector) {
            $(options.showEntriesSelector).on('change', function () {
                dataTable.page.len(this.value).draw();
            });
        }

        // Additional filters outside the table
        if (options.extraFilters) {
            options.extraFilters.forEach(function (filter) {
                $(filter.selector).on('keyup change clear', function () {
                    applyFilter(dataTable, filter, this.value);
                });
            });
        }

        return dataTable;
    }

    // Function to initialize filters in the cloned header
    function initializeFilters(clonedHeader, options, dataTable) {
        clonedHeader.find('th').each(function (i) {
            var column = options.columns[i];
            var title = column.title || '';
            var filterType = column.filterType;

            if (filterType === 'text') {
                $(this).html('<input type="text" placeholder="Search ' + title + '" />');
            } else if (filterType === 'numberExact') {
                $(this).html('<input type="number" placeholder="Search ' + title + '" />');
            } else if (filterType === 'select') {
                var selectHtml = '<select>';
                selectHtml += '<option value="">All</option>';
                column.options.forEach(function (opt) {
                    selectHtml += '<option value="' + opt + '">' + opt + '</option>';
                });
                selectHtml += '</select>';
                $(this).html(selectHtml);
            } else {
                $(this).html(''); // No filter
            }

            // Add event listeners to inputs and selects
            $('input', this).on('keyup change clear', function () {
                var val = this.value;
                if (filterType === 'numberExact') {
                    dataTable.column(i).search(val ? '^' + val + '$' : '', true, false).draw();
                } else {
                    dataTable.column(i).search(val).draw();
                }
            });

            $('select', this).on('change', function () {
                var val = $(this).val();
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

    // Function to initialize all tables
    function initializeAllTables() {
        // Initialize Pokemon Table
        console.log("Initializing Pokémon Table");
        window.pokemonTable = initializeDataTable({
            tableSelector: '#pokemonTable',
            responsive: true,
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: true, // Keep stateSave enabled
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Image', filterType: null }, // Index 1
                { title: 'Name', filterType: 'text' }, // Index 2
                {
                    title: 'Type',
                    filterType: 'select',
                    options: [
                        'Grass', 'Poison', 'Fire', 'Water', 'Electric', 'Ice', 'Fighting', 'Ground', 'Flying',
                        'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
                    ]
                }, // Index 3
                { title: 'Have Living Dex', filterType: 'select', options: ['Yes', 'No'] }, // Index 4
                { title: 'Have Shiny', filterType: 'select', options: ['Yes', 'No'] }, // Index 5
                { title: 'Shiny Available', filterType: 'select', options: ['Yes', 'No'] }, // Index 6
                { title: 'Shiny Note', filterType: 'text' }, // Index 7
                { title: 'Need on iPad', filterType: 'select', options: ['Yes', 'No'] }, // Index 8
                {
                    title: 'Note',
                    filterType: 'select',
                    options: ['Has Notes', 'No Notes'],
                    specialFilter: function (column, val) {
                        if (val === 'Has Notes') {
                            column.search('^(?!\\s*$).+', true, false).draw(); // Match non-empty values
                        } else if (val === 'No Notes') {
                            column.search('^\\s*$', true, false).draw(); // Match empty or whitespace-only values
                        } else {
                            column.search('').draw();
                        }
                    }
                }, // Index 9
                { title: 'Legendary', filterType: null }, // Index 10 (Hidden)
                { title: 'Mythical', filterType: null }, // Index 11 (Hidden)
                { title: 'Ultra Beast', filterType: null }, // Index 12 (Hidden)
            ],
            columnDefs: [
                {
                    targets: [10, 11, 12], // Hide the Legendary, Mythical, and Ultra Beast columns
                    visible: false,
                    searchable: true  // Ensure these hidden columns are searchable
                }
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 2, type: 'text' },
                // Type Filter
                { selector: '#filterType', columnIndex: 3, type: 'select' },
                // Legendary Filter
                { selector: '#filterLegendary', columnIndex: 10, type: 'select' },
                // Mythical Filter
                { selector: '#filterMythical', columnIndex: 11, type: 'select' },
                // Ultra Beast Filter
                { selector: '#filterUltraBeast', columnIndex: 12, type: 'select' },
            ],
        });

        // Initialize Poke Genie Table
        window.pokeGenieTable = initializeDataTable({
            tableSelector: '#pokeGenieTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Form', filterType: 'text' }, // Index 2
                { title: 'Pokemon Number', filterType: 'numberExact' }, // Index 3
                { title: 'Gender', filterType: 'text' }, // Index 4
                { title: 'CP', filterType: 'numberExact' }, // Index 5
                { title: 'Quick Move', filterType: 'text' }, // Index 6
                { title: 'Charge Move', filterType: 'text' }, // Index 7
                { title: 'Charge Move 2', filterType: 'text' }, // Index 8
                { title: 'Scan Date', filterType: 'text' }, // Index 9
                { title: 'Original Scan Date', filterType: 'text' }, // Index 10
                { title: 'Catch Date', filterType: 'text' }, // Index 11
                {
                    title: 'Lucky',
                    filterType: 'select',
                    options: ['Yes', 'No']
                }, // Index 12
                {
                    title: 'Shadow/Purified',
                    filterType: 'select',
                    options: ['Regular', 'Shadow', 'Purified']
                }, // Index 13
                {
                    title: 'Favorite',
                    filterType: 'select',
                    options: ['Normal', 'Shiny', 'Costume', 'Shiny Costume', 'iPad Need', 'Extras']
                }, // Index 14
                { title: 'Name (G)', filterType: 'text' }, // Index 15
                { title: 'Name (U)', filterType: 'text' }, // Index 16
                { title: 'Name (L)', filterType: 'text' }, // Index 17
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
            ],
        });

        // Initialize Rocket Table
        window.rocketTable = initializeDataTable({
            tableSelector: '#rocketTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Shadow Living Dex', filterType: 'select', options: ['Yes', 'No'] }, // Index 2
                { title: 'Purified Living Dex', filterType: 'select', options: ['Yes', 'No'] }, // Index 3
                { title: 'Method', filterType: 'text' }, // Index 4
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
            ],
        });

        // Initialize Shinies Table
        window.shiniesTable = initializeDataTable({
            tableSelector: '#shiniesTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' },     // Index 1
                { title: 'Method', filterType: 'text' },   // Index 2
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
                // Method Search
                { selector: '#searchMethod', columnIndex: 2, type: 'text' },
            ],
        });

        // Initialize Specials Table
        window.specialsTable = initializeDataTable({
            tableSelector: '#specialsTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Type', filterType: 'select', options: ['Legendary', 'Mythical', 'Ultra Beast', 'Paradox'] }, // Index 2
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
                // Type Filter
                { selector: '#filterType', columnIndex: 2, type: 'select' },
            ],
        });

        // Initialize Costumes Table
        console.log("Initializing Pokémon Table");
        window.costumesTable = initializeDataTable({
            tableSelector: '#costumesTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Costume', filterType: 'text' }, // Index 2
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
                // Costume Search
                { selector: '#searchCostume', columnIndex: 2, type: 'text' },
            ],
        });

        // Initialize Forms Table
        window.formsTable = initializeDataTable({
            tableSelector: '#formsTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Form', filterType: 'text' }, // Index 2
                { title: 'Available', filterType: 'select', options: ['Yes', 'No'] }, // Index 3
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
                // Form Search
                { selector: '#searchForm', columnIndex: 2, type: 'text' },
                // Available Filter
                { selector: '#filterAvailable', columnIndex: 3, type: 'select' },
            ],
        });

        // Initialize Notes Table
        window.notesTable = initializeDataTable({
            tableSelector: '#notesTable',
            paging: true,
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            stateSave: false,
            searching: true,
            lengthChange: false,
            showEntriesSelector: '#showEntries',
            columns: [
                { title: '#', filterType: 'numberExact' }, // Index 0
                { title: 'Name', filterType: 'text' }, // Index 1
                { title: 'Note', filterType: 'text' }, // Index 2
            ],
            extraFilters: [
                // Name Search
                { selector: '#searchName', columnIndex: 1, type: 'text' },
                // Note Search
                { selector: '#searchNote', columnIndex: 2, type: 'text' },
            ],
        });
    }

    // Call the function to initialize all tables
    initializeAllTables();

    // Preloader logic (if any)
    window.addEventListener('load', function () {
        document.body.classList.add('loaded');
    });

    var editMode = false; // Moved editMode outside to make it globally accessible

    // Function to enable edit mode
    function enableEditMode() {
        editMode = true;
        $('.note-display').hide();
        $('.note-edit').show();
        $('#editNotesButton').text('Cancel Editing');
        $('#saveAllNotesButton').show(); // Show global Save button
    }

    // Function to disable edit mode
    function disableEditMode() {
        editMode = false;
        $('.note-display').show();
        $('.note-edit').hide();
        $('#editNotesButton').text('Edit Notes');
        $('#saveAllNotesButton').hide(); // Hide global Save button
    }

    // Edit Notes button functionality
    $('#editNotesButton').on('click', function () {
        if (!editMode) {
            $.get('/pogo/is_authenticated', function (response) {
                if (response.authenticated) {
                    enableEditMode();
                } else {
                    var currentUrl = window.location.pathname + window.location.search;
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
        enableEditMode(); // Automatically enable edit mode on page load
    }

    // Global Save All Notes button functionality
    $('#saveAllNotesButton').on('click', function () {
        var notesData = [];

        // Collect all notes that have been edited
        $('.note-edit').each(function () {
            var pokemonId = $(this).closest('tr').find('.hidden-pokemon-id').data('pokemon-id');
            var noteText = $(this).val();

            if (pokemonId !== undefined && noteText !== undefined) {
                notesData.push({ pokemon_id: pokemonId, note: noteText });
            }
        });

        // Send the notes to the server
        $.ajax({
            url: '/pogo/update-notes',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ notes: notesData }),
            success: function () {
                alert('All notes saved successfully!');
                // Update the note displays and disable edit mode without reloading
                $('.note-edit').each(function () {
                    var noteText = $(this).val();
                    $(this).hide();
                    $(this).siblings('.note-display').text(noteText).show();
                });
                disableEditMode();
            },
            error: function () {
                alert('Failed to save notes. Please try again.');
            }
        });
    });

    // Event listener for Reset All button
    $('#resetFiltersButton').on('click', function () {
        // Array of table objects and their corresponding reset functions
        var tablesToReset = [
            { table: window.pokemonTable, filters: ['#searchName', '#filterType', '#filterLegendary', '#filterMythical', '#filterUltraBeast'] },
            // Include other tables if necessary
        ];

        tablesToReset.forEach(function (item) {
            if (item.table) {
                // Reset DataTables filters
                item.table.search('').columns().search('').draw();

                // Reset the input and select elements in the cloned header
                var clonedHeader = item.table.table().header();
                $(clonedHeader).find('input, select').val('');

                // Reset the input and select elements in the extra filters
                item.filters.forEach(function (selector) {
                    $(selector).val('');
                });

                // Reset entries per page to default
                $('#showEntries').val('10');
                item.table.page.len(10).draw();
            }
        });
    });
});