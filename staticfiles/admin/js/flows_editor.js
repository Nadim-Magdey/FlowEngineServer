document.addEventListener('DOMContentLoaded', function () {

    const hiddenField = document.querySelector('input[name="flows_json"]');
    if (!hiddenField) return;

    const REGEX_TYPES = ['query', 'body', 'header'];

    const container = document.createElement('div');
    hiddenField.closest('.form-row').after(container);

    /* =========================
       ACTION DEFINITIONS
    ========================== */

    const ACTIONS = {
        detect: { method: 'GET', url_regix: '', phase: 'request' },

        edit_body: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            element_regix: '',
            new_value: ''
        },

        remove_body_element: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            element_regix: ''
        },

        edit_headers: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            value: ''
        },

        reject: { method: 'GET', url_regix: '', phase: 'request' },

        redirect: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            destination: ''
        },

        forward: { method: 'GET', url_regix: '', phase: 'request' },

        change_body: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            content: ''
        },

        extract_header: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            header_key: ''
        },

        remove_header: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            header_key: ''
        },

        extract_body_element: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            element_regix: '',
            return_name: ''
        },

        extract_query: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            query_key: ''
        },

        edit_query: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            query_key: '',
            new_value: ''
        },

        remove_query: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            query_key: ''
        },

        applyFunction: { function: '' },

        APGMastercard : {
            return_name: '',
        },
        CybersourceFlexV2: {
            return_name: '',   
        },

        change_status_code: {
            method: 'GET',
            url_regix: '',
            phase: 'response',
            status_code: 200
        },

        insertHeaderKey: {
            method: 'GET',
            url_regix: '',
            phase: 'response',
            header_key: '',
            header_value: ''
        },

        customDetect: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            regix_type: 'query',
            value: ''
        },

        editUrlParam: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            param_regix: '',
            new_value: ''
        },

        removeUrlParam: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            param_regix: ''
        },

        extractURLParams: {
            method: 'GET',
            url_regix: '',
            phase: 'request',
            param_regix: '',
            return_name: ''
        }
    };

    const METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
    const PHASES = ['request', 'response'];
    const ENCRYPTORS = ['CybersourceFlexV2', 'APGMastercard'];

    const VARIABLE_ALLOWED = [
        'value',
        'new_value',
        'content',
        'destination'

    ];

    let steps = [];

    try {
        steps = hiddenField.value
            ? JSON.parse(hiddenField.value).steps || []
            : [];
    } catch {
        steps = [];
    }

    /* =========================
       VALUE NORMALIZATION
    ========================== */

    function normalizeValue(v) {

        if (typeof v === "object" && v !== null) {

            if (v.type === "variable") {

                let val = v.value || "";

                if (!val.startsWith("{{"))
                    val = "{{" + val;

                if (!val.endsWith("}}"))
                    val = val + "}}";

                return val;
            }

            return v.value || "";
        }

        return v;
    }

    function normalizeSteps() {

        return steps.map(step => {

            const params = { ...step.params };

            Object.keys(params).forEach(k => {
                params[k] = normalizeValue(params[k]);
            });

            return {
                action: step.action,
                log: step.log,
                params: params
            };
        });
    }

    function updateHiddenField() {

        hiddenField.value = JSON.stringify({
            steps: normalizeSteps()
        });
    }

    /* =========================
       PARAM RENDERING
    ========================== */

    function renderParams(step, container) {

        container.innerHTML = '';

        const template = ACTIONS[step.action];

        Object.keys(template).forEach(key => {

            const row = document.createElement('div');
            row.className = 'form-row';

            const label = document.createElement('label');
            label.textContent =
                key.charAt(0).toUpperCase() + key.slice(1);

            label.style.display = 'block';

            let input;

            /* encryption select */

            // if (step.action === 'encryption' && key === 'encryptor') {

            //     input = document.createElement('select');

            //     ENCRYPTORS.forEach(enc => {

            //         const opt = document.createElement('option');

            //         opt.value = enc;
            //         opt.text = enc;

            //         input.appendChild(opt);
            //     });

            //     input.value =
            //         step.params.encryptor || template.encryptor;

            //     input.onchange = () => {

            //         step.params.encryptor = input.value;
            //         updateHiddenField();
            //     };

            //     row.appendChild(label);
            //     row.appendChild(input);
            //     container.appendChild(row);
            //     return;
            // }

            /* method */

            if (key === 'method') {

                input = document.createElement('select');

                METHODS.forEach(m => {

                    const opt = document.createElement('option');

                    opt.value = m;
                    opt.text = m;

                    input.appendChild(opt);
                });

                input.value =
                    step.params[key] || template[key];

                input.onchange = () => {

                    step.params[key] = input.value;
                    updateHiddenField();
                };

                row.appendChild(label);
                row.appendChild(input);
                container.appendChild(row);
                return;
            }

            /* phase */

            if (key === 'phase') {

                input = document.createElement('select');

                PHASES.forEach(p => {

                    const opt = document.createElement('option');

                    opt.value = p;
                    opt.text = p;

                    input.appendChild(opt);
                });

                input.value =
                    step.params[key] || template[key];

                input.onchange = () => {

                    step.params[key] = input.value;
                    updateHiddenField();
                };

                row.appendChild(label);
                row.appendChild(input);
                container.appendChild(row);
                return;
            }

            /* regex type */

            if (key === 'regix_type') {

                input = document.createElement('select');

                REGEX_TYPES.forEach(t => {

                    const opt = document.createElement('option');

                    opt.value = t;
                    opt.text = t;

                    input.appendChild(opt);
                });

                input.value =
                    step.params[key] || template[key];

                input.onchange = () => {

                    step.params[key] = input.value;
                    updateHiddenField();
                };

                row.appendChild(label);
                row.appendChild(input);
                container.appendChild(row);
                return;
            }

            /* variable selector */

            if (VARIABLE_ALLOWED.includes(key) &&
                step.action !== 'customDetect') {

                const typeSelect =
                    document.createElement('select');

                typeSelect.innerHTML =
                    `<option value="fixed">Fixed</option>
                     <option value="variable">Variable</option>`;

                const valueInput =
                    document.createElement('input');

                valueInput.type = 'text';
                valueInput.className = 'vTextField';
                valueInput.style.width = '50%';

                let paramValue =
                    step.params[key] ?? template[key];

                if (typeof paramValue === 'object') {

                    typeSelect.value = paramValue.type;
                    valueInput.value = paramValue.value;

                } else {

                    typeSelect.value = 'fixed';
                    valueInput.value = paramValue;
                }

                function updateParam() {

                    step.params[key] = {
                        type: typeSelect.value,
                        value: valueInput.value
                    };

                    updateHiddenField();
                }

                typeSelect.onchange = updateParam;
                valueInput.oninput = updateParam;

                row.appendChild(label);
                row.appendChild(typeSelect);
                row.appendChild(valueInput);

                container.appendChild(row);
                return;
            }

            /* normal input */

            input = document.createElement('input');

            input.type = 'text';
            input.className = 'vTextField';
            input.style.width = '50%';

            input.value =
                step.params[key] ?? template[key];

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

        steps.forEach((step, index) => {

            if (step.log === undefined)
                step.log = false;

            const block = document.createElement('div');

            block.className = 'inline-related module';

            block.style.padding = '10px';
            block.style.marginBottom = '10px';

            const actionRow = document.createElement('div');
            actionRow.className = 'form-row';

            const label = document.createElement('label');
            label.textContent = 'Action';

            const select = document.createElement('select');

            Object.keys(ACTIONS).forEach(a => {

                const opt =
                    document.createElement('option');

                opt.value = a;
                opt.text = a;

                select.appendChild(opt);
            });

            select.value = step.action;

            select.onchange = () => {

                step.action = select.value;

                step.params = {
                    ...ACTIONS[step.action]
                };

                render();
                updateHiddenField();
            };

            actionRow.appendChild(label);
            actionRow.appendChild(select);

            block.appendChild(actionRow);

            /* log checkbox */

            const logRow = document.createElement('div');

            const logLabel = document.createElement('label');

            logLabel.textContent = 'Log Step';

            const logCheckbox =
                document.createElement('input');

            logCheckbox.type = 'checkbox';

            logCheckbox.checked = step.log;

            logCheckbox.onchange = () => {

                step.log = logCheckbox.checked;
                updateHiddenField();
            };

            logRow.appendChild(logLabel);
            logRow.appendChild(logCheckbox);

            block.appendChild(logRow);

            const paramsContainer =
                document.createElement('div');

            paramsContainer.style.marginTop = '5px';

            block.appendChild(paramsContainer);

            renderParams(step, paramsContainer);

            const removeBtn =
                document.createElement('input');

            removeBtn.type = 'button';
            removeBtn.value = 'Remove';
            removeBtn.className = 'default';

            removeBtn.onclick = () => {

                steps.splice(index, 1);

                render();
                updateHiddenField();
            };

            block.appendChild(removeBtn);

            container.appendChild(block);
        });

        /* add step */

        const addBtn = document.createElement('input');

        addBtn.type = 'button';
        addBtn.value = 'Add Step';
        addBtn.className = 'default';

        addBtn.onclick = () => {

            steps.push({
                action: 'detect',
                log: false,
                params: { ...ACTIONS.detect }
            });

            render();
            updateHiddenField();
        };

        container.appendChild(addBtn);

        updateHiddenField();
    }

    render();

});
