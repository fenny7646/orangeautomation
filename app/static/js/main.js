document.addEventListener('DOMContentLoaded', () => {
    try {
        initTheme();
    } catch (e) {
        console.error('Failed to initialize theme:', e);
    }

    try {
        initEmployeeForm();
    } catch (e) {
        console.error('Failed to initialize employee form:', e);
    }
});

function safeCreateIcons() {
    try {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    } catch (e) {
        console.warn('Lucide icon rendering notice:', e);
    }
}

function safeStorageGet(key, fallback = null) {
    try {
        return localStorage.getItem(key) || fallback;
    } catch (e) {
        console.warn(`LocalStorage read blocked for key '${key}':`, e);
        return fallback;
    }
}

function safeStorageSet(key, value) {
    try {
        localStorage.setItem(key, value);
    } catch (e) {
        console.warn(`LocalStorage write blocked for key '${key}':`, e);
    }
}

function initTheme() {
    const themeBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    const savedTheme = safeStorageGet('hub-theme', 'dark');
    if (html) html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            try {
                const currentTheme = (html && html.getAttribute('data-theme')) || 'dark';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                if (html) html.setAttribute('data-theme', newTheme);
                safeStorageSet('hub-theme', newTheme);
                updateThemeIcon(newTheme);
                showToast(`Switched to ${newTheme} mode`);
            } catch (err) {
                console.error('Error toggling theme:', err);
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        try {
            themeIcon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
            safeCreateIcons();
        } catch (e) {
            console.warn('Error updating theme icon:', e);
        }
    }
}

