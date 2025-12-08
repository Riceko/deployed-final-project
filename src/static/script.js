let stepHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    // If we're on the grid page (has ship-grid), initialize grid handlers
    if (document.getElementById('ship-grid')) {
        fetchGridState();
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                nextStep();
            }
        });
    }

    // If we're on the start/upload page (has uploadForm), initialize its handlers
    if (document.getElementById('uploadForm')) {
        initStartPage();
    }
});

// Initialize start page upload form behavior (moved from inline start.html script)
function initStartPage() {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const submitBtn = document.getElementById('submitBtn');
    const errorMsg = document.getElementById('errorMsg');
    const uploadForm = document.getElementById('uploadForm');

    if (!fileInput || !fileName || !submitBtn || !errorMsg || !uploadForm) return;

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            if (!file.name.endsWith('.txt')) {
                errorMsg.textContent = 'Error: Please select a .txt file';
                fileName.textContent = 'No file selected';
                submitBtn.disabled = true;
                return;
            }
            errorMsg.textContent = '';
            fileName.innerHTML = `
                <div class="flex items-center justify-center space-x-2">
                    <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <span class="text-green-400 font-semibold">${file.name}</span>
                </div>
            `;
            submitBtn.disabled = false;
        } else {
            fileName.textContent = 'No file selected';
            submitBtn.disabled = true;
        }
    });

    uploadForm.addEventListener('submit', function(e) {
        if (!fileInput.files || !fileInput.files[0]) {
            e.preventDefault();
            errorMsg.textContent = 'Error: Please select a file first';
        }
    });
}

async function fetchGridState() {
    try {
        const response = await fetch('/api/current_grid');
        const data = await response.json(); //data is the main way to get all the info about the grid
        renderSystem(data);
        StepHistory(data);
        const timeElement = document.getElementById('time-display');
        timeElement.innerText = data.total_time;
        const steps = document.getElementById('steps-display');
        steps.innerText = data.num_steps;
    } catch (error) {
        console.error("Error loading grid:", error);
    }
}

async function nextStep() {
    try {
        const response = await fetch('/api/next_grid', { method: 'POST' });
        const data = await response.json();
        
        StepHistory(data);
        renderSystem(data);
    } catch (error) {
        console.error("Error advancing step:", error);
    }
}

function renderStepLog() {
    const container = document.getElementById('step-log');
    if (!container) 
        return;

    container.innerHTML = '';

    if (stepHistory.length === 0) {
        container.innerHTML = `<div class="text-gray-400 text-center text-sm py-4">No steps taken yet. Press "Next Step" to begin.</div>`;
        return;
    }

    stepHistory.forEach((msg) => {
        const item = document.createElement('div');
        item.className = 'step-log-item';
        item.innerHTML = msg;
        container.appendChild(item);
    });

    container.scrollTop = container.scrollHeight;
}
function StepHistory(data) {
    stepHistory = [];
    if (!data || !data.steps || data.steps.length === 0) {
        renderStepLog();
        return;
    }
    let completedCount = data.current_step_num + 1;
    if(completedCount > data.steps.length) {
        completedCount = data.steps.length;
    }
    if (data.all_done) {
        completedCount = data.steps.length;
    }

    for (let idx = 0; idx < completedCount; idx++) {
        const step = data.steps[idx];
        const costs = data.costs[idx];
        const time = String(costs).padStart(1, '0');
        const fromY = String(step[0]).padStart(2, '0');
        const fromX = String(step[1]).padStart(2, '0');
        const toY = String(step[2]).padStart(2, '0');
        const toX = String(step[3]).padStart(2, '0');
        const fromLabel = (fromY === '09' && fromX === '01') ? 'park' : `[${fromY},${fromX}]`;
        const toLabel = (toY === '09' && toX === '01') ? 'park' : `[${toY},${toX}]`;
        

        const isMove = idx % 2 === 1; //moving a container are odd
        const stepNum = idx + 1;
        const totalSteps = data.num_steps;
        const fromSpan = `<span style="color: #2ecc71; font-weight: bold;">${fromLabel}</span>`;
        const toSpan = `<span style="color: #e74c3c; font-weight: bold;">${toLabel}</span>`;

        let message = '';
        if (isMove) {
             //message = `${stepNum} of ${totalSteps}: Move from ${fromSpan} to ${toSpan}`;
            message = `${stepNum} of ${totalSteps}: Move from ${fromSpan} to ${toSpan}, ${time} minutes`;
        } else {
            //message = `${stepNum} of ${totalSteps}: Move crane from ${fromSpan} to ${toSpan}`;
            message = `${stepNum} of ${totalSteps}: Move crane from ${fromSpan} to ${toSpan}, ${time} minutes`;
        }

        if (stepHistory.length === 0 || stepHistory[stepHistory.length - 1] !== message) {
            stepHistory.push(message);
        }
    }
    if(data.all_done)
    {
        const filename = data.file_name;
        const donemessage =`<span >Done! ${filename} was written to Desktop!</span>`
        stepHistory.push(donemessage);
    }

    renderStepLog();
}
//create the grid in its entirety
function renderSystem(data) {
    const statusText = document.getElementById('status-text');
    if (data.all_done) {
        statusText.innerText = "OPERATION DONE";
        statusText.style.color = "#2ecc71";
    } else {
        statusText.innerText = `Step ${data.current_step_num} / ${data.num_steps}`;
        statusText.style.color = "";
    }
    
    const gridMap = {};
    data.grid.forEach(row => {
        const key = `${parseInt(row[0])},${parseInt(row[1])}`;
        gridMap[key] = row;
    });
    
    const shipContainer = document.getElementById('ship-grid');
    shipContainer.innerHTML = '';
    for (let y = 8; y >= 1; y--) {
        for (let x = 1; x <= 12; x++) {
            const cellData = gridMap[`${y},${x}`];
            const cellDiv = createCell(cellData, y, x);
            shipContainer.appendChild(cellDiv);
        }
    }

    const bufferContainer = document.getElementById('buffer-grid');
    bufferContainer.innerHTML = '';
    
    const cellData = gridMap[`9,1`]; 
    const cellDiv = createCell(cellData, 9, 1);
    if (data.park_cell) {
        cellDiv.classList.add(`highlight-${data.park_cell}`);
    }
    
    bufferContainer.appendChild(cellDiv);
}
//look at each Cell and determine the information
function createCell(cellData, y, x) {
    const div = document.createElement('div');
    div.classList.add('cell');
    if (!cellData) {
        div.classList.add('unused');
        div.innerText = " ";
        return div;
    }
    const weight = cellData[2];
    const name = cellData[3];
    const color = cellData[4]; 
    if (name === "NAN") {
        div.classList.add('nan');
        div.innerText = "NAN";
    } else if (name === "UNUSED") {
        div.classList.add('unused');
    } else {
        div.classList.add('container');
        const displayWeight = parseInt(weight, 10) || weight;
        div.innerHTML = `<span>${name.substring(0, 5)}</span><small>${displayWeight}</small>`;
    }

    if (color === 'red') {
        div.classList.add('highlight-red');
    } else if (color === 'green') {
        div.classList.add('highlight-green');
    }

    return div;
}

function downloadManifest() {
    const updateStatus = document.getElementById('update-status');
    window.location.href = "/download_manifest";
    if(updateStatus) {
        updateStatus.innerText = "Done! file was written to the desktop";
    }
}

function closeApp() {
    window.location.href = "/close";
}

function goBack() {
    window.location.href = "/";
}