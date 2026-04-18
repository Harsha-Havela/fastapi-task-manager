from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import auth, tasks

# Import models so SQLAlchemy registers them before creating tables
import app.models.user  # noqa: F401
import app.models.task  # noqa: F401

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="A simple Task Manager REST API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow all origins for development; tighten in production via env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth & task routes
app.include_router(auth.router)
app.include_router(tasks.router)

# Simple root endpoint to serve frontend content
@app.get("/", include_in_schema=False)
def serve_frontend():
    # Complete Task Manager Frontend
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Task Manager</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: #f0f2f5;
      color: #1a1a2e;
      min-height: 100vh;
      padding: 24px 16px;
    }

    .container { max-width: 540px; margin: 0 auto; }
    h1 { font-size: 1.8rem; margin-bottom: 20px; color: #2d3a8c; }
    h2 { font-size: 1.1rem; margin-bottom: 14px; color: #374151; }

    .card {
      background: #fff;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }

    .tabs { display: flex; gap: 8px; margin-bottom: 20px; }
    .tab-btn {
      flex: 1; padding: 10px;
      border: 2px solid #2d3a8c;
      background: transparent; color: #2d3a8c;
      border-radius: 6px; cursor: pointer;
      font-weight: 600; font-size: .95rem;
      transition: background .15s, color .15s;
    }
    .tab-btn.active { background: #2d3a8c; color: #fff; }

    form { display: flex; flex-direction: column; gap: 10px; }
    label { font-size: .85rem; font-weight: 600; color: #374151; }
    input, textarea {
      padding: 9px 12px;
      border: 1.5px solid #d1d5db;
      border-radius: 6px; font-size: .95rem;
      transition: border-color .15s; width: 100%;
    }
    input:focus, textarea:focus { outline: none; border-color: #2d3a8c; }
    textarea { resize: vertical; }

    button[type="submit"] {
      padding: 10px; background: #2d3a8c;
      color: #fff; border: none; border-radius: 6px;
      font-size: .95rem; font-weight: 600;
      cursor: pointer; transition: background .15s;
    }
    button[type="submit"]:hover { background: #1e2a6e; }

    .app-header {
      display: flex; justify-content: space-between;
      align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;
    }
    .app-header div { display: flex; align-items: center; gap: 10px; }
    #welcome-msg { font-size: .9rem; color: #6b7280; }
    #logout-btn {
      padding: 7px 14px; background: #ef4444;
      color: #fff; border: none; border-radius: 6px;
      cursor: pointer; font-weight: 600; font-size: .85rem;
    }
    #logout-btn:hover { background: #dc2626; }

    .filter-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
    .filter-bar span { font-size: .85rem; font-weight: 600; color: #6b7280; }
    .filter-btn {
      padding: 5px 14px; border: 1.5px solid #d1d5db;
      background: #fff; border-radius: 20px;
      cursor: pointer; font-size: .85rem; transition: all .15s;
    }
    .filter-btn.active { background: #2d3a8c; color: #fff; border-color: #2d3a8c; }

    .task-item {
      background: #fff; border-radius: 10px;
      padding: 14px 16px; margin-bottom: 10px;
      box-shadow: 0 1px 4px rgba(0,0,0,.07);
      display: flex; align-items: flex-start; gap: 12px;
    }
    .task-item.completed .task-title { text-decoration: line-through; color: #9ca3af; }
    .task-check {
      width: 22px; height: 22px;
      border: 2px solid #2d3a8c; border-radius: 50%;
      cursor: pointer; flex-shrink: 0; margin-top: 2px;
      display: flex; align-items: center; justify-content: center;
      transition: background .15s;
    }
    .task-check.checked { background: #2d3a8c; }
    .task-check.checked::after { content: "✓"; color: #fff; font-size: .75rem; }
    .task-body { flex: 1; min-width: 0; }
    .task-title { font-weight: 600; font-size: .95rem; word-break: break-word; }
    .task-desc { font-size: .85rem; color: #6b7280; margin-top: 3px; word-break: break-word; }
    .task-meta { font-size: .75rem; color: #9ca3af; margin-top: 4px; }
    .task-actions { display: flex; gap: 6px; flex-shrink: 0; }
    .btn-delete {
      padding: 5px 10px; background: #fee2e2;
      color: #dc2626; border: none; border-radius: 5px;
      cursor: pointer; font-size: .8rem; font-weight: 600;
    }
    .btn-delete:hover { background: #fecaca; }

    .pagination { display: flex; justify-content: center; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
    .page-btn {
      padding: 6px 12px; border: 1.5px solid #d1d5db;
      background: #fff; border-radius: 6px; cursor: pointer; font-size: .85rem;
    }
    .page-btn.active { background: #2d3a8c; color: #fff; border-color: #2d3a8c; }
    .page-btn:disabled { opacity: .4; cursor: default; }

    .hidden { display: none !important; }
    .error { color: #dc2626; font-size: .85rem; margin-top: 6px; }
    .success { color: #16a34a; font-size: .85rem; margin-top: 6px; }
    .empty-state { text-align: center; color: #9ca3af; padding: 32px 0; font-size: .95rem; }

    @media (max-width: 480px) {
      .app-header { flex-direction: column; align-items: flex-start; }
      .task-item { flex-wrap: wrap; }
    }
  </style>
</head>
<body>

  <!-- Auth Section -->
  <div id="auth-section" class="container">
    <h1>Task Manager</h1>

    <div class="tabs">
      <button class="tab-btn active" id="tab-login-btn" onclick="showTab('login')">Login</button>
      <button class="tab-btn" id="tab-register-btn" onclick="showTab('register')">Register</button>
    </div>

    <!-- Login -->
    <div id="login-tab" class="card">
      <h2>Login</h2>
      <form id="login-form">
        <label>Username</label>
        <input type="text" id="login-username" required placeholder="your_username" />
        <label>Password</label>
        <input type="password" id="login-password" required placeholder="••••••" />
        <button type="submit">Login</button>
      </form>
      <p id="login-error" class="error hidden"></p>
    </div>

    <!-- Register -->
    <div id="register-tab" class="card hidden">
      <h2>Register</h2>
      <form id="register-form">
        <label>Username</label>
        <input type="text" id="reg-username" required placeholder="your_username" />
        <label>Email</label>
        <input type="email" id="reg-email" required placeholder="you@example.com" />
        <label>Password</label>
        <input type="password" id="reg-password" required placeholder="min 6 characters" />
        <button type="submit">Register</button>
      </form>
      <p id="register-error" class="error hidden"></p>
      <p id="register-success" class="success hidden"></p>
    </div>
  </div>

  <!-- App Section -->
  <div id="app-section" class="container hidden">
    <div class="app-header">
      <h1>My Tasks</h1>
      <div>
        <span id="welcome-msg"></span>
        <button id="logout-btn" onclick="logout()">Logout</button>
      </div>
    </div>

    <!-- Create Task -->
    <div class="card">
      <h2>New Task</h2>
      <form id="create-task-form">
        <label>Title</label>
        <input type="text" id="task-title" required placeholder="Task title" />
        <label>Description (optional)</label>
        <textarea id="task-desc" placeholder="Task description…" rows="2"></textarea>
        <button type="submit">Add Task</button>
      </form>
      <p id="create-error" class="error hidden"></p>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <span>Filter:</span>
      <button class="filter-btn active" onclick="setFilter('all', this)">All</button>
      <button class="filter-btn" onclick="setFilter('false', this)">Pending</button>
      <button class="filter-btn" onclick="setFilter('true', this)">Completed</button>
    </div>

    <!-- Task List -->
    <div id="task-list"></div>
    <div id="pagination" class="pagination"></div>
  </div>

  <script>
    const API_BASE = "";
    let token = localStorage.getItem("tm_token") || null;
    let currentUser = localStorage.getItem("tm_user") || null;
    let currentFilter = "all";
    let currentPage = 1;
    const PAGE_SIZE = 10;

    document.addEventListener("DOMContentLoaded", () => {
      if (token) showApp();
      document.getElementById("login-form").addEventListener("submit", handleLogin);
      document.getElementById("register-form").addEventListener("submit", handleRegister);
      document.getElementById("create-task-form").addEventListener("submit", handleCreateTask);
    });

    function showTab(tab) {
      const isLogin = tab === "login";
      document.getElementById("login-tab").classList.toggle("hidden", !isLogin);
      document.getElementById("register-tab").classList.toggle("hidden", isLogin);
      document.getElementById("tab-login-btn").classList.toggle("active", isLogin);
      document.getElementById("tab-register-btn").classList.toggle("active", !isLogin);
    }

    async function handleRegister(e) {
      e.preventDefault();
      clearMsg("register-error"); clearMsg("register-success");
      const username = document.getElementById("reg-username").value.trim();
      const email    = document.getElementById("reg-email").value.trim();
      const password = document.getElementById("reg-password").value;
      const resp = await apiFetch("/register", "POST", { username, email, password });
      if (resp.ok) {
        showMsg("register-success", "Account created! You can now log in.");
        document.getElementById("register-form").reset();
      } else {
        showMsg("register-error", extractError(await resp.json()));
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
        localStorage.setItem("tm_token", token);
        localStorage.setItem("tm_user", username);
        showApp();
      } else {
        showMsg("login-error", extractError(await resp.json()));
      }
    }

    function logout() {
      token = null; currentUser = null;
      localStorage.removeItem("tm_token");
      localStorage.removeItem("tm_user");
      document.getElementById("app-section").classList.add("hidden");
      document.getElementById("auth-section").classList.remove("hidden");
      document.getElementById("login-form").reset();
    }

    function showApp() {
      document.getElementById("auth-section").classList.add("hidden");
      document.getElementById("app-section").classList.remove("hidden");
      document.getElementById("welcome-msg").textContent = "Hi, " + currentUser;
      currentPage = 1;
      loadTasks();
    }

    async function loadTasks() {
      let url = "/tasks?page=" + currentPage + "&page_size=" + PAGE_SIZE;
      if (currentFilter !== "all") url += "&completed=" + currentFilter;
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
      list.innerHTML = tasks.map(t => `
        <div class="task-item ${t.completed ? "completed" : ""}" id="task-${t.id}">
          <div class="task-check ${t.completed ? "checked" : ""}"
               onclick="toggleComplete(${t.id}, ${t.completed})" title="Toggle complete"></div>
          <div class="task-body">
            <div class="task-title">${escHtml(t.title)}</div>
            ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ""}
            <div class="task-meta">${new Date(t.created_at).toLocaleString()}</div>
          </div>
          <div class="task-actions">
            <button class="btn-delete" onclick="deleteTask(${t.id})">Delete</button>
          </div>
        </div>`).join("");
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

    function goPage(page) { currentPage = page; loadTasks(); }

    function setFilter(filter, btn) {
      currentFilter = filter; currentPage = 1;
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadTasks();
    }

    async function handleCreateTask(e) {
      e.preventDefault();
      clearMsg("create-error");
      const title       = document.getElementById("task-title").value.trim();
      const description = document.getElementById("task-desc").value.trim() || null;
      const resp = await apiFetch("/tasks", "POST", { title, description });
      if (resp.ok) {
        document.getElementById("create-task-form").reset();
        currentPage = 1; loadTasks();
      } else {
        showMsg("create-error", extractError(await resp.json()));
      }
    }

    async function toggleComplete(id, currentState) {
      const resp = await apiFetch("/tasks/" + id, "PUT", { completed: !currentState });
      if (resp.ok) loadTasks();
    }

    async function deleteTask(id) {
      if (!confirm("Delete this task?")) return;
      const resp = await apiFetch("/tasks/" + id, "DELETE");
      if (resp.ok || resp.status === 204) loadTasks();
    }

    async function apiFetch(path, method = "GET", body = null) {
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = "Bearer " + token;
      const opts = { method, headers };
      if (body && method !== "GET") opts.body = JSON.stringify(body);
      return fetch(API_BASE + path, opts);
    }

    function extractError(err) {
      if (typeof err.detail === "string") return err.detail;
      if (Array.isArray(err.detail)) return err.detail.map(e => e.msg).join(", ");
      return "An unexpected error occurred.";
    }

    function showMsg(id, msg) {
      const el = document.getElementById(id);
      el.textContent = msg; el.classList.remove("hidden");
    }

    function clearMsg(id) {
      const el = document.getElementById(id);
      el.textContent = ""; el.classList.add("hidden");
    }

    function escHtml(str) {
      return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    }
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
