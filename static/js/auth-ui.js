document.addEventListener('DOMContentLoaded', () => {
    const publicPaths = new Set(['/', '/login/', '/register/']);

    function hasValidAccessToken() {
        const token = localStorage.getItem('accessToken');
        if (!token) return false;

        try {
            const encodedPayload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(atob(encodedPayload.padEnd(Math.ceil(encodedPayload.length / 4) * 4, '=')));
            if (!payload.exp || payload.exp * 1000 <= Date.now()) {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                return false;
            }
            return true;
        } catch (error) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            return false;
        }
    }

    if (!publicPaths.has(window.location.pathname) && !hasValidAccessToken()) {
        window.location.replace('/login/');
        return;
    }

    if (window.location.pathname === '/dashboard/') {
        fetch('/api/accounts/profile/', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
            .then((response) => response.ok ? response.json() : Promise.reject())
            .then((profile) => {
                if ((profile.role || '').toLowerCase() === 'student') {
                    window.location.replace('/roadmaps/');
                }
            })
            .catch(() => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.replace('/login/');
            });
    }

    const forms = document.querySelectorAll('.needs-validation');

    forms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            form.classList.add('was-validated');
        });
    });

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const message = document.getElementById('loginMessage');
            const formData = new FormData(loginForm);

            try {
                const response = await fetch('/api/accounts/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: formData.get('username'),
                        password: formData.get('password')
                    })
                });

                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || data.error || 'Login failed');
                }

                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                message.className = 'alert alert-success border-0 rounded-3';
                message.textContent = 'Login successful! Redirecting...';
                message.classList.remove('d-none');
                const role = (data.user?.role || '').toLowerCase();
                window.location.href = role === 'student' ? '/' : '/profile/';
            } catch (error) {
                message.className = 'alert alert-danger border-0 rounded-3';
                message.textContent = error.message;
                message.classList.remove('d-none');
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const message = document.getElementById('registerMessage');
            const formData = new FormData(registerForm);

            try {
                const response = await fetch('/api/accounts/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: formData.get('username'),
                        email: formData.get('email'),
                        password: formData.get('password'),
                        first_name: formData.get('first_name'),
                        last_name: formData.get('last_name')
                    })
                });

                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || data.error || 'Registration failed');
                }

                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                message.className = 'alert alert-success border-0 rounded-3';
                message.textContent = 'Registration successful! Redirecting...';
                message.classList.remove('d-none');
                window.location.href = '/';
            } catch (error) {
                message.className = 'alert alert-danger border-0 rounded-3';
                message.textContent = error.message;
                message.classList.remove('d-none');
            }
        });
    }

    const profilePage = document.getElementById('profileInfo');
    if (profilePage) {
        const token = localStorage.getItem('accessToken');
        const message = document.getElementById('profileMessage');
        if (!token) {
            message.className = 'alert alert-warning border-0 rounded-3';
            message.textContent = 'Please log in to view your profile.';
            message.classList.remove('d-none');
            return;
        }

        fetch('/api/accounts/profile/', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(async (response) => {
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to load profile');
                }

                document.getElementById('profileName').textContent = `${data.first_name || ''} ${data.last_name || ''}`.trim() || 'N/A';
                document.getElementById('profileEmail').textContent = data.email || 'N/A';
                document.getElementById('profileRole').textContent = data.role || 'N/A';
                document.getElementById('profileUsername').textContent = data.username || 'N/A';

                const headerUsername = document.getElementById('profileHeaderUsername');
                if (headerUsername) {
                    headerUsername.textContent = data.username || data.first_name || 'User';
                }
            })
            .catch((error) => {
                message.className = 'alert alert-danger border-0 rounded-3';
                message.textContent = error.message;
                message.classList.remove('d-none');
            });
    }

    const logoutButtons = document.querySelectorAll('[data-logout]');
    logoutButtons.forEach((logoutButton) => {
        logoutButton.addEventListener('click', async () => {
            const token = localStorage.getItem('refreshToken');
            try {
                await fetch('/api/accounts/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('accessToken') || ''}`
                    },
                    body: JSON.stringify({ refresh: token })
                });
            } catch (error) {
                console.error(error);
            } finally {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href = '/login/';
            }
        });
    });

    const guestNavItems = document.querySelectorAll('.auth-guest-item');
    const authenticatedNavItems = document.querySelectorAll('.auth-authenticated-item');
    const homeGuestActions = document.querySelectorAll('.auth-guest-action');
    const homeAuthenticatedActions = document.querySelectorAll('.auth-authenticated-action');
    const instructorNavItem = document.querySelector('.instructor-nav-item');
    const dashboardNavItems = document.querySelectorAll('.dashboard-nav-item');
    const hasToken = hasValidAccessToken();

    guestNavItems.forEach((item) => item.classList.toggle('d-none', hasToken));
    authenticatedNavItems.forEach((item) => item.classList.toggle('d-none', !hasToken));
    homeGuestActions.forEach((item) => item.classList.toggle('d-none', hasToken));
    homeAuthenticatedActions.forEach((item) => item.classList.toggle('d-none', !hasToken));

    if (instructorNavItem) {
        instructorNavItem.classList.toggle('d-none', true);
    }
    dashboardNavItems.forEach((item) => item.classList.toggle('d-none', true));

    if (hasToken) {
        fetch('/api/accounts/profile/', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
            .then((res) => res.ok ? res.json() : null)
            .then((profile) => {
                if (!profile) return;
                const role = (profile.role || profile.effective_role || '').toLowerCase();
                const isStudent = role === 'student';
                dashboardNavItems.forEach((item) => item.classList.toggle('d-none', isStudent));
                if (instructorNavItem) {
                    instructorNavItem.classList.toggle('d-none', isStudent);
                }
            })
            .catch(() => {});
    }

    const instructorPage = document.getElementById('instructorPage');
    if (instructorPage) {
        const token = localStorage.getItem('accessToken');
        const roleNotice = document.getElementById('roleNotice');
        const roadmapList = document.getElementById('instructorRoadmapList');
        const stepList = document.getElementById('instructorStepList');
        const quizList = document.getElementById('instructorQuizList');
        const learningContentList = document.getElementById('instructorLearningContentList');
        const stepSelect = document.getElementById('quizStepSelect');
        const roadmapSelect = document.getElementById('stepRoadmapSelect');
        const questionQuizSelect = document.getElementById('questionQuizSelect');
        const learningContentStepSelect = document.getElementById('learningContentStepSelect');
        const createQuizForm = document.getElementById('createQuizForm');
        const createRoadmapForm = document.getElementById('createRoadmapForm');
        const createStepForm = document.getElementById('createStepForm');
        const createQuestionForm = document.getElementById('createQuestionForm');
        const createLearningContentForm = document.getElementById('createLearningContentForm');
        const createQuizMessage = document.getElementById('createQuizMessage');
        const createRoadmapMessage = document.getElementById('createRoadmapMessage');
        const createStepMessage = document.getElementById('createStepMessage');
        const createQuestionMessage = document.getElementById('createQuestionMessage');
        const createLearningContentMessage = document.getElementById('createLearningContentMessage');
        const learningContentType = document.getElementById('learningContentType');
        const learningContentVideoUpload = document.getElementById('learningContentVideoUpload');
        const addChoiceBtn = document.getElementById('addChoiceBtn');
        const choiceRows = document.getElementById('choiceRows');

        let cachedRoadmaps = [];
        let cachedSteps = [];
        let cachedQuizzes = [];
        let cachedContents = [];

        function showMessage(element, type, text) {
            if (!element) return;
            element.className = `alert alert-${type} border-0 rounded-3`;
            element.textContent = text;
            element.classList.remove('d-none');
        }

        function populateStepSelect(select, steps) {
            if (!select) return;

            if (!steps.length) {
                select.innerHTML = '<option value="" selected disabled>No steps available — create a step first</option>';
                select.disabled = true;
                return;
            }

            select.innerHTML = `
                <option value="" selected disabled>Select a step</option>
                ${steps.map((step) => `<option value="${step.id}">${step.title}</option>`).join('')}
            `;
            select.disabled = false;
        }

        function updateLearningContentFields() {
            if (!learningContentType || !learningContentVideoUpload) return;
            learningContentVideoUpload.classList.toggle(
                'd-none',
                learningContentType.value !== 'video'
            );
        }

        if (learningContentType) {
            learningContentType.addEventListener('change', updateLearningContentFields);
            updateLearningContentFields();
        }

        async function refreshAccessToken() {
            const refresh = localStorage.getItem('refreshToken');
            if (!refresh) return null;

            try {
                const res = await fetch('/api/accounts/token/refresh/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh })
                });
                if (!res.ok) return null;
                const data = await res.json();
                if (data.access) {
                    localStorage.setItem('accessToken', data.access);
                    if (data.refresh) localStorage.setItem('refreshToken', data.refresh);
                    return data.access;
                }
            } catch (e) {
                return null;
            }
            return null;
        }

        async function fetchJson(url, options = {}, isRetry = false) {
            const response = await fetch(url, options);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                let message = data.detail || data.error || data.message;
                const isTokenError = response.status === 401 || (message && (message.includes('token') || message === 'Given token not valid for any token type'));

                if (isTokenError && !isRetry) {
                    const newAccess = await refreshAccessToken();
                    if (newAccess) {
                        const newHeaders = { ...(options.headers || {}), 'Authorization': `Bearer ${newAccess}` };
                        return fetchJson(url, { ...options, headers: newHeaders }, true);
                    }
                }

                if (!message && typeof data === 'object') {
                    const errors = [];
                    for (const [key, val] of Object.entries(data)) {
                        const errStr = Array.isArray(val) ? val.join(', ') : String(val);
                        errors.push(`${key}: ${errStr}`);
                    }
                    if (errors.length) message = errors.join(' | ');
                }
                message = message || 'Request failed';
                if (isTokenError) {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    window.location.href = '/login/';
                }
                throw new Error(message);
            }

            return data;
        }

        function addChoiceRow(text = '', isCorrect = false) {
            if (!choiceRows) return;
            const row = document.createElement('div');
            row.className = 'row g-2 align-items-center choice-row mb-2';
            row.innerHTML = `
                <div class="col-md-7">
                    <input type="text" class="form-control form-control-glass" placeholder="Choice option..." value="${text}" required>
                </div>
                <div class="col-md-3">
                    <label class="d-flex align-items-center gap-2 mb-0 text-secondary small">
                        <input type="radio" name="correctChoice" class="form-check-input mt-0" ${isCorrect ? 'checked' : ''}>
                        <span>Correct Answer</span>
                    </label>
                </div>
                <div class="col-md-2 text-end">
                    <button type="button" class="btn btn-sm btn-glass text-danger remove-choice-btn"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;
            choiceRows.appendChild(row);

            row.querySelector('.remove-choice-btn').addEventListener('click', () => {
                row.remove();
            });
        }

        if (addChoiceBtn) {
            addChoiceBtn.addEventListener('click', () => addChoiceRow());
        }

        for (let i = 0; i < 4; i += 1) {
            addChoiceRow('', i === 0);
        }

        // Universal Edit Modal Logic
        const editEntityModalElement = document.getElementById('editEntityModal');
        const editEntityForm = document.getElementById('editEntityForm');
        let currentEditTarget = { type: '', id: null, endpoint: '' };

        window.openEditModal = function(type, id) {
            currentEditTarget = { type, id };
            const modalTitle = document.getElementById('editEntityModalLabel');
            const modalBody = document.getElementById('editEntityModalBody');

            if (type === 'roadmap') {
                const item = cachedRoadmaps.find(r => r.id === id);
                if (!item) return;
                currentEditTarget.endpoint = `/api/roadmaps/roadmaps/${id}/`;
                modalTitle.textContent = `Edit Roadmap: ${item.title}`;
                modalBody.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Roadmap Title</label>
                        <input type="text" name="title" class="form-control form-control-glass" value="${item.title}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Description</label>
                        <textarea name="description" class="form-control form-control-glass" rows="3" required>${item.description || ''}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Status</label>
                        <select name="status" class="form-select form-select-glass">
                            <option value="draft" ${item.status === 'draft' ? 'selected' : ''}>Draft</option>
                            <option value="published" ${item.status === 'published' ? 'selected' : ''}>Published</option>
                            <option value="archived" ${item.status === 'archived' ? 'selected' : ''}>Archived</option>
                        </select>
                    </div>
                `;
            } else if (type === 'step') {
                const item = cachedSteps.find(s => s.id === id);
                if (!item) return;
                currentEditTarget.endpoint = `/api/roadmaps/steps/${id}/`;
                modalTitle.textContent = `Edit Step: ${item.title}`;
                modalBody.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Step Title</label>
                        <input type="text" name="title" class="form-control form-control-glass" value="${item.title}" required>
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <label class="form-label text-secondary small">Order</label>
                            <input type="number" name="order" class="form-control form-control-glass" value="${item.order}" min="1" required>
                        </div>
                        <div class="col-6">
                            <label class="form-label text-secondary small">Difficulty</label>
                            <select name="difficulty" class="form-select form-select-glass">
                                <option value="beginner" ${item.difficulty === 'beginner' ? 'selected' : ''}>Beginner</option>
                                <option value="intermediate" ${item.difficulty === 'intermediate' ? 'selected' : ''}>Intermediate</option>
                                <option value="advanced" ${item.difficulty === 'advanced' ? 'selected' : ''}>Advanced</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Unlock Quiz Score (%)</label>
                        <input type="number" name="unlock_score" class="form-control form-control-glass" value="${item.unlock_score || 80}" min="0" max="100" required>
                    </div>
                `;
            } else if (type === 'quiz') {
                const item = cachedQuizzes.find(q => q.id === id);
                if (!item) return;
                currentEditTarget.endpoint = `/api/quizzes/${id}/`;
                modalTitle.textContent = `Edit Quiz: ${item.title}`;
                modalBody.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Quiz Title</label>
                        <input type="text" name="title" class="form-control form-control-glass" value="${item.title}" required>
                    </div>
                `;
            } else if (type === 'content') {
                const item = cachedContents.find(c => c.id === id);
                if (!item) return;
                currentEditTarget.endpoint = `/api/roadmaps/contents/${id}/`;
                modalTitle.textContent = `Edit Content: ${item.title}`;
                modalBody.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Material Title</label>
                        <input type="text" name="title" class="form-control form-control-glass" value="${item.title}" required>
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-8">
                            <label class="form-label text-secondary small">Content Type</label>
                            <select name="content_type" class="form-select form-select-glass">
                                <option value="video" ${item.content_type === 'video' ? 'selected' : ''}>Video</option>
                                <option value="article" ${item.content_type === 'article' ? 'selected' : ''}>Article</option>
                                <option value="code" ${item.content_type === 'code' ? 'selected' : ''}>Code</option>
                                <option value="pdf" ${item.content_type === 'pdf' ? 'selected' : ''}>PDF</option>
                                <option value="link" ${item.content_type === 'link' ? 'selected' : ''}>Link</option>
                            </select>
                        </div>
                        <div class="col-4">
                            <label class="form-label text-secondary small">Lesson Order #</label>
                            <input type="number" name="order" class="form-control form-control-glass" value="${item.order || 1}" min="1" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Overview Description</label>
                        <textarea name="description" class="form-control form-control-glass" rows="2">${item.description || ''}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">Content / URL / Body</label>
                        <textarea name="content" class="form-control form-control-glass" rows="3">${item.content || ''}</textarea>
                    </div>
                `;
            }

            const modalInstance = new bootstrap.Modal(editEntityModalElement);
            modalInstance.show();
        };

        if (editEntityForm) {
            editEntityForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(editEntityForm);
                const payload = {};
                formData.forEach((value, key) => {
                    if (key === 'order' || key === 'unlock_score') {
                        payload[key] = Number(value);
                    } else {
                        payload[key] = value;
                    }
                });

                try {
                    await fetchJson(currentEditTarget.endpoint, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(payload)
                    });

                    const modalInstance = bootstrap.Modal.getInstance(editEntityModalElement);
                    if (modalInstance) modalInstance.hide();
                    loadInstructorData();
                } catch (error) {
                    alert('Failed to save changes: ' + error.message);
                }
            });
        }

        async function loadInstructorData() {
            try {
                let currentRole = 'guest';
                if (token) {
                    try {
                        const profileResponse = await fetchJson('/api/accounts/profile/', {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        currentRole = profileResponse.role || profileResponse.effective_role || 'guest';
                    } catch (error) {
                        if (roleNotice) {
                            showMessage(roleNotice, 'warning', 'Your session expired. Please sign in again.');
                        }
                        if (createQuizForm) createQuizForm.classList.add('d-none');
                        if (createRoadmapForm) createRoadmapForm.classList.add('d-none');
                        if (createStepForm) createStepForm.classList.add('d-none');
                        if (createQuestionForm) createQuestionForm.classList.add('d-none');
                        return;
                    }
                }

                const authorizedRole = currentRole?.toLowerCase();
                if (!token || !['instructor', 'admin'].includes(authorizedRole)) {
                    if (roleNotice) {
                        showMessage(roleNotice, 'warning', 'You need an instructor or admin account to manage content here.');
                    }
                    if (createQuizForm) createQuizForm.classList.add('d-none');
                    if (createRoadmapForm) createRoadmapForm.classList.add('d-none');
                    if (createStepForm) createStepForm.classList.add('d-none');
                    if (createQuestionForm) createQuestionForm.classList.add('d-none');
                    if (createLearningContentForm) createLearningContentForm.classList.add('d-none');
                    if (instructorPage) {
                        instructorPage.innerHTML = `
                            <div class="alert alert-danger bg-danger bg-opacity-20 text-danger border-0">You do not have access to the instructor area.</div>
                        `;
                    }
                    return;
                }

                if (instructorNavItem) {
                    instructorNavItem.classList.toggle('d-none', false);
                }

                if (roleNotice) {
                    roleNotice.className = 'alert alert-success bg-success bg-opacity-20 text-success border-0';
                    roleNotice.innerHTML = `<i class="fa-solid fa-circle-check me-2"></i>Signed in as <strong>${currentRole}</strong>. Management controls enabled.`;
                    roleNotice.classList.remove('d-none');
                }

                const stepResponse = await fetchJson('/api/roadmaps/steps/', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const steps = Array.isArray(stepResponse) ? stepResponse : [];
                cachedSteps = steps;

                populateStepSelect(stepSelect, steps);
                populateStepSelect(learningContentStepSelect, steps);

                const [roadmapResponse, quizResponse] = await Promise.all([
                    fetchJson('/api/roadmaps/roadmaps/', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    }),
                    fetchJson('/api/quizzes/', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    })
                ]);

                const roadmaps = Array.isArray(roadmapResponse) ? roadmapResponse : [];
                const quizzes = Array.isArray(quizResponse) ? quizResponse : [];

                cachedRoadmaps = roadmaps;
                cachedQuizzes = quizzes;

                const roadmapCountEl = document.getElementById('roadmapRegistryCount');
                if (roadmapCountEl) roadmapCountEl.textContent = roadmaps.length;

                const stepCountEl = document.getElementById('stepRegistryCount');
                if (stepCountEl) stepCountEl.textContent = steps.length;

                const quizCountEl = document.getElementById('quizRegistryCount');
                if (quizCountEl) quizCountEl.textContent = quizzes.length;

                if (roadmapSelect) {
                    roadmapSelect.innerHTML = roadmaps.map((roadmap) => `<option value="${roadmap.id}">${roadmap.title}</option>`).join('');
                }

                if (questionQuizSelect) {
                    questionQuizSelect.innerHTML = quizzes.map((quiz) => `<option value="${quiz.id}">${quiz.title}</option>`).join('');
                }

                // Render Roadmaps List with Edit & Delete
                if (roadmapList) {
                    roadmapList.innerHTML = roadmaps.length
                        ? roadmaps.map((roadmap) => `
                            <div class="glass-card p-3 bg-dark bg-opacity-40 border border-secondary border-opacity-25">
                                <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                                    <div>
                                        <div class="fw-bold text-white mb-1"><i class="fa-solid fa-route me-2 text-indigo"></i>${roadmap.title}</div>
                                        <small class="text-secondary d-block">${roadmap.description || 'No description provided.'}</small>
                                    </div>
                                    <span class="badge-glass-cyan text-capitalize text-xs">${roadmap.status}</span>
                                </div>
                                <div class="pt-2 border-top border-secondary border-opacity-25 d-flex gap-2 justify-content-end">
                                    <button type="button" class="btn btn-sm btn-outline-indigo px-3 rounded-3" onclick="openEditModal('roadmap', ${roadmap.id})"><i class="fa-solid fa-pen me-1"></i> Edit</button>
                                    <button type="button" class="btn btn-sm btn-glass text-danger px-3 rounded-3 delete-roadmap-btn" data-id="${roadmap.id}"><i class="fa-solid fa-trash me-1"></i> Delete</button>
                                </div>
                            </div>
                        `).join('')
                        : '<div class="alert alert-dark border-0 glass-card text-secondary mb-0"><i class="fa-solid fa-info-circle me-2"></i>No roadmaps created yet.</div>';
                }

                // Render Steps List with Edit & Delete
                if (stepList) {
                    stepList.innerHTML = steps.length
                        ? steps.map((step) => {
                            return `
                                <div class="glass-card p-3 bg-dark bg-opacity-40 border border-secondary border-opacity-25">
                                    <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                                        <div>
                                            <div class="fw-bold text-white mb-1"><i class="fa-solid fa-list-check me-2 text-cyan"></i>Step ${step.order}: ${step.title}</div>
                                            <small class="text-secondary">Difficulty: ${step.difficulty} &bull; Unlock: ${step.unlock_score}%</small>
                                        </div>
                                    </div>
                                    <div class="pt-2 border-top border-secondary border-opacity-25 d-flex gap-2 justify-content-end">
                                        <button type="button" class="btn btn-sm btn-outline-indigo px-3 rounded-3" onclick="openEditModal('step', ${step.id})"><i class="fa-solid fa-pen me-1"></i> Edit</button>
                                        <button type="button" class="btn btn-sm btn-glass text-danger px-3 rounded-3 delete-step-btn" data-id="${step.id}"><i class="fa-solid fa-trash me-1"></i> Delete</button>
                                    </div>
                                </div>
                            `;
                        }).join('')
                        : '<div class="alert alert-dark border-0 glass-card text-secondary mb-0"><i class="fa-solid fa-info-circle me-2"></i>No steps available yet.</div>';
                }

                // Render Learning Contents List with Edit & Delete
                if (learningContentList) {
                    const learningContents = steps.flatMap((step) => (
                        (Array.isArray(step.learning_contents) ? step.learning_contents : []).map((content) => ({
                            ...content,
                            stepTitle: step.title,
                            stepOrder: step.order
                        }))
                    ));
                    cachedContents = learningContents;

                    const contentCountEl = document.getElementById('contentRegistryCount');
                    if (contentCountEl) contentCountEl.textContent = learningContents.length;

                    learningContentList.innerHTML = learningContents.length
                        ? learningContents.map((content) => `
                            <div class="glass-card p-3 bg-dark bg-opacity-40 border border-secondary border-opacity-25">
                                <div class="d-flex justify-content-between align-items-start gap-3 mb-2">
                                    <div>
                                        <div class="fw-bold text-white mb-1"><i class="fa-solid fa-file-video text-emerald me-2"></i>Lesson ${content.order || 1}: ${content.title}</div>
                                        <small class="text-secondary">Step ${content.stepOrder}: ${content.stepTitle} &bull; ${content.content_type || 'Resource'}</small>
                                    </div>
                                    <span class="badge-glass-cyan text-capitalize text-xs">${content.content_type || 'content'}</span>
                                </div>
                                ${content.description ? `<div class="small text-secondary mb-2">${content.description}</div>` : ''}
                                <div class="pt-2 border-top border-secondary border-opacity-25 d-flex gap-2 justify-content-end">
                                    <button type="button" class="btn btn-sm btn-outline-indigo px-3 rounded-3" onclick="openEditModal('content', ${content.id})"><i class="fa-solid fa-pen me-1"></i> Edit</button>
                                    <button type="button" class="btn btn-sm btn-glass text-danger px-3 rounded-3 delete-content-btn" data-id="${content.id}"><i class="fa-solid fa-trash me-1"></i> Delete</button>
                                </div>
                            </div>
                        `).join('')
                        : '<div class="alert alert-dark border-0 glass-card text-secondary mb-0"><i class="fa-solid fa-info-circle me-2"></i>No learning content has been added yet.</div>';
                }

                // Render Quizzes List with Edit & Delete
                if (quizList) {
                    quizList.innerHTML = quizzes.length
                        ? quizzes.map((quiz) => {
                            const questions = Array.isArray(quiz.questions) ? quiz.questions : [];
                            const questionMarkup = questions.length
                                ? questions.map((question, index) => {
                                    const choices = Array.isArray(question.choices) ? question.choices : [];
                                    const choiceMarkup = choices.length
                                        ? `<ul class="mb-1 ps-3 small text-secondary">${choices.map((choice) => `<li>${choice.text}${choice.is_correct ? ' <span class="badge-glass-emerald text-xs">Correct</span>' : ''}</li>`).join('')}</ul>`
                                        : '<div class="text-muted small">No choices yet.</div>';

                                    return `
                                        <div class="glass-card p-2 bg-dark bg-opacity-60 mb-2 border-0">
                                            <div class="d-flex justify-content-between align-items-start gap-2 mb-1">
                                                <div class="fw-semibold small text-white">Q${index + 1}. ${question.text}</div>
                                                <button type="button" class="btn btn-sm btn-glass text-danger py-0 px-2 delete-question-btn" data-question-id="${question.id}"><i class="fa-solid fa-xmark"></i></button>
                                            </div>
                                            ${choiceMarkup}
                                        </div>
                                    `;
                                }).join('')
                                : '<div class="text-muted small">No questions added yet.</div>';

                            return `
                                <div class="glass-card p-3 bg-dark bg-opacity-40 border border-secondary border-opacity-25">
                                    <div class="d-flex justify-content-between align-items-start gap-3 mb-2">
                                        <div>
                                            <div class="fw-bold text-white mb-1"><i class="fa-solid fa-brain text-purple me-2"></i>${quiz.title}</div>
                                            <small class="text-secondary">Quiz ID: #${quiz.id} &bull; ${questions.length} Questions</small>
                                        </div>
                                        <div class="d-flex gap-1">
                                            <button type="button" class="btn btn-sm btn-outline-indigo px-2 rounded-3" onclick="openEditModal('quiz', ${quiz.id})"><i class="fa-solid fa-pen"></i></button>
                                            <button type="button" class="btn btn-sm btn-glass text-danger px-2 rounded-3 delete-quiz-btn" data-quiz-id="${quiz.id}"><i class="fa-solid fa-trash"></i></button>
                                        </div>
                                    </div>
                                    <div class="d-grid gap-1 mt-2">${questionMarkup}</div>
                                </div>
                            `;
                        }).join('')
                        : '<div class="alert alert-dark border-0 glass-card text-secondary mb-0"><i class="fa-solid fa-info-circle me-2"></i>No quizzes created yet.</div>';
                }

                // Global Delete Event Delegation
                if (!window._deleteHandlerAttached) {
                    window._deleteHandlerAttached = true;
                    document.addEventListener('click', async (e) => {
                        const activeToken = localStorage.getItem('accessToken');
                        if (!activeToken) return;

                        const deleteRoadmapBtn = e.target.closest('.delete-roadmap-btn');
                        if (deleteRoadmapBtn) {
                            e.preventDefault();
                            const id = Number(deleteRoadmapBtn.dataset.id || deleteRoadmapBtn.dataset.roadmapId);
                            if (!id || !confirm('Delete this roadmap? This action cannot be undone.')) return;
                            try {
                                await fetchJson(`/api/roadmaps/roadmaps/${id}/`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${activeToken}` }
                                });
                                if (typeof loadInstructorData === 'function') loadInstructorData();
                                if (typeof loadDashboard === 'function') loadDashboard();
                            } catch (err) { alert('Delete failed: ' + err.message); }
                            return;
                        }

                        const deleteStepBtn = e.target.closest('.delete-step-btn');
                        if (deleteStepBtn) {
                            e.preventDefault();
                            const id = Number(deleteStepBtn.dataset.id || deleteStepBtn.dataset.stepId);
                            if (!id || !confirm('Delete this step module?')) return;
                            try {
                                await fetchJson(`/api/roadmaps/steps/${id}/`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${activeToken}` }
                                });
                                if (typeof loadInstructorData === 'function') loadInstructorData();
                                if (typeof loadDashboard === 'function') loadDashboard();
                            } catch (err) { alert('Delete failed: ' + err.message); }
                            return;
                        }

                        const deleteContentBtn = e.target.closest('.delete-content-btn');
                        if (deleteContentBtn) {
                            e.preventDefault();
                            const id = Number(deleteContentBtn.dataset.id || deleteContentBtn.dataset.contentId);
                            if (!id || !confirm('Delete this learning material?')) return;
                            try {
                                await fetchJson(`/api/roadmaps/contents/${id}/`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${activeToken}` }
                                });
                                if (typeof loadInstructorData === 'function') loadInstructorData();
                                if (typeof loadDashboard === 'function') loadDashboard();
                            } catch (err) { alert('Delete failed: ' + err.message); }
                            return;
                        }

                        const deleteQuizBtn = e.target.closest('.delete-quiz-btn');
                        if (deleteQuizBtn) {
                            e.preventDefault();
                            const quizId = Number(deleteQuizBtn.dataset.quizId || deleteQuizBtn.dataset.id);
                            if (!quizId || !confirm('Delete this quiz? This will also remove its questions.')) return;
                            try {
                                await fetchJson(`/api/quizzes/${quizId}/`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${activeToken}` }
                                });
                                if (typeof loadInstructorData === 'function') loadInstructorData();
                                if (typeof loadDashboard === 'function') loadDashboard();
                            } catch (err) { alert('Delete failed: ' + err.message); }
                            return;
                        }

                        const deleteQuestionBtn = e.target.closest('.delete-question-btn');
                        if (deleteQuestionBtn) {
                            e.preventDefault();
                            const questionId = Number(deleteQuestionBtn.dataset.questionId || deleteQuestionBtn.dataset.id);
                            if (!questionId || !confirm('Delete this question?')) return;
                            try {
                                await fetchJson(`/api/quizzes/questions/${questionId}/`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${activeToken}` }
                                });
                                if (typeof loadInstructorData === 'function') loadInstructorData();
                                if (typeof loadDashboard === 'function') loadDashboard();
                            } catch (err) { alert('Delete failed: ' + err.message); }
                            return;
                        }
                    });
                }
            } catch (error) {
                console.error(error);
                showMessage(createQuizMessage, 'danger', 'Unable to load instructor data.');
            }
        }

        if (createRoadmapForm) {
            createRoadmapForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                if (!token) {
                    showMessage(createRoadmapMessage, 'warning', 'Please sign in as an instructor or admin to create roadmaps.');
                    return;
                }

                const formData = new FormData(createRoadmapForm);
                try {
                    const data = await fetchJson('/api/roadmaps/roadmaps/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            title: formData.get('title'),
                            description: formData.get('description'),
                            status: formData.get('status') || 'draft',
                        })
                    });

                    showMessage(createRoadmapMessage, 'success', `Roadmap created successfully: ${data.title}`);
                    createRoadmapForm.reset();
                    loadInstructorData();
                } catch (error) {
                    showMessage(createRoadmapMessage, 'danger', error.message);
                }
            });
        }

        if (createStepForm) {
            createStepForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                if (!token) {
                    showMessage(createStepMessage, 'warning', 'Please sign in as an instructor or admin to create steps.');
                    return;
                }

                const formData = new FormData(createStepForm);
                const roadmapId = Number(formData.get('roadmap'));
                if (!roadmapId) {
                    showMessage(createStepMessage, 'danger', 'Please choose a roadmap before creating a step.');
                    return;
                }

                try {
                    const data = await fetchJson(`/api/roadmaps/roadmaps/${roadmapId}/steps/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            title: formData.get('title'),
                            order: Number(formData.get('order')),
                            difficulty: formData.get('difficulty') || 'beginner',
                            unlock_score: Number(formData.get('unlock_score')),
                        })
                    });

                    showMessage(createStepMessage, 'success', `Step created successfully: ${data.title}`);
                    createStepForm.reset();
                    loadInstructorData();
                } catch (error) {
                    showMessage(createStepMessage, 'danger', error.message);
                }
            });
        }

        if (createQuizForm) {
            createQuizForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                if (!token) {
                    showMessage(createQuizMessage, 'warning', 'Please sign in as an instructor or admin to create a quiz.');
                    return;
                }

                const formData = new FormData(createQuizForm);
                try {
                    const data = await fetchJson('/api/quizzes/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            title: formData.get('title'),
                            step: Number(formData.get('step'))
                        })
                    });

                    showMessage(createQuizMessage, 'success', `Quiz created successfully: ${data.title}`);
                    createQuizForm.reset();
                    loadInstructorData();
                } catch (error) {
                    showMessage(createQuizMessage, 'danger', error.message);
                }
            });
        }

        if (createLearningContentForm) {
            createLearningContentForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                if (!token) {
                    showMessage(createLearningContentMessage, 'warning', 'Please sign in as an instructor or admin to add learning content.');
                    return;
                }

                const formData = new FormData(createLearningContentForm);
                try {
                    const data = await fetchJson('/api/roadmaps/contents/', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    });

                    showMessage(createLearningContentMessage, 'success', `Learning content created successfully: ${data.title}`);
                    createLearningContentForm.reset();
                    updateLearningContentFields();
                    loadInstructorData();
                } catch (error) {
                    showMessage(createLearningContentMessage, 'danger', error.message);
                }
            });
        }

        if (createQuestionForm) {
            createQuestionForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                if (!token) {
                    showMessage(createQuestionMessage, 'warning', 'Please sign in as an instructor or admin to create a question.');
                    return;
                }

                const formData = new FormData(createQuestionForm);
                const rows = choiceRows.querySelectorAll('.choice-row');
                const choices = [];

                rows.forEach((row) => {
                    const text = row.querySelector('input[type="text"]').value.trim();
                    const isCorrect = row.querySelector('input[type="radio"]').checked;
                    if (text) {
                        choices.push({ text, is_correct: isCorrect });
                    }
                });

                if (choices.length < 2) {
                    showMessage(createQuestionMessage, 'danger', 'Please provide at least two choices for the question.');
                    return;
                }

                const correctChoiceCount = choices.filter((choice) => choice.is_correct).length;
                if (correctChoiceCount !== 1) {
                    showMessage(createQuestionMessage, 'danger', 'Please mark exactly one choice as the correct answer.');
                    return;
                }

                try {
                    const data = await fetchJson('/api/quizzes/questions/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            quiz: Number(formData.get('quiz')),
                            text: formData.get('text'),
                            order: Number(formData.get('order')),
                            choices,
                        })
                    });

                    showMessage(createQuestionMessage, 'success', `Question created successfully: ${data.text}`);
                    createQuestionForm.reset();
                    choiceRows.innerHTML = '';
                    for (let i = 0; i < 4; i += 1) {
                        addChoiceRow('', i === 0);
                    }
                    loadInstructorData();
                } catch (error) {
                    showMessage(createQuestionMessage, 'danger', error.message);
                }
            });
        }

        loadInstructorData();
    }
});
