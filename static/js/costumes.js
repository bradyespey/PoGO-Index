// static/js/costumes.js

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
    $(document).on('change', '.brady-own-checkbox, .brady-shiny-checkbox, .matt-own-checkbox, .matt-shiny-checkbox', function () {
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
        if (filter.type === 'text') {
            dataTable.column(columnIndex).search(value).draw();
        } else if (filter.type === 'numberExact') {
            dataTable.column(columnIndex).search(value ? '^' + value + '$' : '', true, false).draw();
        } else if (filter.type === 'select') {
            if (value) {
                dataTable.column(columnIndex)
                    .search('^' + $.fn.dataTable.util.escapeRegex(value.trim()) + '$', true, false)
                    .draw();
            } else {
                dataTable.column(columnIndex).search('').draw();
            }
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
                $(this).html(''); // No filter for columns without a specified filterType
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
                if (val) {
                    dataTable.column(i).search('^' + $.fn.dataTable.util.escapeRegex(val) + '$', true, false).draw();
                } else {
                    dataTable.column(i).search('').draw();
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

    // Function to adjust columns after images have loaded
    function adjustColumnsWhenImagesLoaded() {
        const images = $('#costumesTable').find('img');
        const totalImages = images.length;
        let imagesLoaded = 0;
    
        if (totalImages === 0) {
            window.costumesTable.columns.adjust();
            return;
        }
    
        images.each(function () {
            if (this.complete) {
                imagesLoaded++;
                if (imagesLoaded === totalImages) {
                    window.costumesTable.columns.adjust();
                }
            } else {
                $(this).on('load error', function () {
                    imagesLoaded++;
                    if (imagesLoaded === totalImages) {
                        window.costumesTable.columns.adjust();
                    }
                });
            }
        });
    }

    // Modify initializeDataTable to include image filtering logic
    function initializeDataTable(options) {
        const tableSelector = options.tableSelector;
        const table = $(tableSelector);
        if (table.length === 0) return null;
    
        // Remove any previously cloned headers to prevent duplication
        table.find('thead tr.clone-header').remove();
    
        const originalHeader = table.find('thead tr').first();
        const clonedHeader = originalHeader.clone(true).addClass('clone-header').appendTo(table.find('thead'));
    
        const dataTable = table.DataTable({
            scrollX: true,
            responsive: false,
            orderCellsTop: true,
            fixedHeader: true,
            paging: options.paging,
            pageLength: options.pageLength,
            lengthMenu: options.lengthMenu,
            stateSave: false,
            searching: options.searching,
            lengthChange: options.lengthChange,
            columnDefs: options.columnDefs,
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
            { title: '#', filterType: 'numberExact' },            // Column 0
            { title: 'Name', filterType: 'text' },                // Column 1
            { title: 'Costume', filterType: 'text' },             // Column 2
            // Image column with custom filter                     // Column 3
            { 
                title: 'Image', 
                filterType: 'select', 
                options: ['Has Image', 'No Image'],
                specialFilter: applyImageFilter
            },
            // Brady 👤 column                                     // Column 4
            { 
                title: 'Brady 👤', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (data, type, row, meta) {
                    if (type === 'filter' || type === 'sort') {
                        // Retrieve data-filter attribute from the cell
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return data;
                }
            },
            // Matt 👤 column                                      // Column 5
            { 
                title: 'Matt 👤', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (data, type, row, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return data;
                }
            },
            // Shiny Image column with custom filter              // Column 6
            { 
                title: 'Shiny', 
                filterType: 'select', 
                options: ['Has Image', 'No Image'],
                specialFilter: applyImageFilter
            },
            // Brady ✨ column                                     // Column 7
            { 
                title: 'Brady ✨', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (data, type, row, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return data;
                }
            },
            // Matt ✨ column                                      // Column 8
            { 
                title: 'Matt ✨', 
                filterType: 'select', 
                options: ['Yes', 'No'],
                data: function (data, type, row, meta) {
                    if (type === 'filter' || type === 'sort') {
                        var cell = meta.settings.aoData[meta.row].anCells[meta.col];
                        return $(cell).attr('data-filter') || '';
                    }
                    return data;
                }
            },
        ],
        extraFilters: [
            { selector: '#searchName', columnIndex: 1, type: 'text' },
            { selector: '#searchCostume', columnIndex: 2, type: 'text' }
        ]
    });
    
    // Final adjustment on full page load to ensure columns align after all elements are ready
    $(window).on('load', function () {
        if (window.costumesTable) {
            // Call the image loading adjustment function in case any images were cached but not detected initially
            adjustColumnsWhenImagesLoaded();
            
            // Force a final column adjustment to ensure header alignment
            window.costumesTable.columns.adjust();
        }
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

            // Adjust columns after reset
            window.costumesTable.columns.adjust();
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