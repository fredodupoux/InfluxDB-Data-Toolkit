// --- DOM Elements ---
// Navbar
const navExportBtn = document.getElementById('nav-export-btn');
const navOpenFileBtn = document.getElementById('nav-open-file-btn');
const navCleanBtn = document.getElementById('nav-clean-btn');
const navReformatBtn = document.getElementById('nav-reformat-btn');
const navButtons = [navExportBtn, navOpenFileBtn, navCleanBtn, navReformatBtn];

// Content Sections
const exportSection = document.getElementById('export-section');
const openFileSection = document.getElementById('open-file-section');
const previewSection = document.getElementById('preview-section');
const cleanDataSection = document.getElementById('clean-data-section');
const reformatTimeSection = document.getElementById('reformat-time-section');
const contentSections = [exportSection, openFileSection, previewSection, cleanDataSection, reformatTimeSection];

// Export Section Elements
const exportForm = document.getElementById('export-form');
const exportStatusDiv = document.getElementById('export-status');

// Open File Section Elements
const fileSelectMain = document.getElementById('file-select-main');
const refreshFilesBtn = document.getElementById('refresh-files-btn');
const fileListStatusDiv = document.getElementById('file-list-status');

// Preview Section Elements
const previewArea = document.getElementById('preview-area');
const previewFilename = document.getElementById('preview-filename');
const previewInfo = document.getElementById('preview-info');
const previewTableContainer = document.getElementById('preview-table-container');
const previewPlaceholder = document.getElementById('preview-placeholder');
// Using fileListStatusDiv for preview loading/error messages for now

// Clean Data Section Elements
const cleanFilenameDisplay = document.getElementById('clean-filename-display');
const operationsBuilder = document.getElementById('operations-builder');
const operationsListUl = document.getElementById('operations-list');
const executeCleanButton = document.getElementById('execute-clean-button');
const cleanStatusDiv = document.getElementById('clean-status');
const addRemoveColBtn = document.getElementById('add-remove-col-btn');
const addFilterBtn = document.getElementById('add-filter-btn');
const addRenameColBtn = document.getElementById('add-rename-col-btn');

// Reformat Time Section Elements
const reformatFilenameDisplay = document.getElementById('reformat-filename-display');
const reformatOptions = document.getElementById('reformat-options');
const reformatConvertTzCheckbox = document.getElementById('reformat-convert-tz-checkbox');
const reformatTzInputDiv = document.getElementById('reformat-tz-input-div');
const reformatTargetTzInput = document.getElementById('reformat-target-tz');
const reformatKeepTimeOnlyCheckbox = document.getElementById('reformat-keep-time-only-checkbox');
const executeReformatButton = document.getElementById('execute-reformat-button');
const reformatStatusDiv = document.getElementById('reformat-status');

// Modal elements (remain the same)
const removeColModal = document.getElementById('remove-col-modal');
const filterModal = document.getElementById('filter-modal');
const renameColModal = document.getElementById('rename-col-modal');
const removeColSelect = document.getElementById('remove-col-select');
const filterColSelect = document.getElementById('filter-col-select');
const filterOperatorSelect = document.getElementById('filter-operator-select');
const filterValueInput = document.getElementById('filter-value-input');
const renameColSelect = document.getElementById('rename-col-select');
const renameNewNameInput = document.getElementById('rename-new-name-input');

// --- State ---
let availableFiles = [];
let selectedFilename = null; // Central state for the currently selected file
let currentPreviewData = null;
let cleaningOperations = []; // Array to hold operation objects
let activeSectionId = 'preview-section'; // Track the currently visible section

// --- Helper function to display status messages ---
function showStatus(element, message, type = 'info') {
    element.textContent = message;
    element.className = `status-message status-${type}`;
    element.style.display = 'block';
}

