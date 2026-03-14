document.addEventListener('DOMContentLoaded', function () {

    const notifyHidden = document.querySelector('input[name="notify_condition_json"]');
    const notifyVarsHidden = document.querySelector('input[name="notify_variables_json"]');

    if (!notifyHidden || !notifyVarsHidden) return;

    const formRow = notifyHidden.closest('.form-row');
    if (!formRow) return;

    const container = document.createElement('div');
    container.className = 'inline-related module';
    container.style.padding = '15px';
    container.style.marginTop = '20px';

    const title = document.createElement('h3');
    title.innerText = "Notification Settings";
    container.appendChild(title);
    
    let notifyCondition = {};
    let notifyVariables = [];

    try {
        notifyCondition = notifyHidden.value ? JSON.parse(notifyHidden.value) : {};
        notifyVariables = notifyVarsHidden.value ? JSON.parse(notifyVarsHidden.value) : [];
    } catch (e) {
        notifyCondition = {};
        notifyVariables = [];
    }

    /* ==============================
       ENABLE CHECKBOX
    ============================== */

    const enableWrapper = document.createElement('div');
    enableWrapper.className = 'form-row';

    const enableCheckbox = document.createElement('input');
    enableCheckbox.type = 'checkbox';
    enableCheckbox.checked = Object.keys(notifyCondition).length > 0;

    const enableLabel = document.createElement('label');
    enableLabel.innerText = " Enable Notification";

    enableWrapper.appendChild(enableCheckbox);
    enableWrapper.appendChild(enableLabel);
    container.appendChild(enableWrapper);


    /* ==============================
       TYPE + REGEX
    ============================== */

    const typeRow = document.createElement('div');
    typeRow.className = 'form-row';
    typeRow.style.marginTop = '10px';

    const typeSelect = document.createElement('select');
    typeSelect.className = 'vTextField';

    ['query', 'body_regex', 'headers'].forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.text = t;
        typeSelect.appendChild(opt);
    });

    const regexInput = document.createElement('input');
    regexInput.type = 'text';
    regexInput.placeholder = "Regex";
    regexInput.className = 'vTextField';
    regexInput.style.width = '40%';
    regexInput.style.marginLeft = '10px';

    if (notifyCondition.type) {
        typeSelect.value = notifyCondition.type;
        regexInput.value = notifyCondition.regex || '';
    }

    typeRow.appendChild(typeSelect);
    typeRow.appendChild(regexInput);
    container.appendChild(typeRow);


    /* ==============================
       SUCCESS TEXTBOX (NEW)
    ============================== */

    const successRow = document.createElement('div');
    successRow.className = 'form-row';
    successRow.style.marginTop = '10px';

    const successInput = document.createElement('input');
    successInput.type = 'text';
    successInput.className = 'vTextField';
    successInput.placeholder = "Success value";
    successInput.style.width = '50%';

    if (notifyCondition.success) {
        successInput.value = notifyCondition.success;
    }

    successRow.appendChild(successInput);
    container.appendChild(successRow);


    /* ==============================
       VARIABLES
    ============================== */

    const varsContainer = document.createElement('div');
    varsContainer.style.marginTop = '15px';
    container.appendChild(varsContainer);

    function renderVars() {
        varsContainer.innerHTML = '';

        notifyVariables.forEach((v, i) => {
            const row = document.createElement('div');
            row.className = 'form-row';

            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'vTextField';
            input.value = v;
            input.style.width = '40%';

            input.oninput = () => {
                notifyVariables[i] = input.value;
                updateHidden();
            };

            row.appendChild(input);
            varsContainer.appendChild(row);
        });
    }

    const addVarBtn = document.createElement('input');
    addVarBtn.type = 'button';
    addVarBtn.value = 'Add Variable';
    addVarBtn.className = 'default';
    addVarBtn.style.marginTop = '10px';

    addVarBtn.onclick = function () {
        notifyVariables.push('');
        renderVars();
        updateHidden();
    };

    container.appendChild(addVarBtn);


    /* ==============================
       UPDATE HIDDEN JSON
    ============================== */

    function updateHidden() {
        if (enableCheckbox.checked) {
            notifyCondition = {
                type: typeSelect.value,
                regex: regexInput.value,
                success: successInput.value
            };
        } else {
            notifyCondition = {};
        }

        notifyHidden.value = JSON.stringify(notifyCondition);
        notifyVarsHidden.value = JSON.stringify(notifyVariables);
    }

    enableCheckbox.onchange = updateHidden;
    typeSelect.onchange = updateHidden;
    regexInput.oninput = updateHidden;
    successInput.oninput = updateHidden;

    renderVars();
    updateHidden();

    formRow.after(container);
});
