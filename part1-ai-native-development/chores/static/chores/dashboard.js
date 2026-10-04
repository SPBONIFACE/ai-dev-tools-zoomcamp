/**
 * Chore Manager Dashboard Interactive Client
 * Powers live Chore Board updates, assignment completion, and AI allocation workflow.
 */

// Helper to retrieve CSRF token from meta tag, form input, or cookie
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  if (input && input.value) return input.value;
  const cookieMatch = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='));
  if (cookieMatch) {
    return cookieMatch.split('=')[1];
  }
  return '';
}

// Helper to escape HTML characters
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Return human-readable effort label and styling classes
function getEffortInfo(effortLevel) {
  switch (Number(effortLevel)) {
    case 1:
      return {
        label: 'Low',
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
      };
    case 3:
      return {
        label: 'High',
        badgeClass: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
      };
    case 2:
    default:
      return {
        label: 'Medium',
        badgeClass: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
      };
  }
}

// Return empty state template for a column
function getEmptyStateHtml(columnType) {
  switch (columnType) {
    case 'pending':
      return `
        <div class="empty-state text-center py-8 px-3 text-slate-400 text-xs flex flex-col items-center justify-center h-full">
          <svg class="w-8 h-8 text-slate-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>No pending assignments</span>
        </div>
      `;
    case 'in-progress':
      return `
        <div class="empty-state text-center py-8 px-3 text-slate-400 text-xs flex flex-col items-center justify-center h-full">
          <svg class="w-8 h-8 text-slate-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>No chores in progress</span>
        </div>
      `;
    case 'completed':
    default:
      return `
        <div class="empty-state text-center py-8 px-3 text-slate-400 text-xs flex flex-col items-center justify-center h-full">
          <svg class="w-8 h-8 text-slate-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>No completed chores</span>
        </div>
      `;
  }
}

// Create an assignment DOM card
function createAssignmentCard(assignment) {
  const card = document.createElement('div');
  card.className = 'assignment-card bg-slate-900/90 border border-slate-800 hover:border-slate-700/80 rounded-xl p-3.5 shadow-sm transition-all duration-300 space-y-2.5';
  card.dataset.assignmentId = assignment.id;
  card.dataset.status = assignment.status;

  const chore = assignment.chore || {};
  const member = assignment.member || {};
  const effort = getEffortInfo(chore.effort_level);
  const frequency = chore.frequency ? chore.frequency.replace('_', ' ') : 'weekly';

  const reasoningHtml = assignment.ai_reasoning
    ? `<div class="text-[11px] text-slate-400 italic bg-slate-950/60 p-2 rounded-lg border border-slate-800/60 leading-snug">
        <span class="font-medium text-slate-300 not-italic">AI Note:</span> "${escapeHtml(assignment.ai_reasoning)}"
      </div>`
    : '';

  const isCompleted = assignment.status === 'completed';

  const actionButtonHtml = isCompleted
    ? `<div class="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-medium py-1">
        <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>Completed</span>
      </div>`
    : `<button
        type="button"
        class="btn-mark-done w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 active:bg-emerald-600/40 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition cursor-pointer"
        data-id="${assignment.id}"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>Mark Done</span>
      </button>`;

  card.innerHTML = `
    <div class="flex items-start justify-between gap-2">
      <h4 class="text-sm font-semibold text-slate-100 leading-snug break-words">${escapeHtml(chore.title || 'Untitled Chore')}</h4>
      <span class="inline-flex items-center text-[10px] font-medium px-2 py-0.5 rounded shrink-0 ${effort.badgeClass}">
        ${effort.label}
      </span>
    </div>

    <div class="flex items-center justify-between gap-2 text-xs">
      <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-medium">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span>${escapeHtml(member.name || 'Unassigned')}</span>
      </span>
      <span class="text-[11px] text-slate-400 capitalize">${escapeHtml(frequency)}</span>
    </div>

    ${reasoningHtml}

    <div class="card-action-container pt-0.5">
      ${actionButtonHtml}
    </div>
  `;

  if (!isCompleted) {
    const markDoneBtn = card.querySelector('.btn-mark-done');
    if (markDoneBtn) {
      markDoneBtn.addEventListener('click', () => handleMarkDone(assignment.id, card));
    }
  }

  return card;
}