// --- Navigation Logic ---
function showSection(sectionId) {
    activeSectionId = sectionId;
    contentSections.forEach(section => {
        if (section.id === sectionId) {
            section.classList.remove('hidden');
        } else {
            section.classList.add('hidden');
        }
    });

    // Update navbar button active states
    navButtons.forEach(button => {
        if (button.id === `nav-${sectionId.split('-')[0]}-btn` || (sectionId === 'open-file-section' && button.id === 'nav-open-file-btn')) {
             button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Special handling for preview section (always visible conceptually, but content changes)
    if (sectionId !== 'preview-section') {
        previewSection.classList.add('hidden');
    } else {
         previewSection.classList.remove('hidden'); // Ensure preview section is shown when explicitly selected (though it's default)
    }

    // Enable/disable Clean/Reformat buttons based on file selection
    const fileIsSelected = !!selectedFilename;
    navCleanBtn.disabled = !fileIsSelected;
    navReformatBtn.disabled = !fileIsSelected;
}

// --- Function to fetch and update file list ---
async function fetchFiles(selectFilenameAfterFetch = null) {
    showStatus(fileListStatusDiv, 'Loading file list...', 'loading');
    fileSelectMain.innerHTML = '<option value="">-- Loading... --</option>';
    fileSelectMain.disabled = true;
    availableFiles = [];

    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const files = await response.json();
        availableFiles = files; // Store files

        fileSelectMain.innerHTML = ''; // Clear loading
        if (files.length === 0) {
            fileSelectMain.innerHTML = '<option value="">-- No CSV files found --</option>';
            fileSelectMain.disabled = true;
            showStatus(fileListStatusDiv, 'No CSV files found in _data directory.', 'info');
        } else {
            fileSelectMain.innerHTML = '<option value="">-- Select a file --</option>';
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                fileSelectMain.appendChild(option);
            });
            fileSelectMain.disabled = false; // Enable select
            fileListStatusDiv.style.display = 'none'; // Hide status on success

            // Auto-select file if specified
            if (selectFilenameAfterFetch && availableFiles.includes(selectFilenameAfterFetch)) {
                fileSelectMain.value = selectFilenameAfterFetch;
                // Trigger change event manually to load preview etc.
                fileSelectMain.dispatchEvent(new Event('change'));
            } else if (selectedFilename && !availableFiles.includes(selectedFilename)) {
                 // If the previously selected file is gone, reset
                 resetSelectionAndPreview();
            } else if (selectedFilename) {
                // Keep current selection if it still exists
                fileSelectMain.value = selectedFilename;
            }
        }
    } catch (error) {
        console.error('Error fetching files:', error);
        fileSelectMain.innerHTML = '<option value="">-- Error loading files --</option>';
        fileSelectMain.disabled = true;
        showStatus(fileListStatusDiv, `Error loading files: ${error.message}`, 'error');
        resetSelectionAndPreview(); // Reset on error
    }
}

// --- Function to reset file selection and preview ---
function resetSelectionAndPreview() {
    selectedFilename = null;
    currentPreviewData = null;
    fileSelectMain.value = '';
    previewArea.style.display = 'none';
    previewPlaceholder.style.display = 'block';
    navCleanBtn.disabled = true;
    navReformatBtn.disabled = true;
    cleanFilenameDisplay.textContent = 'No file selected';
    reformatFilenameDisplay.textContent = 'No file selected';
    resetCleaningOperations();
    executeCleanButton.disabled = true;
    executeReformatButton.disabled = true;
    // Optionally switch back to the 'Open File' view or keep the current view
    // showSection('open-file-section');
}

// --- Function to fetch and display file preview ---
async function fetchAndDisplayPreview(filename) {
    if (!filename) {
        resetSelectionAndPreview();
        return;
    }

    showStatus(fileListStatusDiv, 'Loading preview...', 'loading'); // Use file list status for preview loading
    previewPlaceholder.style.display = 'none';
    previewArea.style.display = 'none';
    currentPreviewData = null;

    try {
        const response = await fetch('/api/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `Preview failed with status: ${response.status}`);
        }

        currentPreviewData = result; // Store preview data

        // Display preview info
        previewFilename.textContent = filename;
        previewInfo.textContent = `Shape: (${result.shape.join(', ')}), Columns: ${result.columns.length}`;

        // Display preview table (head)
        previewTableContainer.innerHTML = ''; // Clear previous table
        if (result.head && result.head.length > 0) {
            // ... (table generation code remains the same)
            const table = document.createElement('table');
            const thead = table.createTHead();
            const tbody = table.createTBody();
            const headerRow = thead.insertRow();

            // Create headers
            result.columns.forEach(colName => {
                const th = document.createElement('th');
                th.textContent = colName;
                headerRow.appendChild(th);
            });

            // Create rows
            result.head.forEach(rowData => {
                const row = tbody.insertRow();
                result.columns.forEach(colName => {
                    const cell = row.insertCell();
                    cell.textContent = rowData[colName] !== null && rowData[colName] !== undefined ? rowData[colName] : '';
                });
            });
            previewTableContainer.appendChild(table);
        }

        previewArea.style.display = 'block';
        fileListStatusDiv.style.display = 'none'; // Hide loading message
        resetCleaningOperations(); // Clear any previous operations for the new file

        // Update displays in other sections
        cleanFilenameDisplay.textContent = filename;
        reformatFilenameDisplay.textContent = filename;

        // Enable relevant nav buttons and action buttons
        navCleanBtn.disabled = false;
        navReformatBtn.disabled = false;
        executeCleanButton.disabled = true; // Disabled until operations are added
        executeReformatButton.disabled = false;

        // Optionally switch to preview view if another section was active
        if (activeSectionId !== 'preview-section') {
             showSection('preview-section');
        }

    } catch (error) {
        console.error('Preview error:', error);
        showStatus(fileListStatusDiv, `Failed to load preview: ${error.message}`, 'error');
        resetSelectionAndPreview(); // Reset on error
    }
}

