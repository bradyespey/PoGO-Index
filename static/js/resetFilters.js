// Reset all filters and redraw tables
$('#resetFiltersButton').on('click', function () {
    const tablesToReset = [
        {
            table: window.pokemonTable,
            filters: ['#searchName', '#filterType', '#filterLegendary', '#filterMythical', '#filterUltraBeast']
        }
        // Additional tables can be added here with their filters
    ];

    tablesToReset.forEach(function (item) {
        if (item.table) {
            // Clear DataTables filters
            item.table.search('').columns().search('').draw();

            // Reset cloned header inputs and selects
            const clonedHeader = item.table.table().header();
            $(clonedHeader).find('input, select').val('');

            // Reset additional filter elements outside the table
            item.filters.forEach(selector => {
                $(selector).val('');
            });

            // Reset entries per page to default
            $('#showEntries').val('10');
            item.table.page.len(10).draw();
        }
    });
});