// Mark Done action handler
async function handleMarkDone(assignmentId, cardElement) {
  const btn = cardElement.querySelector('.btn-mark-done');
  if (!btn || btn.disabled) return;

  btn.disabled = true;
  btn.innerHTML = `
    <svg class="w-3.5 h-3.5 animate-spin text-emerald-300" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span>Completing...</span>
  `;

  try {
    const response = await fetch(`/api/assignments/${assignmentId}/complete/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ status: 'completed' }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${response.status}: Failed to complete assignment.`);
    }

    const updatedAssignment = await response.json();

    // Visual transition: smooth fade and move
    cardElement.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
    cardElement.style.opacity = '0';
    cardElement.style.transform = 'scale(0.95)';

    setTimeout(() => {
      const sourceCol = cardElement.parentElement;
      const completedCol = document.getElementById('completed-column');

      // Remove card from current column
      cardElement.remove();

      // Check source column empty state
      if (sourceCol) {
        const remainingCards = sourceCol.querySelectorAll('.assignment-card');
        if (remainingCards.length === 0) {
          const colType = sourceCol.id === 'pending-column' ? 'pending' : 'in-progress';
          sourceCol.innerHTML = getEmptyStateHtml(colType);
        }
      }

      // Update card status attribute and action container
      cardElement.dataset.status = 'completed';
      const actionContainer = cardElement.querySelector('.card-action-container');
      if (actionContainer) {
        actionContainer.innerHTML = `
          <div class="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-medium py-1">
            <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Completed</span>
          </div>
        `;
      }

      // Remove empty state from completed column if present
      if (completedCol) {
        const emptyState = completedCol.querySelector('.empty-state');
        if (emptyState) {
          emptyState.remove();
        }
        completedCol.prepend(cardElement);
      }

      // Fade back in
      requestAnimationFrame(() => {
        cardElement.style.opacity = '1';
        cardElement.style.transform = 'scale(1)';
      });

      // Update column badges & top metrics
      updateBoardCounts();
    }, 250);

  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = `
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <span>Mark Done</span>
    `;
    alert(err.message || 'Failed to complete assignment.');
  }
}

// Update column badge counters and metrics bar
function updateBoardCounts() {
  const pendingCol = document.getElementById('pending-column');
  const inProgressCol = document.getElementById('in-progress-column');
  const completedCol = document.getElementById('completed-column');

  const pendingCount = pendingCol ? pendingCol.querySelectorAll('.assignment-card').length : 0;
  const inProgressCount = inProgressCol ? inProgressCol.querySelectorAll('.assignment-card').length : 0;
  const completedCount = completedCol ? completedCol.querySelectorAll('.assignment-card').length : 0;

  // Badges
  const pendingBadge = document.getElementById('pending-column-badge');
  const inProgressBadge = document.getElementById('in-progress-column-badge');
  const completedBadge = document.getElementById('completed-column-badge');

  if (pendingBadge) pendingBadge.textContent = pendingCount;
  if (inProgressBadge) inProgressBadge.textContent = inProgressCount;
  if (completedBadge) completedBadge.textContent = completedCount;

  // Metrics Bar
  const metricPending = document.getElementById('metric-pending-assignments');
  const metricCompleted = document.getElementById('metric-completed-this-week');

  if (metricPending) metricPending.textContent = pendingCount;
  if (metricCompleted) metricCompleted.textContent = completedCount;
}

// Render assignments into the 3 columns
function renderChoreBoard(assignments) {
  const pendingCol = document.getElementById('pending-column');
  const inProgressCol = document.getElementById('in-progress-column');
  const completedCol = document.getElementById('completed-column');

  if (!pendingCol || !inProgressCol || !completedCol) return;

  // Clear existing content
  pendingCol.innerHTML = '';
  inProgressCol.innerHTML = '';
  completedCol.innerHTML = '';

  const pending = [];
  const inProgress = [];
  const completed = [];

  assignments.forEach((assignment) => {
    const status = (assignment.status || '').toLowerCase();
    if (status === 'completed') {
      completed.push(assignment);
    } else if (status === 'in_progress') {
      inProgress.push(assignment);
    } else if (status === 'pending') {
      pending.push(assignment);
    }
  });

  // Populate Pending Column
  if (pending.length === 0) {
    pendingCol.innerHTML = getEmptyStateHtml('pending');
  } else {
    pending.forEach((a) => pendingCol.appendChild(createAssignmentCard(a)));
  }

  // Populate In Progress Column
  if (inProgress.length === 0) {
    inProgressCol.innerHTML = getEmptyStateHtml('in-progress');
  } else {
    inProgress.forEach((a) => inProgressCol.appendChild(createAssignmentCard(a)));
  }

  // Populate Completed Column
  if (completed.length === 0) {
    completedCol.innerHTML = getEmptyStateHtml('completed');
  } else {
    completed.forEach((a) => completedCol.appendChild(createAssignmentCard(a)));
  }

  updateBoardCounts();
}

