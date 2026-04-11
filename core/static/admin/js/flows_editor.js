document.addEventListener('DOMContentLoaded', function () {


    function exportToJson() {
        const dataStr = hiddenField.value; // Get the current state
        if (!dataStr || dataStr === '{"steps":[]}') {
            alert("No data to export!");
            return;
        }

        // Create a blob and a temporary download link
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        // Naming the file (optional: add timestamp)
        const timestamp = new Date().toISOString().slice(0, 10);
        link.href = url;
        link.download = `flow_export_${timestamp}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
}


    // 1. Create a hidden file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.json';
        fileInput.style.display = 'none';

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedData = JSON.parse(event.target.result);
                    
                    // Validate structure (expecting { "steps": [...] })
                    if (importedData && Array.isArray(importedData.steps)) {
                        // Update the global groups variable using your existing grouping function
                        groups = groupSteps(importedData.steps);
                        
                        // Refresh the UI and the hidden Django field
                        render();
                        updateHiddenField();
                        alert("✅ Flows imported successfully!");
                    } else {
                        alert("❌ Invalid file format. Please use a valid Flow JSON.");
                    }
                } catch (err) {
                    alert("❌ Error parsing JSON file.");
                    console.error(err);
                }
            };
            reader.readAsText(file);
        };

    const hiddenField = document.querySelector('input[name="flows_json"]');
    if (!hiddenField) return;
    
    const METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
    const PHASES = ['request', 'response'];

    const container = document.createElement('div');
    container.className = 'inline-group';
    hiddenField.closest('.form-row').after(container);

    /* =========================
       ACTIONS
    ========================== */

    const ACTIONS = {
        detect: {},
        edit_body: { element_regix: '', new_value: '' },
        remove_body_element: { element_regix: '' },
        edit_headers: { value: '',header_key : ''},
        reject: {},
        redirect: { destination: '' },
        forward: {},
        change_body: { content: '' },
        extract_header: { header_key: '' },
        remove_header: { header_key: '',  },
        extract_body_element: { element_regix: '', return_name: '' },
        extract_query: { query_key: '' },
        edit_query: { query_key: '', new_value: '' },
        remove_query: { query_key: '' },
        applyFunction: { function: '' },
        APGMastercard: { return_name: '' },
        CybersourceFlexV2: { return_name: '' },
        change_status_code: { status_code: 200 },
        insertHeaderKey: { header_key: '', header_value: '' },
        customDetect: { regix_type: 'query', value: '' },
        editUrlParam: { param_regix: '', new_value: '' },
        removeUrlParam: { param_regix: '' },
        extractURLParams: { param_regix: '', return_name: '' }
    };

    let groups = [];

    /* =========================
       LOAD OLD DATA → GROUPS
    ========================== */

    function groupSteps(flatSteps) {
        const map = {};

        flatSteps.forEach(step => {
            const p = step.params || {};
            const key = `${p.method}|${p.url_regix}|${p.phase}`;

            if (!map[key]) {
                map[key] = {
                    method: p.method || 'GET',
                    url_regix: p.url_regix || '',
                    phase: p.phase || 'request',
                    steps: []
                };
            }

            const { method, url_regix, phase, ...rest } = p;

            map[key].steps.push({
                action: step.action,
                log: step.log || false,
                params: rest
            });
        });

        return Object.values(map);
    }

    try {
        const parsed = hiddenField.value
            ? JSON.parse(hiddenField.value).steps || []
            : [];

        groups = groupSteps(parsed);

    } catch {
        groups = [];
    }

    /* =========================
       FLATTEN BEFORE SAVE
    ========================== */

    function flattenGroups() {
        const result = [];

        groups.forEach(group => {
            group.steps.forEach(step => {
                result.push({
                    action: step.action,
                    log: step.log,
                    params: {
                        ...step.params,
                        method: group.method,
                        url_regix: group.url_regix,
                        phase: group.phase
                    }
                });
            });
        });

        return result;
    }

    function updateHiddenField() {
        hiddenField.value = JSON.stringify({
            steps: flattenGroups()
        });
    }

    /* =========================
       PARAMS RENDER
    ========================== */

    function renderParams(step, container) {

        container.innerHTML = '';

        const template = ACTIONS[step.action];

        Object.keys(template).forEach(key => {

            const row = document.createElement('div');
            row.className = 'form-row';

            const label = document.createElement('label');
            label.textContent = key;

            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'vTextField';

            input.value = step.params[key] ?? template[key];

            input.oninput = () => {
                step.params[key] = input.value;
                updateHiddenField();
            };

            row.appendChild(label);
            row.appendChild(input);
            container.appendChild(row);
        });
    }

    /* =========================
       MAIN RENDER
    ========================== */

    function render() {

        container.innerHTML = '';
        container.appendChild(document.createElement('hr'));

        //import buttun
        const importBtn = document.createElement('input');
        importBtn.type = 'button';
        importBtn.value = '📤 Import Flows from JSON';
        importBtn.className = 'button';
        
        // Style it slightly different (e.g., Blue or a different Green)
        importBtn.style.backgroundColor = '#17a2b8'; // Teal/Info Blue
        importBtn.style.color = 'white';
        importBtn.style.fontWeight = 'bold';
        importBtn.style.padding = '10px 20px';
        importBtn.style.marginLeft = '10px';
        importBtn.style.border = 'none';
        importBtn.style.borderRadius = '4px';
        importBtn.style.cursor = 'pointer';

        // When clicked, trigger the hidden file input
        importBtn.onclick = () => fileInput.click();

        // Append them to the container
        container.appendChild(fileInput);
        container.appendChild(importBtn);

        container.appendChild(document.createElement('hr'));

        // export btn 
        container.appendChild(document.createElement('hr'));
        const exportBtn = document.createElement('input');
        exportBtn.type = 'button';
        exportBtn.value = 'Export to JSON File';
        exportBtn.className = 'button'; // Django admin default button style
        exportBtn.style.marginLeft = '10px';
        exportBtn.style.backgroundColor = '#28a745'; // Django header blue
        exportBtn.style.color = 'white';

        exportBtn.onclick = exportToJson;

        // Append it next to your "Add Request Group" button
        container.appendChild(exportBtn);
        container.appendChild(document.createElement('hr'));

        groups.forEach((group, gIndex) => {

            const groupBlock = document.createElement('fieldset');
            groupBlock.className = 'module aligned';

            /* HEADER */

            const headerRow = document.createElement('div');
            headerRow.className = 'form-row';
            // headerRow.style.marginLeft = "5%";
            /* METHOD */
            const methodField = document.createElement('div');
            const methodLabel = document.createElement('label');
            methodLabel.textContent = 'Method';

            const methodSelect = document.createElement('select');
            methodSelect.className = 'vSelect';

            METHODS.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.text = m;
                methodSelect.appendChild(opt);
            });

            methodSelect.value = group.method;
            methodSelect.onchange = () => {
                group.method = methodSelect.value;
                updateHiddenField();
            };

            methodField.appendChild(methodLabel);
            methodField.appendChild(methodSelect);

            /* URL */
            const urlField = document.createElement('div');
            const urlLabel = document.createElement('label');
            urlLabel.textContent = 'URL Regex';

            const urlInput = document.createElement('input');
            urlInput.className = 'vTextField';
            urlInput.value = group.url_regix;

            urlInput.oninput = () => {
                group.url_regix = urlInput.value;
                updateHiddenField();
            };

            urlField.appendChild(urlLabel);
            urlField.appendChild(urlInput);

            /* PHASE */
            const phaseField = document.createElement('div');
            const phaseLabel = document.createElement('label');
            phaseLabel.textContent = 'Phase';

            const phaseSelect = document.createElement('select');
            phaseSelect.className = 'vSelect';

            PHASES.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p;
                opt.text = p;
                phaseSelect.appendChild(opt);
            });

            phaseSelect.value = group.phase;
            phaseSelect.onchange = () => {
                group.phase = phaseSelect.value;
                updateHiddenField();
            };

            phaseField.appendChild(phaseLabel);
            phaseField.appendChild(phaseSelect);

            headerRow.appendChild(methodField);
            headerRow.appendChild(urlField);
            headerRow.appendChild(phaseField);

            groupBlock.appendChild(headerRow);

            /* ================= STEPS ================= */

            group.steps.forEach((step, index) => {

                const block = document.createElement('div');
                block.className = 'inline-related';
                block.style.marginTop = '10px';
                block.style.marginLeft  = "5%"
                /* ACTION */
                const actionRow = document.createElement('div');
                actionRow.className = 'form-row';
                // actionRow.style.marginLeft  = "5%"
                const select = document.createElement('select');
                select.className = 'vSelect';

                Object.keys(ACTIONS).forEach(a => {
                    const opt = document.createElement('option');
                    opt.value = a;
                    opt.text = a;
                    select.appendChild(opt);
                });

                select.value = step.action;

                select.onchange = () => {
                    step.action = select.value;
                    step.params = { ...ACTIONS[step.action] };
                    render();
                    updateHiddenField();
                };

                actionRow.appendChild(select);
                block.appendChild(actionRow);

                /* LOG */
                const logRow = document.createElement('div');
                logRow.className = 'form-row';

                const logLabel = document.createElement('label');
                logLabel.textContent = 'Log';

                const logCheckbox = document.createElement('input');
                logCheckbox.type = 'checkbox';
                logCheckbox.checked = step.log;

                logCheckbox.onchange = () => {
                    step.log = logCheckbox.checked;
                    updateHiddenField();
                };

                logRow.appendChild(logLabel);
                logRow.appendChild(logCheckbox);

                block.appendChild(logRow);

                /* PARAMS */
                const paramsContainer = document.createElement('div');
                block.appendChild(paramsContainer);

                renderParams(step, paramsContainer);

                /* REMOVE STEP */
                const removeBtn = document.createElement('input');
                removeBtn.type = 'button';
                removeBtn.value = 'Remove Step';
                removeBtn.className = 'button';
                removeBtn.style.color = "white"
                removeBtn.style.backgroundColor = "#D32F2F"
                removeBtn.onclick = () => {
                    group.steps.splice(index, 1);
                    render();
                    updateHiddenField();
                };

                block.appendChild(removeBtn);

                groupBlock.appendChild(block);
            });

            /* ADD STEP */
            const addStepBtn = document.createElement('input');
            addStepBtn.type = 'button';
            addStepBtn.value = 'Add Step';
            addStepBtn.className = 'addlink';

            addStepBtn.onclick = () => {
                group.steps.push({
                    action: 'detect',
                    log: false,
                    params: {}
                });
                render();
            };

            groupBlock.appendChild(addStepBtn);

            /* REMOVE GROUP */
            const removeGroupBtn = document.createElement('input');
            removeGroupBtn.type = 'button';
            removeGroupBtn.value = 'Remove Group';
            removeGroupBtn.className = 'deletelink';
            removeGroupBtn.style.backgroundColor = "#D32F2F"
            removeGroupBtn.onclick = () => {
                groups.splice(gIndex, 1);
                render();
            };

            groupBlock.appendChild(removeGroupBtn);

            container.appendChild(groupBlock);
        });

        /* ADD GROUP */
        const addGroupBtn = document.createElement('input');
        addGroupBtn.type = 'button';
        addGroupBtn.value = 'Add Request Group';
        addGroupBtn.className = 'addlink';

        addGroupBtn.onclick = () => {
            groups.push({
                method: 'GET',
                url_regix: '',
                phase: 'request',
                steps: []
            });
            render();
        };

        container.appendChild(addGroupBtn);

        updateHiddenField();
    }

    render();

});
