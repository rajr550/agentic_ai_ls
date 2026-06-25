// ===== DOM Elements =====
const taskForm = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const taskList = document.getElementById('task-list');
const taskCount = document.getElementById('task-count');
const clearAllBtn = document.getElementById('clear-all');
const toastContainer = document.getElementById('toast-container');

// ===== State =====
let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
  renderTasks();
});

// ===== Save to localStorage =====
function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

// ===== Toast Notifications =====
function showToast(message, type = 'success') {
  const icons = {
    success: '✅',
    error: '⚠️',
    info: 'ℹ️',
  };

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span class="toast__icon">${icons[type]}</span>
    <span>${message}</span>
  `;

  toastContainer.appendChild(toast);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    toast.classList.add('removing');
    toast.addEventListener('animationend', () => toast.remove());
  }, 3000);
}

// ===== Validate Input =====
function validateInput(text) {
  const trimmed = text.trim();

  if (!trimmed) {
    showToast('Task cannot be empty!', 'error');
    taskInput.classList.add('shake');
    setTimeout(() => taskInput.classList.remove('shake'), 400);
    return null;
  }

  if (trimmed.length < 2) {
    showToast('Task must be at least 2 characters.', 'error');
    taskInput.classList.add('shake');
    setTimeout(() => taskInput.classList.remove('shake'), 400);
    return null;
  }

  if (trimmed.length > 200) {
    showToast('Task is too long (max 200 characters).', 'error');
    return null;
  }

  // Check for duplicate
  const duplicate = tasks.find(
    (t) => t.text.toLowerCase() === trimmed.toLowerCase()
  );
  if (duplicate) {
    showToast('This task already exists!', 'error');
    taskInput.classList.add('shake');
    setTimeout(() => taskInput.classList.remove('shake'), 400);
    return null;
  }

  return trimmed;
}

// ===== Add Task =====
taskForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = validateInput(taskInput.value);
  if (!text) return;

  const task = {
    id: Date.now().toString(),
    text,
    completed: false,
    createdAt: new Date().toISOString(),
  };

  tasks.unshift(task);
  saveTasks();
  renderTasks();
  taskInput.value = '';
  taskInput.focus();
  showToast('Task added successfully!', 'success');
});

// ===== Toggle Complete =====
function toggleComplete(id) {
  const task = tasks.find((t) => t.id === id);
  if (task) {
    task.completed = !task.completed;
    saveTasks();
    renderTasks();
    showToast(
      task.completed ? 'Task marked as complete!' : 'Task marked as active.',
      'info'
    );
  }
}

// ===== Delete Task =====
function deleteTask(id) {
  const taskEl = document.querySelector(`[data-id="${id}"]`);
  if (taskEl) {
    taskEl.classList.add('removing');
    taskEl.addEventListener('animationend', () => {
      tasks = tasks.filter((t) => t.id !== id);
      saveTasks();
      renderTasks();
      showToast('Task deleted.', 'info');
    });
  }
}

// ===== Edit Task =====
function startEdit(id) {
  const task = tasks.find((t) => t.id === id);
  if (!task) return;

  const taskEl = document.querySelector(`[data-id="${id}"]`);
  const textEl = taskEl.querySelector('.task-item__text');
  const actionsEl = taskEl.querySelector('.task-item__actions');

  // Replace text with input
  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'task-item__edit-input';
  input.value = task.text;
  input.maxLength = 200;
  textEl.replaceWith(input);
  input.focus();
  input.select();

  // Replace action buttons
  actionsEl.innerHTML = `
    <button class="task-item__btn task-item__btn--save" onclick="saveEdit('${id}')" title="Save">💾</button>
    <button class="task-item__btn task-item__btn--delete" onclick="cancelEdit()" title="Cancel">✕</button>
  `;

  // Save on Enter, Cancel on Escape
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') saveEdit(id);
    if (e.key === 'Escape') cancelEdit();
  });
}

function saveEdit(id) {
  const taskEl = document.querySelector(`[data-id="${id}"]`);
  const input = taskEl.querySelector('.task-item__edit-input');
  const newText = input.value.trim();

  if (!newText) {
    showToast('Task cannot be empty!', 'error');
    input.classList.add('shake');
    setTimeout(() => input.classList.remove('shake'), 400);
    return;
  }

  if (newText.length < 2) {
    showToast('Task must be at least 2 characters.', 'error');
    return;
  }

  // Check for duplicate (excluding current task)
  const duplicate = tasks.find(
    (t) => t.id !== id && t.text.toLowerCase() === newText.toLowerCase()
  );
  if (duplicate) {
    showToast('This task already exists!', 'error');
    return;
  }

  const task = tasks.find((t) => t.id === id);
  if (task) {
    task.text = newText;
    saveTasks();
    renderTasks();
    showToast('Task updated!', 'success');
  }
}

function cancelEdit() {
  renderTasks();
}

// ===== Clear All =====
clearAllBtn.addEventListener('click', () => {
  if (tasks.length === 0) return;

  if (confirm('Are you sure you want to delete all tasks?')) {
    tasks = [];
    saveTasks();
    renderTasks();
    showToast('All tasks cleared.', 'info');
  }
});

// ===== Render =====
function renderTasks() {
  // Update count
  const activeTasks = tasks.filter((t) => !t.completed).length;
  taskCount.textContent = activeTasks;

  // Toggle clear button
  clearAllBtn.classList.toggle('hidden', tasks.length === 0);

  // Empty state
  if (tasks.length === 0) {
    taskList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">📋</div>
        <p class="empty-state__text">No tasks yet. Add one above!</p>
      </div>
    `;
    return;
  }

  // Render tasks
  taskList.innerHTML = tasks
    .map(
      (task) => `
    <div class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
      <input
        type="checkbox"
        class="task-item__checkbox"
        ${task.completed ? 'checked' : ''}
        onchange="toggleComplete('${task.id}')"
      />
      <span class="task-item__text">${escapeHTML(task.text)}</span>
      <div class="task-item__actions">
        <button class="task-item__btn task-item__btn--edit" onclick="startEdit('${task.id}')" title="Edit">✏️</button>
        <button class="task-item__btn task-item__btn--delete" onclick="deleteTask('${task.id}')" title="Delete">🗑️</button>
      </div>
    </div>
  `
    )
    .join('');
}

// ===== Utility: Escape HTML =====
function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
