document.addEventListener('DOMContentLoaded', function () {
    const hidden = document.querySelector('input[name="inputs_json"]');
    if (!hidden) return;

    // Create editor container
    const container = document.createElement('div');
    container.id = 'inputs-editor';
    container.className = 'flow-editor';
    hidden.closest('.form-row').after(container);

    // Initial state
    let state = { inputs: [] };
    try {
        state = JSON.parse(hidden.value || '{"inputs": []}');
    } catch (e) {
        console.warn('Invalid inputs JSON, resetting');
    }

    function render() {
        container.innerHTML = `
            <h2>Inputs</h2>
            <div class="flow-steps"></div>
            <div class="submit-row">
                <button type="button" class="button default add-input">
                    + Add Input
                </button>
            </div>
        `;

        const stepsEl = container.querySelector('.flow-steps');

        state.inputs.forEach((input, index) => {
            const step = document.createElement('div');
            step.className = 'flow-step';

            step.innerHTML = `
                <div class="flow-step-header">
                    <strong>#${index + 1}</strong>

                    <input
                        type="text"
                        class="vTextField"
                        placeholder="name"
                        value="${input.name || ''}"
                        style="width: 140px;"
                    >

                    <select class="vSelect">
                        <option value="text" ${input.type === 'text' ? 'selected' : ''}>Text</option>
                        <option value="integer" ${input.type === 'integer' ? 'selected' : ''}>Integer</option>
                    </select>

                    <a href="#" class="deletelink delete-input">Remove</a>
                </div>

                <div class="flow-step-body">
                    ${renderParams(input)}
                </div>
            `;

            // Handlers
            step.querySelector('.delete-input').onclick = e => {
                e.preventDefault();
                state.inputs.splice(index, 1);
                sync();
            };

            step.querySelector('input').oninput = e => {
                input.name = e.target.value;
                sync(false);
            };

            step.querySelector('select').onchange = e => {
                input.type = e.target.value;
                delete input.default;
                delete input.constraints;
                sync();
            };

            stepsEl.appendChild(step);
        });

        container.querySelector('.add-input').onclick = () => {
            state.inputs.push({ name: '', type: 'text' });
            sync();
        };
    }

    function renderParams(input) {
        if (input.type === 'integer') {
            return `
                <fieldset class="module aligned">
                    <div class="form-row">
                        <label>Default</label>
                        <input type="number" data-key="default" value="${input.default ?? ''}">
                    </div>
                    <div class="form-row">
                        <label>Min</label>
                        <input type="number" data-key="min" value="${input.constraints?.min ?? ''}">
                    </div>
                    <div class="form-row">
                        <label>Max</label>
                        <input type="number" data-key="max" value="${input.constraints?.max ?? ''}">
                    </div>
                </fieldset>
            `;
        }

        return `
            <fieldset class="module aligned">
                <div class="form-row">
                    <label>Default</label>
                    <input type="text" data-key="default" value="${input.default ?? ''}">
                </div>
                <div class="form-row">
                    <label>Min Length</label>
                    <input type="number" data-key="minLength" value="${input.constraints?.minLength ?? ''}">
                </div>
                <div class="form-row">
                    <label>Max Length</label>
                    <input type="number" data-key="maxLength" value="${input.constraints?.maxLength ?? ''}">
                </div>
            </fieldset>
        `;
    }

    function sync(rerender = true) {
        const bodies = container.querySelectorAll('.flow-step-body');

        state.inputs.forEach((input, idx) => {
            const body = bodies[idx];
            if (!body) return;

            body.querySelectorAll('[data-key]').forEach(el => {
                const key = el.dataset.key;
                const value = el.value;

                if (key === 'default') {
                    input.default = value === '' ? undefined : value;
                } else {
                    input.constraints = input.constraints || {};
                    input.constraints[key] =
                        value === '' ? undefined : Number(value);
                }
            });

            if (input.constraints && Object.keys(input.constraints).length === 0) {
                delete input.constraints;
            }
        });

        hidden.value = JSON.stringify(state, null, 2);
        if (rerender) render();
    }

    render();
});
