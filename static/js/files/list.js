"use strict";

var KTFileManagerList = function () {
    var datatable;
    var table

    var uploadTemplate;
    var actionTemplate;
    var checkboxTemplate;


    const initTemplates = () => {
        uploadTemplate = document.querySelector('[data-kt-filemanager-template="upload"]');
        actionTemplate = document.querySelector('[data-kt-filemanager-template="action"]');
        checkboxTemplate = document.querySelector('[data-kt-filemanager-template="checkbox"]');
    }

    const initDatatable = () => {
        const tableRows = table.querySelectorAll('tbody tr');

        tableRows.forEach(row => {
            const dateRow = row.querySelectorAll('td');
            const dateCol = dateRow[3];
            const realDate = moment(dateCol.innerHTML, "DD MMM YYYY, LT").format();
            dateCol.setAttribute('data-order', realDate);
        });

        const filesListOptions = {
            "info": false,
            'order': [],
            'pageLength': 5,
            "paging": true,
            "lengthChange": false,
            'ordering': true,
            'order': [[2, 'desc']],
            'columnDefs': [
                { orderable: false, targets: 3 },               
            ],
            'columns': [
                { data: 'name' },
                { data: 'size' },
                { data: 'date' },
                { data: 'action' },
            ]
        };

        var loadOptions;
        loadOptions = filesListOptions;

        datatable = $(table).DataTable(loadOptions);

        datatable.on('draw', function () {
            toggleToolbars();
            KTMenu.createInstances();
            countTotalItems();
        });
    }

    const handleSearchDatatable = () => {
        const filterSearch = document.querySelector('[data-kt-filemanager-table-filter="search"]');
        filterSearch.addEventListener('keyup', function (e) {
            datatable.search(e.target.value).draw();
        });
    }

    const toggleToolbars = () => {
        const toolbarBase = document.querySelector('[data-kt-filemanager-table-toolbar="base"]');
        const toolbarSelected = document.querySelector('[data-kt-filemanager-table-toolbar="selected"]');
        const selectedCount = document.querySelector('[data-kt-filemanager-table-select="selected_count"]');

        const allCheckboxes = table.querySelectorAll('tbody [type="checkbox"]');

        let checkedState = false;
        let count = 0;

        allCheckboxes.forEach(c => {
            if (c.checked) {
                checkedState = true;
                count++;
            }
        });

        if (checkedState) {
            selectedCount.innerHTML = count;
            toolbarBase.classList.add('d-none');
            toolbarSelected.classList.remove('d-none');
        } else {
            toolbarBase.classList.remove('d-none');
            toolbarSelected.classList.add('d-none');
        }
    }

    const countTotalItems = () => {
        const counter = document.getElementById('kt_file_manager_items_counter');
        const itemCount = datatable.rows().count();
        counter.innerText = itemCount + ' ' + (itemCount === 1 ? 'file' : 'files');
    }

    const initUpload = () => {
        const fileInput = document.getElementById('file_input');
        const uploadButton = document.getElementById('upload_button');
        const fileNameDisplay = document.getElementById('file_name');
        const modalElement = document.getElementById('kt_modal_upload'); 
    
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
    
            if (file) {
                if (file.name.endsWith('.txt') && file.type === 'text/plain') {
                    if (file.size >= 512 && file.size <= 2048) {
                        uploadButton.disabled = false;
                        fileNameDisplay.textContent = file.name;
                    } else {
                        uploadButton.disabled = true;
                        fileInput.value = '';
                        fileNameDisplay.textContent = "";
                        Swal.fire({
                            icon: 'error',
                            title: 'Invalid File Size',
                            text: 'File size must be between 0.5 KB and 2 KB.',
                            confirmButtonText: 'OK',
                            customClass: {
                                title: 'text-gray-900'
                            }
                        });
                    }
                } else {
                    uploadButton.disabled = true;
                    fileInput.value = '';
                    fileNameDisplay.textContent = "";
                    Swal.fire({
                        icon: 'error',
                        title: 'Invalid File',
                        text: 'Only .txt files are allowed.',
                        confirmButtonText: 'OK',
                        customClass: {
                            title: 'text-gray-900'
                        }
                    });
                }
            }
        });
    
        uploadButton.addEventListener('click', function() {
            uploadButton.setAttribute('data-kt-indicator', 'on');
            uploadButton.disabled = true;
            const formData = new FormData(document.getElementById('file_upload_form'));
    
            axios.post('/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
            .then(function(response) {
                uploadButton.removeAttribute('data-kt-indicator');
                uploadButton.disabled = false;
                Swal.fire({
                    icon: 'success',
                    text: response.data.status,
                    confirmButtonText: 'OK',
                }).then(() => {
                    const modal = bootstrap.Modal.getInstance(modalElement); 
                    modal.hide();
                    fileNameDisplay.textContent = ""; 
    
                    window.location.reload();
    
                    toggleToolbars();
                    countTotalItems();
                    KTMenu.createInstances();
                });
            })
            .catch(function(error) {
                uploadButton.removeAttribute('data-kt-indicator');
                uploadButton.disabled = false;
                Swal.fire({
                    icon: 'error',
                    title: 'Upload Failed',
                    text: error.response && error.response.data ? error.response.data.error : 'File upload failed',
                    confirmButtonText: 'Retry',
                    customClass: {
                        title: 'text-gray-900'
                    }
                });
            });
        });
    }

    var getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const handleFileContentDisplay = () => {
        table.querySelectorAll('tbody tr').forEach(row => {
            const fileNameLink = row.querySelector('td a');
            const viewOption = row.querySelector('[data-action="view"]');
            const downloadOption = row.querySelector('[data-action="download"]'); 
    
            const displayFileContent = async () => {
                const fileName = fileNameLink.textContent.trim();
                const fileContentDisplay = document.getElementById('file_content_display');
                const fileContentSection = document.getElementById('file_content_section');
                const fileContentTitle = document.getElementById('file_content_title');
    
                if (!fileContentSection.classList.contains('d-none') && fileContentTitle.textContent.includes(fileName)) {
                    return; 
                }
    
                KTApp.showPageLoading();
    
                try {
                    const response = await axios.get(`/api/file-content/${fileName}/`);
                    const content = response.data.content;
                    KTApp.hidePageLoading();
    
                    fileContentTitle.innerText = `File Content: ${fileName}`;
                    fileContentDisplay.innerText = content;
                    fileContentSection.classList.remove('d-none');
    
                    const searchInput = document.getElementById('search_content');
                    searchInput.value = '';
                    searchInput.addEventListener('keyup', () => highlightSearch(content));
                } catch (error) {
                    KTApp.hidePageLoading();
                    console.error("Error fetching file content:", error);
                }
            };
    
            
            fileNameLink.addEventListener('click', (event) => {
                event.preventDefault();
                displayFileContent();
            });
    
            
            viewOption.addEventListener('click', displayFileContent);
    
            
            downloadOption.addEventListener('click', async () => {
                const fileName = fileNameLink.textContent.trim();
                try {
                    const response = await axios.get(`/api/download/${fileName}/`, {
                        responseType: 'blob' 
                    });
    
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', fileName); 
                    document.body.appendChild(link);
                    link.click();
    
                    
                    link.remove();
                    window.URL.revokeObjectURL(url);
                } catch (error) {
                    console.error("Error downloading file:", error);
                }
            });
        });
    };
    
    
    const highlightSearch = (content) => {
        const searchInput = document.getElementById('search_content').value.trim();
        const fileContentDisplay = document.getElementById('file_content_display');
    
        if (searchInput) {
            const regex = new RegExp(`(${searchInput})`, 'gi');
            const highlightedContent = content.replace(regex, `<span class="bg-warning">$1</span>`);
            fileContentDisplay.innerHTML = highlightedContent;
        } else {
            fileContentDisplay.innerText = content;
        }
    };
    
    const initFileContentFeature = () => {
        handleFileContentDisplay();
    };

    const initCloseButton = () => {
        const closeButton = document.getElementById('close_file_content');
        const fileContentSection = document.getElementById('file_content_section');
    
        closeButton.addEventListener('click', () => {
            fileContentSection.classList.add('d-none');
        });
    };

    return {
        init: function () {
            table = document.querySelector('#kt_file_manager_list');

            if (!table) {
                return;
            }

            initTemplates();
            initDatatable();
            handleSearchDatatable();
            countTotalItems();
            initUpload();
            KTMenu.createInstances();
            initFileContentFeature();
            initCloseButton();
        }
    }
}();

KTUtil.onDOMContentLoaded(function () {
    KTFileManagerList.init();
});