// --- Cleaning Operations Logic ---
function addCleaningOperation(operation) {
    cleaningOperations.push(operation);
    renderOperationsList();
    executeCleanButton.disabled = false; // Enable execute button
}

function removeCleaningOperation(index) {
    cleaningOperations.splice(index, 1);
    renderOperationsList();
    executeCleanButton.disabled = cleaningOperations.length === 0; // Disable if no operations
}

function renderOperationsList() {
    operationsListUl.innerHTML = ''; // Clear list
    cleaningOperations.forEach((op, index) => {
        const li = document.createElement('li');
        let description = '';
        switch (op.action) {
            case 'remove_column':
                description = `Remove column: <code>${op.column}</code>`;
                break;
            case 'filter':
                description = `Filter where <code>${op.column}</code> ${op.operator} <code>${op.value}</code>`;
                break;
            case 'rename_column':
                description = `Rename column <code>${op.old_name}</code> to <code>${op.new_name}</code>`;
                break;
        }
        li.innerHTML = `${description} <button data-index="${index}">Remove</button>`;
        operationsListUl.appendChild(li);
    });

    // Add event listeners to new remove buttons
    operationsListUl.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', (e) => {
            const indexToRemove = parseInt(e.target.getAttribute('data-index'), 10);
            removeCleaningOperation(indexToRemove);
        });
    });
}

function resetCleaningOperations() {
    cleaningOperations = [];
    renderOperationsList();
    executeCleanButton.disabled = true;
}

// --- Modal Handling ---
function openModal(modalId) {
    if (!selectedFilename || !currentPreviewData || !currentPreviewData.columns) {
        // Use clean status div for messages related to cleaning modals
        showStatus(cleanStatusDiv, 'Please select a file and wait for the preview to load first.', 'error');
        return;
    }
    // ... (rest of the modal opening logic remains the same)
    populateColumnSelect(removeColSelect, currentPreviewData.columns);
    populateColumnSelect(filterColSelect, currentPreviewData.columns);
    populateColumnSelect(renameColSelect, currentPreviewData.columns);

    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    // Clear inputs on close
    if (modalId === 'filter-modal') filterValueInput.value = '';
    if (modalId === 'rename-col-modal') renameNewNameInput.value = '';
}

