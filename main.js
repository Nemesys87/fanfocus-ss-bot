// FanFocusGPT Main JavaScript

class FanFocusGPT {
    constructor() {
        this.currentFanId = null;
        this.currentCreator = null;
        this.sessionData = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSessionData();
    }

    bindEvents() {
        // Form submission
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'chatForm') {
                e.preventDefault();
                this.handleFormSubmission();
            }
        });

        // Creator selection
        const creatorSelect = document.getElementById('creatorSelect');
        if (creatorSelect) {
            creatorSelect.addEventListener('change', (e) => {
                this.handleCreatorChange(e.target.value);
            });
        }

        // Fan status radio buttons
        document.querySelectorAll('input[name="fanStatus"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleFanStatusChange(e.target.value);
            });
        });

        // Copy response button
        const copyBtn = document.getElementById('copyResponseBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyResponse();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.handleFormSubmission();
                        break;
                    case 'c':
                        if (document.getElementById('responsePanel').style.display !== 'none') {
                            e.preventDefault();
                            this.copyResponse();
                        }
                        break;
                }
            }
        });
    }

    handleCreatorChange(creatorKey) {
        this.currentCreator = creatorKey;
        if (creatorKey) {
            this.loadCreatorInfo(creatorKey);
        } else {
            this.hideCreatorInfo();
        }
    }

    handleFanStatusChange(status) {
        const fanIdGroup = document.getElementById('fanIdGroup');
        const existingNotesGroup = document.getElementById('existingNotesGroup');

        if (status === 'EXISTING') {
            fanIdGroup.style.display = 'block';
            existingNotesGroup.style.display = 'block';
        } else {
            fanIdGroup.style.display = 'none';
            existingNotesGroup.style.display = 'none';
            document.getElementById('fanId').value = '';
            document.getElementById('existingNotes').value = '';
        }
    }

    async loadCreatorInfo(creatorKey) {
        try {
            const response = await fetch(`/api/creator_info/${creatorKey}`);
            const data = await response.json();

            if (data.success) {
                this.displayCreatorInfo(data.creator);
            } else {
                console.error('Failed to load creator info:', data.error);
            }
        } catch (error) {
            console.error('Error loading creator info:', error);
        }
    }

    displayCreatorInfo(creator) {
        const infoPanel = document.getElementById('creatorInfoPanel');
        const infoContent = document.getElementById('creatorInfo');

        const html = `
            <div class="creator-profile">
                <h6 class="text-primary mb-3">${creator.name}</h6>

                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Niche:</strong>
                        <div class="text-muted small">
                            ${creator.niche_positioning.join(', ')}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <strong>English Level:</strong>
                        <span class="badge bg-info">${creator.english_level}</span>
                    </div>
                </div>

                <div class="mb-3">
                    <strong>Personality Traits:</strong>
                    <div class="text-muted small">
                        ${creator.personality_traits.slice(0, 6).join(', ')}
                    </div>
                </div>

                <div class="mb-3">
                    <strong>Communication Style:</strong>
                    <div class="text-muted small">
                        ${creator.communication_style.tone}
                    </div>
                </div>

                <div class="mb-3">
                    <strong>Key Restrictions:</strong>
                    <ul class="small text-danger mb-0">
                        ${creator.restrictions.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>

                <div class="mb-0">
                    <strong>Chat Goal:</strong>
                    <div class="text-muted small">
                        ${creator.chat_strategy.goal}
                    </div>
                </div>
            </div>
        `;

        infoContent.innerHTML = html;
        infoPanel.style.display = 'block';
        infoPanel.classList.add('fade-in');
    }

    hideCreatorInfo() {
        const infoPanel = document.getElementById('creatorInfoPanel');
        infoPanel.style.display = 'none';
    }

    async handleFormSubmission() {
        const formData = this.collectFormData();

        if (!this.validateFormData(formData)) {
            return;
        }

        this.showLoading();

        try {
            const response = await this.generateResponse(formData);

            if (response.success) {
                this.displayResponse(response);
                this.updateFanProfile(response.fan_profile, response.next_kyc_step);
                this.currentFanId = response.fan_id;
                this.saveSessionData();
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            console.error('Error generating response:', error);
            this.showError('Failed to generate response. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    collectFormData() {
        return {
            creator_key: document.getElementById('creatorSelect').value,
            fan_status: document.querySelector('input[name="fanStatus"]:checked').value,
            fan_message: document.getElementById('fanMessage').value.trim(),
            fan_id: document.getElementById('fanId').value.trim(),
            existing_notes: document.getElementById('existingNotes').value.trim()
        };
    }

    validateFormData(data) {
        if (!data.creator_key) {
            this.showError('Please select a creator model.');
            return false;
        }

        if (!data.fan_message) {
            this.showError('Please enter the fan\'s message.');
            return false;
        }

        return true;
    }

    async generateResponse(formData) {
        const response = await fetch('/api/generate_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        return await response.json();
    }

    displayResponse(responseData) {
        // Display AI response
        const responseElement = document.getElementById('aiResponse');
        responseElement.textContent = responseData.ai_response;

        // Display upselling suggestion if available
        const upsellPanel = document.getElementById('upsellPanel');
        const upsellSuggestion = document.getElementById('upsellSuggestion');

        if (responseData.upsell_suggestion) {
            upsellSuggestion.textContent = responseData.upsell_suggestion;
            upsellPanel.style.display = 'block';
        } else {
            upsellPanel.style.display = 'none';
        }

        // Show response panel
        const responsePanel = document.getElementById('responsePanel');
        responsePanel.style.display = 'block';
        responsePanel.classList.add('fade-in');

        // Scroll to response
        responsePanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    updateFanProfile(profile, nextStep) {
        // Update KYC progress
        const progressPercent = profile.phase0_completion;
        const progressBar = document.getElementById('kycProgress');
        const nextStepElement = document.getElementById('nextKycStep');

        progressBar.style.width = progressPercent + '%';
        progressBar.textContent = progressPercent + '%';
        nextStepElement.textContent = nextStep ? `Next step: ${nextStep}` : 'Phase 0 Complete';

        // Update profile fields
        document.getElementById('fanType').textContent = profile.fan_type || 'Not classified';
        document.getElementById('confidenceLevel').textContent = profile.confidence;
        document.getElementById('personality').textContent = profile.personality || 'Not determined';
        document.getElementById('purchaseInterest').textContent = profile.purchase_interest;
        document.getElementById('fanNotes').textContent = profile.notes || 'No notes yet';

        // Show fan profile panel
        const profilePanel = document.getElementById('fanProfilePanel');
        profilePanel.style.display = 'block';
        profilePanel.classList.add('slide-in');
    }

    copyResponse() {
        const responseText = document.getElementById('aiResponse').textContent;

        navigator.clipboard.writeText(responseText).then(() => {
            this.showCopySuccess();
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            this.showError('Failed to copy response to clipboard');
        });
    }

    showCopySuccess() {
        const btn = document.getElementById('copyResponseBtn');
        const originalHTML = btn.innerHTML;

        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-success');

        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-primary');
        }, 2000);
    }

    showLoading() {
        const modal = document.getElementById('loadingModal');
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    hideLoading() {
        const modal = document.getElementById('loadingModal');
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('errorAlert');
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'errorAlert';
            errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
            errorAlert.innerHTML = `
                <strong>Error:</strong> <span id="errorMessage"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.querySelector('.container-fluid').insertBefore(errorAlert, document.querySelector('.row'));
        }

        document.getElementById('errorMessage').textContent = message;
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getInstance(errorAlert);
            if (alert) {
                alert.close();
            }
        }, 5000);
    }

    saveSessionData() {
        const sessionData = {
            currentFanId: this.currentFanId,
            currentCreator: this.currentCreator,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem('fanfocus_session', JSON.stringify(sessionData));
    }

    loadSessionData() {
        try {
            const saved = localStorage.getItem('fanfocus_session');
            if (saved) {
                this.sessionData = JSON.parse(saved);
                this.currentFanId = this.sessionData.currentFanId;
                this.currentCreator = this.sessionData.currentCreator;

                // Restore creator selection if available
                if (this.currentCreator) {
                    const creatorSelect = document.getElementById('creatorSelect');
                    if (creatorSelect) {
                        creatorSelect.value = this.currentCreator;
                        this.loadCreatorInfo(this.currentCreator);
                    }
                }
            }
        } catch (error) {
            console.error('Error loading session data:', error);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new FanFocusGPT();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Utility functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
