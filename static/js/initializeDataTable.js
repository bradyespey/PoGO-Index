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

// Initialize a DataTable with custom settings
function initializeDataTable(options) {
    const tableSelector = options.tableSelector;
    const table = $(tableSelector);

    // Check if the table exists on the page
    if (table.length === 0) {
        return null;
    }

    // Remove existing cloned header rows to prevent duplication
    table.find('thead tr.clone').remove();

    // Clone the first header row to add filter inputs
    const originalHeader = table.find('thead tr').first();
    const clonedHeader = originalHeader.clone(true).addClass('clone').appendTo(table.find('thead'));

    // Initialize the DataTable with options and custom settings
    const dataTable = table.DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        paging: options.paging !== false,
        pageLength: options.pageLength || 10,
        lengthMenu: options.lengthMenu || [10, 25, 50, 100],
        stateSave: options.stateSave || false,
        searching: options.searching !== false,
        lengthChange: options.lengthChange !== false,
        columnDefs: options.columnDefs || [],
        
        // State save settings - clear global search on save
        stateSaveParams: (settings, data) => { data.search.search = ''; },

        // Adjust column visibility and widths on initialization
        initComplete: function () {
            const api = this.api();
            api.columns().visible(true); // Make sure all columns are visible initially
            api.columns.adjust();        // Adjust column widths
        }
    });

    // Initialize filters in the cloned header row
    initializeFilters(clonedHeader, options, dataTable);

    // Handle custom entries per page setting, if selector is provided
    if (options.showEntriesSelector) {
        $(options.showEntriesSelector).on('change', function () {
            dataTable.page.len(this.value).draw();
        });
    }

    // Attach any additional filters outside the table
    if (options.extraFilters) {
        options.extraFilters.forEach(filter => {
            $(filter.selector).on('keyup change clear', function () {
                applyFilter(dataTable, filter, this.value);
            });
        });
    }

    return dataTable;
}

// Initialize all DataTables on the page
function initializeAllTables() {
    // Pokémon Table Initialization
    window.pokemonTable = initializeDataTable({
        tableSelector: '#pokemonTable',
        responsive: true,
        scrollX: true,
        autoWidth: false,
        paging: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100],
        stateSave: true,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: '#', filterType: 'numberExact' },
            { title: 'Image', filterType: null },
            { title: 'Name', filterType: 'text' },
            {
                title: 'Type',
                filterType: 'select',
                options: ['Grass', 'Poison', 'Fire', 'Water', 'Electric', 'Ice', 'Fighting', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']
            },
            { title: 'Brady', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Brady Lucky', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt Lucky', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'iPad', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'iPad Lucky', filterType: 'select', options: ['Yes', 'No'] },
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
            },
            { title: 'Legendary', filterType: null },
            { title: 'Mythical', filterType: null },
            { title: 'Ultra Beast', filterType: null },
        ],
        columnDefs: [
            {
                targets: [10, 11, 12], // Hide the Legendary, Mythical, and Ultra Beast columns
                visible: false,
                searchable: true
            }
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 2, type: 'text' },
            { selector: '#filterType', columnIndex: 3, type: 'select' },
            { selector: '#filterLegendary', columnIndex: 11, type: 'select' },
            { selector: '#filterMythical', columnIndex: 12, type: 'select' },
            { selector: '#filterUltraBeast', columnIndex: 13, type: 'select' },
        ]
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

// Document ready function to initialize all tables on the page
$(document).ready(function () {
    initializeAllTables(); // Call to initialize all DataTables on the page.
});