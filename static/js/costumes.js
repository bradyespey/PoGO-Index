$(document).ready(function () {
    let hasChanges = false;

    // Function to mark when changes occur
    function markChanged() {
        hasChanges = true;
    }

    // Reset changes after successful save
    function resetChanges() {
        hasChanges = false;
        $('.brady-own-checkbox, .brady-shiny-checkbox, .matt-own-checkbox, .matt-shiny-checkbox').removeAttr('data-changed');
    }

    // Track changes on checkbox modification
    $(document).on('change', '.brady-own-checkbox, .brady-shiny-checkbox, .matt-own-checkbox, .matt-shiny-checkbox', function() {
        markChanged();
        $(this).attr('data-changed', 'true'); // Mark as changed

        // Update the data-filter attribute
        const isChecked = $(this).is(':checked') ? 'Yes' : 'No';
        $(this).closest('td').attr('data-filter', isChecked);
    });

    // Save Changes button event
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
                
                // Invalidate and redraw the DataTable
                updateDataTableAfterChanges();

                resetChanges();
            },
            error: function () {
                alert('Failed to save changes. Please try again.');
            }
        });
    });

    // Collect modified checkboxes for saving
    function collectChanges() {
        const checkboxesData = [];

        $('.brady-own-checkbox[data-changed], .brady-shiny-checkbox[data-changed], .matt-own-checkbox[data-changed], .matt-shiny-checkbox[data-changed]').each(function () {
            const costumeId = $(this).data('costume-id');
            let checkboxType;

            if ($(this).hasClass('brady-own-checkbox')) checkboxType = 'costume_brady_own';
            else if ($(this).hasClass('brady-shiny-checkbox')) checkboxType = 'costume_brady_shiny';
            else if ($(this).hasClass('matt-own-checkbox')) checkboxType = 'costume_matt_own';
            else if ($(this).hasClass('matt-shiny-checkbox')) checkboxType = 'costume_matt_shiny';

            const checkedValue = $(this).is(':checked') ? 'Yes' : 'No';
            if (costumeId !== undefined && checkboxType !== undefined) {
                checkboxesData.push({
                    costume_id: costumeId,
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
        $('.brady-own-checkbox[data-changed], .brady-shiny-checkbox[data-changed], .matt-own-checkbox[data-changed], .matt-shiny-checkbox[data-changed]').each(function () {
            const $checkbox = $(this);
            const rowElement = $checkbox.closest('tr');
            const dataTableRow = window.costumesTable.row(rowElement);
            dataTableRow.invalidate(); // Invalidate the row's cached data
            $checkbox.removeAttr('data-changed'); // Remove the data-changed attribute
        });
    
        // Redraw the DataTable to reflect changes
        window.costumesTable.draw(false);
    }

    // Apply filter settings for DataTable columns
    function applyFilter(dataTable, filter, value) {
        const columnIndex = filter.columnIndex;

        if (filter.type === 'select') {
            if (value) {
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

            if (filterType === 'text') {
                $(this).html('<input type="text" placeholder="Search ' + title + '" />');
            } else if (filterType === 'numberExact') {
                $(this).html('<input type="number" placeholder="Search ' + title + '" />');
            } else if (filterType === 'select') {
                // Manually add a single "All" option and then add unique options
                let selectHtml = '<select><option value="">All</option>';

                // Use a Set to ensure options are unique and avoid duplicates
                const uniqueOptions = new Set(column.options);
                uniqueOptions.forEach(opt => {
                    if (opt !== "All") {  // Avoid adding "All" again
                        selectHtml += `<option value="${opt}">${opt}</option>`;
                    }
                });

                selectHtml += '</select>';
                $(this).html(selectHtml);
            }

            // Event listeners for filter inputs
            $('input', this).on('keyup change clear', function () {
                const val = this.value;
                if (filterType === 'numberExact') {
                    dataTable.column(i).search(val ? '^' + val + '$' : '', true, false).draw();
                } else {
                    dataTable.column(i).search(val).draw();
                }
            });

            // Handle select dropdown change with custom filters for image columns
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

    // Custom filter for image presence
    function applyImageFilter(column, value) {
        if (value === "Has Image" || value === "No Image") {
            column.search(value, true, false).draw();
        } else {
            column.search('').draw(); // Reset filter for "All"
        }
    }

    // Modify initializeDataTable to include image filtering logic
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

        // Additional logic for Image filters
        dataTable.columns().every(function(index) {
            const column = this;
        
            $('select', clonedHeader.find('th').eq(index)).on('change', function () {
                const val = $(this).val();
                const columnTitle = options.columns[index].title;
        
                // Apply custom image filter logic for "Image" and "Shiny Image" columns
                if (columnTitle === 'Image' || columnTitle === 'Shiny Image') {
                    applyImageFilter(column, val);
                } else if (val) {
                    column.search('^' + $.fn.dataTable.util.escapeRegex(val) + '$', true, false).draw();
                } else {
                    column.search('').draw();
                }
            });
        });

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

    // Initialize DataTable with adjusted columns
    window.costumesTable = initializeDataTable({
        tableSelector: '#costumesTable',
        paging: true,
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
        stateSave: false,
        searching: true,
        lengthChange: false,
        showEntriesSelector: '#showEntries',
        columns: [
            { title: '#', filterType: 'numberExact' },
            { title: 'Name', filterType: 'text' },
            { title: 'Costume', filterType: 'text' },
            { title: 'Image', filterType: 'select', options: ['All', 'Has Image', 'No Image'] },
            // Brady 👤 column
            { 
                title: 'Brady 👤', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, set, meta) {
                    if (type === 'filter' || type === 'sort') {
                        return $(row).find('td').eq(meta.col).attr('data-filter') || '';
                    }
                    return null; // Use default renderer
                }
            },
            // Matt 👤 column
            { 
                title: 'Matt 👤', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, set, meta) {
                    if (type === 'filter' || type === 'sort') {
                        return $(row).find('td').eq(meta.col).attr('data-filter') || '';
                    }
                    return null; // Use default renderer
                }
            },
            // Shiny Released column
            { title: 'Shiny Released', filterType: 'select', options: ['Yes', 'No'] },
            // Shiny Image column
            { title: 'Shiny Image', filterType: 'select', options: ['All', 'Has Image', 'No Image'] },
            // Brady ✨ column
            { 
                title: 'Brady ✨', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, set, meta) {
                    if (type === 'filter' || type === 'sort') {
                        return $(row).find('td').eq(meta.col).attr('data-filter') || '';
                    }
                    return null; // Use default renderer
                }
            },
            // Matt ✨ column
            { 
                title: 'Matt ✨', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (row, type, set, meta) {
                    if (type === 'filter' || type === 'sort') {
                        return $(row).find('td').eq(meta.col).attr('data-filter') || '';
                    }
                    return null; // Use default renderer
            }
        },
            { title: 'Shiny Released', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Shiny Image', filterType: 'select', options: ['All', 'Has Image', 'No Image'] },
            { title: 'Brady ✨', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt ✨', filterType: 'select', options: ['Yes', 'No'] }
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 1, type: 'text' },
            { selector: '#searchCostume', columnIndex: 2, type: 'text' }
        ]
    });

    // === Reset Filters ===
    $('#resetFiltersButton').on('click', function () {
        if (window.costumesTable) {
            window.costumesTable.search('').columns().search('').draw();
            const clonedHeader = window.costumesTable.table().header();
            $(clonedHeader).find('input, select').val('');
            $('#searchName, #searchCostume').val('');
            $('#showEntries').val('10');
            window.costumesTable.page.len(10).draw();
        }
    });

    // === Select All / Deselect All ===
    function updateColumnCheckboxes(columnClass, isChecked) {
        $(`.${columnClass}`).each(function () {
            $(this).prop('checked', isChecked);
            $(this).attr('data-changed', 'true');
            $(this).trigger('change'); // Trigger the change event
            markChanged();
        });
    }

    $('#selectAllBradyOwn').on('change', function () {
        updateColumnCheckboxes('brady-own-checkbox', $(this).is(':checked'));
    });

    $('#selectAllBradyShiny').on('change', function () {
        updateColumnCheckboxes('brady-shiny-checkbox', $(this).is(':checked'));
    });

    $('#selectAllMattOwn').on('change', function () {
        updateColumnCheckboxes('matt-own-checkbox', $(this).is(':checked'));
    });

    $('#selectAllMattShiny').on('change', function () {
        updateColumnCheckboxes('matt-shiny-checkbox', $(this).is(':checked'));
    });
});