// Fetch all assignments and update board
async function loadAssignments() {
  try {
    const response = await fetch('/api/assignments/');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to fetch assignments`);
    }
    const assignments = await response.json();
    renderChoreBoard(assignments);
    return assignments;
  } catch (err) {
    console.error('Error loading assignments:', err);
  }
}

// Render preview of newly created assignments in AI Allocator panel
function renderAllocationPreview(assignments) {
  const previewContainer = document.getElementById('allocation-preview-container');
  const previewList = document.getElementById('allocation-preview-list');

  if (!previewContainer || !previewList) return;

  if (!assignments || assignments.length === 0) {
    previewContainer.classList.add('hidden');
    previewList.innerHTML = '';
    return;
  }

  previewList.innerHTML = '';
  assignments.forEach((item) => {
    const choreTitle = item.chore_title || (item.chore && item.chore.title) || 'Chore';
    const memberName = item.member_name || (item.member && item.member.name) || 'Member';
    const reasoning = item.reasoning || item.ai_reasoning || '';

    const row = document.createElement('div');
    row.className = 'p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-1';
    row.innerHTML = `
      <div class="flex items-center justify-between gap-2">
        <span class="font-medium text-slate-200 truncate">${escapeHtml(choreTitle)}</span>
        <span class="text-indigo-400 shrink-0 font-medium text-[11px] bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">${escapeHtml(memberName)}</span>
      </div>
      ${reasoning ? `<p class="text-[10px] text-slate-400 italic">${escapeHtml(reasoning)}</p>` : ''}
    `;
    previewList.appendChild(row);
  });

  previewContainer.classList.remove('hidden');
}

// Handle AI Allocator form submission
async function handleAllocate() {
  const btn = document.getElementById('btn-allocate');
  const spinner = document.getElementById('allocator-spinner');
  const btnText = document.getElementById('btn-allocate-text');
  const errorAlert = document.getElementById('allocation-error');
  const errorMessage = document.getElementById('allocation-error-message');
  const notesArea = document.getElementById('allocator-notes');
  const summaryEl = document.getElementById('allocation-summary');
  const engineBadge = document.getElementById('allocator-engine-badge');

  if (!btn || btn.disabled) return;

  // 1. Double-submission prevention & loading state
  btn.disabled = true;
  if (notesArea) notesArea.disabled = true;
  if (spinner) spinner.classList.remove('hidden');
  if (btnText) btnText.textContent = 'Allocating...';
  if (errorAlert) errorAlert.classList.add('hidden');

  const notes = notesArea ? notesArea.value.trim() : '';

  try {
    const response = await fetch('/api/allocate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ user_notes: notes }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const msg = data.error || data.message || 'Failed to run allocation. Please try again.';
      throw new Error(msg);
    }

    // 2. Render reasoning summary & engine badge
    if (engineBadge) {
      engineBadge.textContent = (data.engine_used || 'AI').toUpperCase();
      engineBadge.className = 'text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold uppercase tracking-wider';
    }

    if (summaryEl) {
      summaryEl.textContent = data.raw_reasoning_summary || 'Chores successfully allocated.';
    }

    // 3. Render live preview of generated assignments
    renderAllocationPreview(data.assignments || []);

    // 4. Automatically refresh the Chore Board
    await loadAssignments();

  } catch (err) {
    if (errorAlert) {
      errorAlert.classList.remove('hidden');
      if (errorMessage) {
        errorMessage.textContent = err.message || 'Failed to run allocation. Please try again.';
      }
    }
  } finally {
    btn.disabled = false;
    if (notesArea) notesArea.disabled = false;
    if (spinner) spinner.classList.add('hidden');
    if (btnText) btnText.textContent = 'Run AI Allocation';
  }
}

// Initialization on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  const btnAllocate = document.getElementById('btn-allocate');
  if (btnAllocate) {
    btnAllocate.addEventListener('click', handleAllocate);
  }

  // Load initial assignments onto the Chore Board
  loadAssignments();
});

// Export functions for testability / modularity if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getCsrfToken,
    escapeHtml,
    getEffortInfo,
    getEmptyStateHtml,
    createAssignmentCard,
    handleMarkDone,
    updateBoardCounts,
    renderChoreBoard,
    loadAssignments,
    renderAllocationPreview,
    handleAllocate,
  };
}
