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
                let selectHtml = '<select><option value="">All</option>';
                column.options.forEach(opt => {
                    selectHtml += `<option value="${opt}">${opt}</option>`;
                });
                selectHtml += '</select>';
                $(this).html(selectHtml);
            } else {
                $(this).html('');
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

    // === Initialize Costumes DataTable ===
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
            { title: 'Brady 👤', filterType: 'select', options: ['Yes', 'No'] },
            { title: 'Matt 👤', filterType: 'select', options: ['Yes', 'No'] },
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
