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