function populateColumnSelect(selectElement, columns) {
    selectElement.innerHTML = ''; // Clear existing options
    columns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col;
        selectElement.appendChild(option);
    });
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Initial setup
    fetchFiles();
    showSection('preview-section'); // Show preview section by default
    navOpenFileBtn.classList.add('active'); // Set Open File as active initially

    // Navbar listeners
    navExportBtn.addEventListener('click', () => showSection('export-section'));
    navOpenFileBtn.addEventListener('click', () => showSection('open-file-section'));
    navCleanBtn.addEventListener('click', () => {
        if (!navCleanBtn.disabled) showSection('clean-data-section');
    });
    navReformatBtn.addEventListener('click', () => {
        if (!navReformatBtn.disabled) showSection('reformat-time-section');
    });

    // Export form listener
    exportForm.addEventListener('submit', handleExportSubmit);

    // File selection listener
    fileSelectMain.addEventListener('change', (e) => {
        selectedFilename = e.target.value;
        fetchAndDisplayPreview(selectedFilename);
    });

    // Refresh files button listener
    refreshFilesBtn.addEventListener('click', () => fetchFiles(selectedFilename)); // Pass current selection to try and preserve it

    // Reformat options listeners
    reformatConvertTzCheckbox.addEventListener('change', (e) => {
        reformatTzInputDiv.style.display = e.target.checked ? 'block' : 'none';
    });

    // Execute Reformat button listener
    executeReformatButton.addEventListener('click', handleReformatSubmit);

    // Modal triggers
    addRemoveColBtn.addEventListener('click', () => openModal('remove-col-modal'));
    addFilterBtn.addEventListener('click', () => openModal('filter-modal'));
    addRenameColBtn.addEventListener('click', () => openModal('rename-col-modal'));

    // Modal confirmation buttons (logic remains the same)
    document.getElementById('confirm-remove-col').addEventListener('click', () => {
        const column = removeColSelect.value;
        if (column) {
            addCleaningOperation({ action: 'remove_column', column: column });
            closeModal('remove-col-modal');
        }
    });

    document.getElementById('confirm-filter').addEventListener('click', () => {
        const column = filterColSelect.value;
        const operator = filterOperatorSelect.value;
        const value = filterValueInput.value;
        if (column && operator && value !== '') {
            addCleaningOperation({ action: 'filter', column: column, operator: operator, value: value });
            closeModal('filter-modal');
        } else {
            alert('Please fill in all filter fields.');
        }
    });

    document.getElementById('confirm-rename-col').addEventListener('click', () => {
        const old_name = renameColSelect.value;
        const new_name = renameNewNameInput.value.trim();
        if (old_name && new_name) {
            if (currentPreviewData.columns.includes(new_name)) {
                alert(`Column "${new_name}" already exists. Please choose a different name.`);
                return;
            }
            addCleaningOperation({ action: 'rename_column', old_name: old_name, new_name: new_name });
            closeModal('rename-col-modal');
        } else {
            alert('Please select a column and enter a new name.');
        }
    });

    // Execute cleaning listener
    executeCleanButton.addEventListener('click', async () => {
        if (!selectedFilename || cleaningOperations.length === 0) {
            showStatus(cleanStatusDiv, 'Please select a file and add at least one cleaning operation.', 'error');
            return;
        }

        showStatus(cleanStatusDiv, 'Applying cleaning operations...', 'loading');
        executeCleanButton.disabled = true;
        let cleanedFilenameResult = null;

        try {
            const response = await fetch('/api/clean', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: selectedFilename, operations: cleaningOperations })
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `Cleaning failed with status: ${response.status}`);
            }

            cleanedFilenameResult = result.cleanedFilename;
            showStatus(cleanStatusDiv, `Cleaning successful! New file created: ${cleanedFilenameResult}`, 'success');
            // Refresh file list and attempt to select the new file
            fetchFiles(cleanedFilenameResult);

        } catch (error) {
            console.error('Cleaning error:', error);
            showStatus(cleanStatusDiv, `Cleaning failed: ${error.message}`, 'error');
            // Re-enable button on failure only if operations still exist
             executeCleanButton.disabled = cleaningOperations.length === 0;
        } finally {
             // Button state is handled by fetchFiles/fetchAndDisplayPreview if successful
        }
    });

    // Close modals if clicked outside content
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    }
});

// --- handleExportSubmit function ---
async function handleExportSubmit(event) {
    // ... (logic remains the same, ensure status is shown in exportStatusDiv)
    event.preventDefault();
    const daysInput = document.getElementById('export-days');
    const deviceInput = document.getElementById('export-device');
    const days = parseInt(daysInput.value, 10);
    const device = deviceInput.value.trim();

    if (isNaN(days) || days <= 0) {
        showStatus(exportStatusDiv, 'Please enter a valid positive number for days.', 'error');
        return;
    }
    if (!device) {
        showStatus(exportStatusDiv, 'Please enter a device name.', 'error');
        return;
    }

    showStatus(exportStatusDiv, 'Exporting data...', 'loading');
    let exportedFilename = null;

    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ days: days, device: device }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `Export failed with status: ${response.status}`);
        }

        exportedFilename = result.filename;
        showStatus(exportStatusDiv, `Export successful! File created: ${exportedFilename}`, 'success');
        // Refresh the file list and switch to open file view, selecting the new file
        fetchFiles(exportedFilename);
        showSection('open-file-section');

    } catch (error) {
        console.error('Export error:', error);
        showStatus(exportStatusDiv, `Export failed: ${error.message}`, 'error');
    }
}

