// ── Configuration ─────────────────────────────────────────────────────────────
// When served from the same origin (FastAPI), use relative URLs.
// Override with window.API_BASE (set before this script) for separate deployments.
const API_BASE = window.API_BASE || "";

// ── State ─────────────────────────────────────────────────────────────────────
let token = localStorage.getItem("token") || null;
let currentUser = localStorage.getItem("username") || null;
let currentFilter = "all";
let currentPage = 1;
const PAGE_SIZE = 10;

// ── Bootstrap ─────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if (token) {
    showApp();
  }

  document.getElementById("login-form").addEventListener("submit", handleLogin);
  document.getElementById("register-form").addEventListener("submit", handleRegister);
  document.getElementById("create-task-form").addEventListener("submit", handleCreateTask);
});

// ── Tab switching ─────────────────────────────────────────────────────────────
function showTab(tabId) {
  document.querySelectorAll(".tab-content").forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach((el) => el.classList.remove("active"));
  document.getElementById(tabId).classList.remove("hidden");
  event.target.classList.add("active");
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function handleRegister(e) {
  e.preventDefault();
  clearMsg("register-error");
  clearMsg("register-success");

  const username = document.getElementById("reg-username").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;

  const resp = await apiFetch("/register", "POST", { username, email, password });
  if (resp.ok) {
    showMsg("register-success", "Account created! You can now log in.");
    document.getElementById("register-form").reset();
  } else {
    const err = await resp.json();
    showMsg("register-error", extractError(err));
  }
}

async function handleLogin(e) {
  e.preventDefault();
  clearMsg("login-error");

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  const resp = await apiFetch("/login", "POST", { username, password });
  if (resp.ok) {
    const data = await resp.json();
    token = data.access_token;
    currentUser = username;
    localStorage.setItem("token", token);
    localStorage.setItem("username", username);
    showApp();
  } else {
    const err = await resp.json();
    showMsg("login-error", extractError(err));
  }
}

function logout() {
  token = null;
  currentUser = null;
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  document.getElementById("app-section").classList.add("hidden");
  document.getElementById("auth-section").classList.remove("hidden");
  document.getElementById("login-form").reset();
}

// ── App view ──────────────────────────────────────────────────────────────────
function showApp() {
  document.getElementById("auth-section").classList.add("hidden");
  document.getElementById("app-section").classList.remove("hidden");
  document.getElementById("welcome-msg").textContent = `Hi, ${currentUser}`;
  currentPage = 1;
  loadTasks();
}

// ── Tasks ─────────────────────────────────────────────────────────────────────
async function loadTasks() {
  let url = `/tasks?page=${currentPage}&page_size=${PAGE_SIZE}`;
  if (currentFilter !== "all") url += `&completed=${currentFilter}`;

  const resp = await apiFetch(url, "GET");
  if (resp.status === 401) { logout(); return; }

  const data = await resp.json();
  renderTasks(data.tasks);
  renderPagination(data.total_pages);
}

function renderTasks(tasks) {
  const list = document.getElementById("task-list");
  if (!tasks.length) {
    list.innerHTML = '<p class="empty-state">No tasks here yet.</p>';
    return;
  }

  list.innerHTML = tasks
    .map(
      (t) => `
    <div class="task-item ${t.completed ? "completed" : ""}" id="task-${t.id}">
      <div class="task-check ${t.completed ? "checked" : ""}" onclick="toggleComplete(${t.id}, ${t.completed})" title="Toggle complete"></div>
      <div class="task-body">
        <div class="task-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ""}
        <div class="task-meta">${new Date(t.created_at).toLocaleString()}</div>
      </div>
      <div class="task-actions">
        <button class="btn-delete" onclick="deleteTask(${t.id})">Delete</button>
      </div>
    </div>`
    )
    .join("");
}

function renderPagination(totalPages) {
  const pg = document.getElementById("pagination");
  if (totalPages <= 1) { pg.innerHTML = ""; return; }

  let html = `<button class="page-btn" onclick="goPage(${currentPage - 1})" ${currentPage === 1 ? "disabled" : ""}>‹ Prev</button>`;
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn ${i === currentPage ? "active" : ""}" onclick="goPage(${i})">${i}</button>`;
  }
  html += `<button class="page-btn" onclick="goPage(${currentPage + 1})" ${currentPage === totalPages ? "disabled" : ""}>Next ›</button>`;
  pg.innerHTML = html;
}

function goPage(page) {
  currentPage = page;
  loadTasks();
}

function setFilter(filter, btn) {
  currentFilter = filter;
  currentPage = 1;
  document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  loadTasks();
}

async function handleCreateTask(e) {
  e.preventDefault();
  clearMsg("create-error");

  const title = document.getElementById("task-title").value.trim();
  const description = document.getElementById("task-desc").value.trim() || null;

  const resp = await apiFetch("/tasks", "POST", { title, description });
  if (resp.ok) {
    document.getElementById("create-task-form").reset();
    currentPage = 1;
    loadTasks();
  } else {
    const err = await resp.json();
    showMsg("create-error", extractError(err));
  }
}

async function toggleComplete(id, currentState) {
  const resp = await apiFetch(`/tasks/${id}`, "PUT", { completed: !currentState });
  if (resp.ok) loadTasks();
}

async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  const resp = await apiFetch(`/tasks/${id}`, "DELETE");
  if (resp.ok || resp.status === 204) loadTasks();
}

// ── Utilities ─────────────────────────────────────────────────────────────────
async function apiFetch(path, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body && method !== "GET") opts.body = JSON.stringify(body);

  return fetch(`${API_BASE}${path}`, opts);
}

function extractError(err) {
  if (typeof err.detail === "string") return err.detail;
  if (Array.isArray(err.detail)) return err.detail.map((e) => e.msg).join(", ");
  return "An unexpected error occurred.";
}

function showMsg(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove("hidden");
}

function clearMsg(id) {
  const el = document.getElementById(id);
  el.textContent = "";
  el.classList.add("hidden");
}

function escHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