function initEmployeeForm() {
    const form = document.getElementById('employeeForm');
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const employeeIdInput = document.getElementById('employeeId');
    const btnFillSample = document.getElementById('btnFillSample');
    const btnClearLogs = document.getElementById('btnClearLogs');
    const btnRefreshCsv = document.getElementById('btnRefreshCsv');
    const terminalOutput = document.getElementById('terminalOutput');
    const csvTableBody = document.getElementById('csvTableBody');

    const orangeUserInput = document.getElementById('orangeUsername');
    const orangePassInput = document.getElementById('orangePassword');
    const usernameErrorMsg = document.getElementById('usernameErrorMsg');
    const passwordErrorMsg = document.getElementById('passwordErrorMsg');
    const credentialAlert = document.getElementById('credentialAlert');
    const credentialAlertMessage = document.getElementById('credentialAlertMessage');
    const btnCloseAlert = document.getElementById('btnCloseAlert');
    const taskStatusBox = document.getElementById('taskStatusBox');
    const taskStatusIcon = document.getElementById('taskStatusIcon');
    const taskStatusBadge = document.getElementById('taskStatusBadge');
    const taskStatusTime = document.getElementById('taskStatusTime');
    const taskStatusText = document.getElementById('taskStatusText');
    const btnCloseStatusBox = document.getElementById('btnCloseStatusBox');
    const btnRunAutomation = document.getElementById('btnRunAutomation');

    async function loadCsvRecords() {
        if (!csvTableBody) return;
        try {
            const res = await fetch('/api/csv-records');
            if (res.ok) {
                const data = await res.json();
                if (data.records && Array.isArray(data.records) && data.records.length > 0) {
                    csvTableBody.innerHTML = '';
                    data.records.forEach((rec, idx) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><strong>#${idx + 1}</strong></td>
                            <td><code>${escapeHtml(rec.id || '-')}</code></td>
                            <td>${escapeHtml(rec.first_name || '-')}</td>
                            <td>${escapeHtml(rec.last_name || '-')}</td>
                            <td><span class="badge get">${escapeHtml(rec.status || 'Success')}</span></td>
                        `;
                        csvTableBody.appendChild(row);
                    });
                } else {
                    csvTableBody.innerHTML = `
                        <tr id="emptyCsvRow">
                            <td colspan="5" class="text-center text-muted">No CSV records found. Run the automation above to save records to CSV.</td>
                        </tr>
                    `;
                }
            }
        } catch (err) {
            console.warn('Error loading CSV records:', err);
        }
    }

    loadCsvRecords();

    if (btnRefreshCsv) {
        btnRefreshCsv.addEventListener('click', async () => {
            await loadCsvRecords();
            showToast('CSV records refreshed!');
        });
    }

    function setTaskStatus(status, message) {
        try {
            if (!taskStatusBox) return;

            taskStatusBox.style.display = 'flex';
            taskStatusBox.className = 'task-status-banner status-' + status;

            if (taskStatusTime) {
                taskStatusTime.textContent = new Date().toLocaleTimeString();
            }

            if (status === 'running') {
                if (taskStatusIcon) taskStatusIcon.innerHTML = `<i data-lucide="loader" class="spin-icon"></i>`;
                if (taskStatusBadge) {
                    taskStatusBadge.textContent = 'Running';
                }
                if (taskStatusText) taskStatusText.textContent = message || 'Executing Playwright automation workflow in OrangeHRM...';
            } else if (status === 'success') {
                if (taskStatusIcon) taskStatusIcon.innerHTML = `<i data-lucide="check-circle"></i>`;
                if (taskStatusBadge) {
                    taskStatusBadge.textContent = 'Success';
                }
                if (taskStatusText) taskStatusText.textContent = message || 'Task is Success: OrangeHRM automation completed successfully!';
            } else if (status === 'failed') {
                if (taskStatusIcon) taskStatusIcon.innerHTML = `<i data-lucide="x-circle"></i>`;
                if (taskStatusBadge) {
                    taskStatusBadge.textContent = 'Failed';
                }
                if (taskStatusText) taskStatusText.textContent = message || 'Task is Failed';
            }

            safeCreateIcons();
        } catch (e) {
            console.error('Error setting task status:', e);
        }
    }

    function hideTaskStatus() {
        if (taskStatusBox) {
            taskStatusBox.style.display = 'none';
        }
    }

    if (btnCloseStatusBox) {
        btnCloseStatusBox.addEventListener('click', () => {
            hideTaskStatus();
        });
    }

    function showTemplateError(message) {
        if (credentialAlert) {
            if (credentialAlertMessage) {
                credentialAlertMessage.textContent = message || 'Username or password is wrong';
            }
            credentialAlert.style.display = 'flex';
            safeCreateIcons();
        }
    }

    function hideTemplateError() {
        if (credentialAlert) {
            credentialAlert.style.display = 'none';
        }
        if (orangeUserInput) {
            orangeUserInput.classList.remove('is-invalid');
        }
        if (orangePassInput) {
            orangePassInput.classList.remove('is-invalid');
        }
        if (usernameErrorMsg) {
            usernameErrorMsg.style.display = 'none';
        }
        if (passwordErrorMsg) {
            passwordErrorMsg.style.display = 'none';
        }
    }

    if (btnCloseAlert) {
        btnCloseAlert.addEventListener('click', () => {
            hideTemplateError();
        });
    }

    if (btnFillSample) {
        btnFillSample.addEventListener('click', () => {
            try {
                const samples = [
                    { first: 'Alexander', last: 'Wright', id: 'EMP-' + Math.floor(1000 + Math.random() * 9000) },
                    { first: 'Sophia', last: 'Martinez', id: 'EMP-' + Math.floor(1000 + Math.random() * 9000) },
                    { first: 'Liam', last: 'Johnson', id: 'EMP-' + Math.floor(1000 + Math.random() * 9000) },
                    { first: 'Emma', last: 'Davis', id: 'EMP-' + Math.floor(1000 + Math.random() * 9000) },
                    { first: 'Lucas', last: 'Taylor', id: 'EMP-' + Math.floor(1000 + Math.random() * 9000) }
                ];

                const randomSample = samples[Math.floor(Math.random() * samples.length)];
                if (firstNameInput) firstNameInput.value = randomSample.first;
                if (lastNameInput) lastNameInput.value = randomSample.last;
                if (employeeIdInput) employeeIdInput.value = randomSample.id;

                showToast('Sample data filled!');
            } catch (err) {
                console.error('Error auto-filling sample:', err);
            }
        });
    }

    if (btnClearLogs && terminalOutput) {
        btnClearLogs.addEventListener('click', () => {
            try {
                terminalOutput.innerHTML = `
                    <div class="terminal-line system-line">
                        <span class="log-time">[System]</span> Terminal logs cleared.
                    </div>
                `;
                showToast('Console mirror cleared');
            } catch (err) {
                console.error('Error clearing terminal logs:', err);
            }
        });
    }

    if (orangeUserInput) {
        orangeUserInput.addEventListener('input', () => {
            try {
                orangeUserInput.classList.remove('is-invalid');
                if (usernameErrorMsg) usernameErrorMsg.style.display = 'none';
                if (!orangePassInput || !orangePassInput.classList.contains('is-invalid')) {
                    hideTemplateError();
                }
            } catch (e) {}
        });
    }

    if (orangePassInput) {
        orangePassInput.addEventListener('input', () => {
            try {
                orangePassInput.classList.remove('is-invalid');
                if (passwordErrorMsg) passwordErrorMsg.style.display = 'none';
                if (!orangeUserInput || !orangeUserInput.classList.contains('is-invalid')) {
                    hideTemplateError();
                }
            } catch (e) {}
        });
    }

    if (btnRunAutomation) {
        btnRunAutomation.addEventListener('click', async () => {
            try {
                const firstName = (firstNameInput && firstNameInput.value.trim()) || 'Automation';
                const lastName = (lastNameInput && lastNameInput.value.trim()) || 'Tester';
                const employeeId = (employeeIdInput && employeeIdInput.value.trim()) || ('EMP-' + Math.floor(1000 + Math.random() * 9000));
                const username = orangeUserInput ? orangeUserInput.value.trim() : '';
                const password = orangePassInput ? orangePassInput.value.trim() : '';

                if (!username || !password) {
                    if (!username) {
                        if (orangeUserInput) orangeUserInput.classList.add('is-invalid');
                        if (usernameErrorMsg) usernameErrorMsg.style.display = 'block';
                    } else {
                        if (orangeUserInput) orangeUserInput.classList.remove('is-invalid');
                        if (usernameErrorMsg) usernameErrorMsg.style.display = 'none';
                    }

                    if (!password) {
                        if (orangePassInput) orangePassInput.classList.add('is-invalid');
                        if (passwordErrorMsg) passwordErrorMsg.style.display = 'block';
                    } else {
                        if (orangePassInput) orangePassInput.classList.remove('is-invalid');
                        if (passwordErrorMsg) passwordErrorMsg.style.display = 'none';
                    }

                    const errorMsg = 'Username and password not received';
                    showTemplateError(errorMsg);
                    setTaskStatus('failed', `Task is Failed: ${errorMsg}`);
                    appendAutomationTerminalLog(`[ERROR] ${errorMsg}: Please enter username and password.`);
                    showToast(`Task is Failed: ${errorMsg}`);
                    return;
                }

                hideTemplateError();

                if (firstNameInput && !firstNameInput.value) firstNameInput.value = firstName;
                if (lastNameInput && !lastNameInput.value) lastNameInput.value = lastName;
                if (employeeIdInput && !employeeIdInput.value) employeeIdInput.value = employeeId;

                btnRunAutomation.disabled = true;
                btnRunAutomation.innerHTML = `<i data-lucide="loader" class="spin-icon"></i> <span>Running Automation...</span>`;
                safeCreateIcons();

                setTaskStatus('running', `Awaiting Playwright automation for user "${username}" & Employee "${firstName} ${lastName}"...`);
                appendAutomationTerminalLog(`[START] Triggering OrangeHRM Playwright automation with user: "${username}" & Employee: "${firstName} ${lastName}"...`);
                showToast('Launching Playwright automation...');

                const showBrowserToggle = document.getElementById('showBrowserToggle');
                const isHeadless = showBrowserToggle ? !showBrowserToggle.checked : false;

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 180000);

                try {
                    const response = await fetch('/api/run-automation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: username,
                            password: password,
                            first_name: firstName,
                            last_name: lastName,
                            employee_id: employeeId,
                            headless: isHeadless
                        }),
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);

                    let data;
                    try {
                        data = await response.json();
                    } catch (parseErr) {
                        data = { success: false, error: `Invalid server response format (${response.status})` };
                    }

                    if (data.logs && Array.isArray(data.logs)) {
                        data.logs.forEach(log => appendAutomationTerminalLog(log));
                    }

                    if (response.ok && data.success) {
                        hideTemplateError();
                        const durationSec = data.duration_seconds || '0';
                        const successMessage = `Task is Success: OrangeHRM workflow completed in ${durationSec}s. Employee "${firstName} ${lastName}" registered.`;
                        setTaskStatus('success', successMessage);
                        appendAutomationTerminalLog(`[SUCCESS] Flow completed in ${durationSec}s.`);
                        if (data.csv_file) {
                            appendAutomationTerminalLog(`[CSV] Data stored in CSV file: ${data.csv_file}`);
                        }

                        await loadCsvRecords();

                    } else {
                        const failReason = data.error || (data.message ? data.message : 'Automation encountered an error.');
                        const failMessage = `Task is Failed: ${failReason}`;
                        setTaskStatus('failed', failMessage);
                        showTemplateError(failReason);
                        if (orangeUserInput) orangeUserInput.classList.add('is-invalid');
                        if (orangePassInput) orangePassInput.classList.add('is-invalid');
                        showToast(`Task is Failed!`);
                        appendAutomationTerminalLog(`[ERROR] ${failReason}`);
                    }
                } catch (fetchErr) {
                    clearTimeout(timeoutId);
                    const isAbort = fetchErr.name === 'AbortError';
                    const failReason = isAbort ? 'Request timed out after 180 seconds' : (fetchErr.message || 'Network connection failed');
                    const failMessage = `Task is Failed: ${failReason}`;
                    setTaskStatus('failed', failMessage);
                    showTemplateError(failReason);
                    showToast(`Task is Failed!`);
                    appendAutomationTerminalLog(`[FAILED] Request error: ${failReason}`);
                }
            } catch (handlerErr) {
                console.error('Unhandled error in automation button handler:', handlerErr);
                setTaskStatus('failed', `Task is Failed: Unexpected error (${handlerErr.message})`);
            } finally {
                if (btnRunAutomation) {
                    btnRunAutomation.disabled = false;
                    btnRunAutomation.innerHTML = `<i data-lucide="play-circle"></i> <span>Run Automation</span>`;
                    safeCreateIcons();
                }
            }
        });
    }

    if (form) {
        form.addEventListener('reset', () => {
            hideTemplateError();
            hideTaskStatus();
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const firstName = firstNameInput ? firstNameInput.value.trim() : '';
                const lastName = lastNameInput ? lastNameInput.value.trim() : '';
                const employeeId = employeeIdInput ? employeeIdInput.value.trim() : '';

                if (!firstName || !lastName || !employeeId) {
                    showToast('Please fill all fields before submitting!');
                    return;
                }

                const payload = {
                    first_name: firstName,
                    last_name: lastName,
                    employee_id: employeeId
                };

                try {
                    console.group('%c🚀 [EMPLOYEE SUBMISSION]', 'color: #06b6d4; font-weight: bold; font-size: 13px;');
                    console.log('%cFirst Name  :', 'color: #818cf8; font-weight: bold;', firstName);
                    console.log('%cLast Name   :', 'color: #818cf8; font-weight: bold;', lastName);
                    console.log('%cEmployee ID :', 'color: #818cf8; font-weight: bold;', employeeId);
                    console.log('Payload Object:', payload);
                    console.log('Timestamp   :', new Date().toISOString());
                    console.groupEnd();
                } catch (ce) {}

                appendTerminalLog(payload);

                try {
                    const response = await fetch('/api/employee', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (response.ok) {
                        const resData = await response.json();
                        console.log('%c[Server Response]:', 'color: #10b981;', resData);
                    }
                } catch (err) {
                    console.warn('[Server Logging Notice]:', err.message);
                }

                showToast(`Employee "${firstName} ${lastName}" printed to console!`);
                form.reset();
                hideTemplateError();
                if (firstNameInput) firstNameInput.focus();

            } catch (submitErr) {
                console.error('Error during form submission:', submitErr);
                showToast('Failed to submit form: ' + submitErr.message);
            }
        });
    }
}

function appendAutomationTerminalLog(message) {
    try {
        const terminalOutput = document.getElementById('terminalOutput');
        if (!terminalOutput) return;

        const placeholder = terminalOutput.querySelector('.placeholder-line');
        if (placeholder) placeholder.remove();

        const logItem = document.createElement('div');
        logItem.className = 'terminal-line';
        logItem.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> <span style="color: #38bdf8;">${escapeHtml(message)}</span>`;
        terminalOutput.appendChild(logItem);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    } catch (e) {
        console.warn('Error appending automation log:', e);
    }
}

function appendTerminalLog(data) {
    try {
        const terminalOutput = document.getElementById('terminalOutput');
        if (!terminalOutput) return;

        const placeholder = terminalOutput.querySelector('.placeholder-line');
        if (placeholder) placeholder.remove();

        const timestamp = new Date().toLocaleTimeString();
        const logItem = document.createElement('div');
        logItem.className = 'terminal-line log-entry';
        logItem.innerHTML = `
            <span class="log-time">[${timestamp}]</span>
            <span class="log-tag">CONSOLE.LOG:</span>
            <span class="log-json">{ "first_name": "<span class="hl-str">${escapeHtml(data.first_name || '')}</span>", "last_name": "<span class="hl-str">${escapeHtml(data.last_name || '')}</span>", "employee_id": "<span class="hl-num">${escapeHtml(data.employee_id || '')}</span>" }</span>
        `;

        terminalOutput.appendChild(logItem);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    } catch (e) {
        console.warn('Error appending terminal log:', e);
    }
}

function showToast(message) {
    try {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<i data-lucide="check-circle" style="color: #10b981; width: 18px; height: 18px;"></i> <span>${escapeHtml(message)}</span>`;
        container.appendChild(toast);

        safeCreateIcons();

        setTimeout(() => {
            try {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(16px)';
                toast.style.transition = 'all 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            } catch (e) {}
        }, 3200);
    } catch (e) {
        console.warn('Error showing toast:', e);
    }
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