// --- function to handle Timestamp Reformatting Submit ---
async function handleReformatSubmit() {
    if (!selectedFilename) {
        showStatus(reformatStatusDiv, 'Please select a file to reformat.', 'error');
        return;
    }

    // ... (rest of the logic remains the same, using selectedFilename)
    const convertTimezone = reformatConvertTzCheckbox.checked;
    const keepTimeOnly = reformatKeepTimeOnlyCheckbox.checked;
    let targetTimezone = reformatTargetTzInput.value.trim();

    if (convertTimezone && !targetTimezone) {
        targetTimezone = 'America/New_York'; // Default
    }
    if (!convertTimezone) {
        targetTimezone = null;
    }

    showStatus(reformatStatusDiv, 'Reformatting timestamps...', 'loading');
    executeReformatButton.disabled = true;
    let reformattedFilenameResult = null;

    try {
        const response = await fetch('/api/reformat_time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: selectedFilename,
                convertTimezone: convertTimezone,
                targetTimezone: targetTimezone,
                keepTimeOnly: keepTimeOnly
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `Reformatting failed with status: ${response.status}`);
        }

        reformattedFilenameResult = result.reformattedFilename;
        showStatus(reformatStatusDiv, `Reformatting successful! New file created: ${reformattedFilenameResult}`, 'success');
        // Refresh file list and attempt to select the new file
        fetchFiles(reformattedFilenameResult);

    } catch (error) {
        console.error('Reformat error:', error);
        showStatus(reformatStatusDiv, `Reformatting failed: ${error.message}`, 'error');
        // Re-enable button on failure
        executeReformatButton.disabled = !selectedFilename;
    } finally {
         // Button state is handled by fetchFiles/fetchAndDisplayPreview if successful
    }
}

// === Configuration Management ===
const configModal = document.getElementById('config-modal');
const configBtn = document.getElementById('nav-config-btn');
const closeConfigBtn = document.getElementById('close-config-modal');
const cancelConfigBtn = document.getElementById('cancel-config-btn');
const saveConfigBtn = document.getElementById('save-config-btn');
const reloadConfigBtn = document.getElementById('reload-config-btn');
const configSelect = document.getElementById('config-select');
const configEditor = document.getElementById('config-editor');
const configStatus = document.getElementById('config-status');

function showConfigModal() {
  configModal.style.display = 'block';
  loadConfigFile();
}
function hideConfigModal() {
  configModal.style.display = 'none';
  configStatus.style.display = 'none';
}
configBtn.addEventListener('click', showConfigModal);
closeConfigBtn.addEventListener('click', hideConfigModal);
cancelConfigBtn.addEventListener('click', hideConfigModal);
window.addEventListener('click', function(event) {
  if (event.target === configModal) hideConfigModal();
});
configSelect.addEventListener('change', loadConfigFile);
reloadConfigBtn.addEventListener('click', loadConfigFile);

function loadConfigFile() {
  const name = configSelect.value;
  configStatus.style.display = 'none';
  configEditor.value = '';
  fetch(`/api/config/${name}`)
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        configStatus.textContent = data.error;
        configStatus.className = 'status-message status-error';
        configStatus.style.display = '';
      } else {
        configEditor.value = JSON.stringify(data, null, 2);
      }
    })
    .catch(err => {
      configStatus.textContent = 'Failed to load config: ' + err;
      configStatus.className = 'status-message status-error';
      configStatus.style.display = '';
    });
}

saveConfigBtn.addEventListener('click', function() {
  const name = configSelect.value;
  let json;
  try {
    json = JSON.parse(configEditor.value);
  } catch (e) {
    configStatus.textContent = 'Invalid JSON: ' + e.message;
    configStatus.className = 'status-message status-error';
    configStatus.style.display = '';
    return;
  }
  configStatus.textContent = 'Saving...';
  configStatus.className = 'status-message status-loading';
  configStatus.style.display = '';
  fetch(`/api/config/${name}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(json)
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        configStatus.textContent = data.error;
        configStatus.className = 'status-message status-error';
      } else {
        configStatus.textContent = data.message || 'Saved!';
        configStatus.className = 'status-message status-success';
      }
      configStatus.style.display = '';
    })
    .catch(err => {
      configStatus.textContent = 'Failed to save config: ' + err;
      configStatus.className = 'status-message status-error';
      configStatus.style.display = '';
    });
});

// === Global Toast Notification System ===
function showToast(message, type = 'info', duration = 4000) {
    let toast = document.getElementById('global-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'global-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `global-toast toast-${type}`;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, duration);
}

// Patch fetch to show toast on network/server errors globally
const originalFetch = window.fetch;
window.fetch = function(...args) {
    return originalFetch(...args).then(async response => {
        if (!response.ok) {
            let msg = `Error: ${response.status}`;
            try {
                const data = await response.clone().json();
                if (data && data.error) msg = data.error;
            } catch {}
            showToast(msg, 'error');
        }
        return response;
    }).catch(err => {
        showToast('Network error: ' + err, 'error');
        throw err;
    });
};
