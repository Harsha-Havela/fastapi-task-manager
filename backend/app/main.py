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

# Frontend route - serves the main application
@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the main frontend application"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Task Manager</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #2d3748;
      min-height: 100vh;
      padding: 20px;
      line-height: 1.6;
    }

    .container { 
      max-width: 480px; 
      margin: 0 auto; 
      padding: 20px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    
    h1 { 
      font-size: 2.5rem; 
      margin-bottom: 30px; 
      color: #ffffff;
      text-align: center;
      font-weight: 700;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 { 
      font-size: 1.5rem; 
      margin-bottom: 20px; 
      color: #2d3748;
      font-weight: 600;
    }

    .card {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 16px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: all 0.3s ease;
    }

    .card h2 { 
      font-size: 1.3rem; 
      margin-bottom: 16px; 
      color: #2d3748;
      font-weight: 600;
    }

    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
    }

    .tabs { 
      display: flex; 
      gap: 12px; 
      margin-bottom: 30px; 
      background: rgba(255, 255, 255, 0.1);
      padding: 6px;
      border-radius: 16px;
      backdrop-filter: blur(10px);
    }
    
    .tab-btn {
      flex: 1; 
      padding: 14px 20px;
      border: none;
      background: transparent; 
      color: rgba(255, 255, 255, 0.8);
      border-radius: 12px; 
      cursor: pointer;
      font-weight: 600; 
      font-size: 1rem;
      transition: all 0.3s ease;
      position: relative;
    }
    
    .tab-btn.active { 
      background: rgba(255, 255, 255, 0.2); 
      color: #ffffff;
      transform: scale(1.02);
    }

    .tab-btn:hover:not(.active) {
      background: rgba(255, 255, 255, 0.1);
      color: #ffffff;
    }

    form { 
      display: flex; 
      flex-direction: column; 
      gap: 12px; 
    }
    
    label { 
      font-size: 0.9rem; 
      font-weight: 600; 
      color: #4a5568;
      margin-bottom: 6px;
    }
    
    input, textarea {
      padding: 16px 20px;
      border: 2px solid #e2e8f0;
      border-radius: 12px; 
      font-size: 1rem;
      transition: all 0.3s ease; 
      width: 100%;
      background: #ffffff;
      font-family: inherit;
    }
    
    input:focus, textarea:focus { 
      outline: none; 
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      transform: translateY(-1px);
    }
    
    textarea { 
      resize: vertical; 
      min-height: 80px;
    }

    button[type="submit"] {
      padding: 16px 24px; 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #ffffff; 
      border: none; 
      border-radius: 12px;
      font-size: 1rem; 
      font-weight: 600;
      cursor: pointer; 
      transition: all 0.3s ease;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      position: relative;
      overflow: hidden;
    }
    
    button[type="submit"]:hover { 
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }

    button[type="submit"]:active {
      transform: translateY(0);
    }

    .app-header {
      display: flex; 
      justify-content: space-between;
      align-items: center; 
      margin-bottom: 16px; 
      flex-wrap: wrap; 
      gap: 15px;
      background: rgba(255, 255, 255, 0.1);
      padding: 16px 20px;
      border-radius: 16px;
      backdrop-filter: blur(10px);
    }
    
    .app-header h1 {
      font-size: 1.6rem;
      margin: 0;
      color: #ffffff;
    }
    
    .app-header div { 
      display: flex; 
      align-items: center; 
      gap: 15px; 
    }
    
    #welcome-msg { 
      font-size: 1rem; 
      color: rgba(255, 255, 255, 0.9);
      font-weight: 500;
    }
    
    #logout-btn {
      padding: 10px 20px; 
      background: rgba(239, 68, 68, 0.9);
      color: #ffffff; 
      border: none; 
      border-radius: 10px;
      cursor: pointer; 
      font-weight: 600; 
      font-size: 0.9rem;
      transition: all 0.3s ease;
    }
    
    #logout-btn:hover { 
      background: #dc2626;
      transform: translateY(-1px);
    }

    .filter-bar { 
      display: flex; 
      align-items: center; 
      gap: 10px; 
      margin-bottom: 16px; 
      flex-wrap: wrap;
      background: rgba(255, 255, 255, 0.1);
      padding: 12px 16px;
      border-radius: 12px;
      backdrop-filter: blur(10px);
    }
    
    .filter-bar span { 
      font-size: 0.9rem; 
      font-weight: 600; 
      color: rgba(255, 255, 255, 0.9);
    }
    
    .filter-btn {
      padding: 8px 16px; 
      border: 2px solid rgba(255, 255, 255, 0.3);
      background: transparent; 
      border-radius: 25px;
      cursor: pointer; 
      font-size: 0.9rem; 
      transition: all 0.3s ease;
      color: rgba(255, 255, 255, 0.8);
      font-weight: 500;
    }
    
    .filter-btn.active { 
      background: rgba(255, 255, 255, 0.2); 
      color: #ffffff; 
      border-color: rgba(255, 255, 255, 0.5);
      transform: scale(1.05);
    }

    .filter-btn:hover:not(.active) {
      background: rgba(255, 255, 255, 0.1);
      color: #ffffff;
    }

    .task-item {
      background: rgba(255, 255, 255, 0.95);
      border-radius: 16px;
      padding: 20px 24px; 
      margin-bottom: 16px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      display: flex; 
      align-items: flex-start; 
      gap: 16px;
      transition: all 0.3s ease;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .task-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .task-item.completed .task-title { 
      text-decoration: line-through; 
      color: #9ca3af; 
    }
    
    .task-check {
      width: 24px; 
      height: 24px;
      border: 2px solid #667eea; 
      border-radius: 50%;
      cursor: pointer; 
      flex-shrink: 0; 
      margin-top: 2px;
      display: flex; 
      align-items: center; 
      justify-content: center;
      transition: all 0.3s ease;
      background: #ffffff;
    }
    
    .task-check:hover {
      transform: scale(1.1);
      border-color: #5a67d8;
    }
    
    .task-check.checked { 
      background: #667eea;
      border-color: #667eea;
    }
    
    .task-check.checked::after { 
      content: "✓"; 
      color: #ffffff; 
      font-size: 0.8rem; 
      font-weight: bold;
    }
    
    .task-body { 
      flex: 1; 
      min-width: 0; 
    }
    
    .task-title { 
      font-weight: 600; 
      font-size: 1.1rem; 
      word-break: break-word;
      color: #2d3748;
      margin-bottom: 4px;
    }
    
    .task-desc { 
      font-size: 0.95rem; 
      color: #718096; 
      margin-top: 6px; 
      word-break: break-word;
      line-height: 1.5;
    }
    
    .task-meta { 
      font-size: 0.8rem; 
      color: #a0aec0; 
      margin-top: 8px;
      font-weight: 500;
    }
    
    .task-actions { 
      display: flex; 
      gap: 8px; 
      flex-shrink: 0; 
    }
    
    .btn-delete {
      padding: 8px 16px; 
      background: rgba(239, 68, 68, 0.1);
      color: #e53e3e; 
      border: 1px solid rgba(239, 68, 68, 0.2); 
      border-radius: 8px;
      cursor: pointer; 
      font-size: 0.85rem; 
      font-weight: 600;
      transition: all 0.3s ease;
    }
    
    .btn-delete:hover { 
      background: rgba(239, 68, 68, 0.2);
      transform: translateY(-1px);
    }

    .pagination { 
      display: flex; 
      justify-content: center; 
      gap: 8px; 
      margin-top: 24px; 
      flex-wrap: wrap; 
    }
    
    .page-btn {
      padding: 10px 16px; 
      border: 2px solid rgba(255, 255, 255, 0.3);
      background: rgba(255, 255, 255, 0.1); 
      border-radius: 10px; 
      cursor: pointer; 
      font-size: 0.9rem;
      color: rgba(255, 255, 255, 0.8);
      font-weight: 500;
      transition: all 0.3s ease;
      backdrop-filter: blur(10px);
    }
    
    .page-btn.active { 
      background: rgba(255, 255, 255, 0.2); 
      color: #ffffff; 
      border-color: rgba(255, 255, 255, 0.5);
      transform: scale(1.05);
    }
    
    .page-btn:disabled { 
      opacity: 0.4; 
      cursor: default; 
      transform: none;
    }

    .page-btn:hover:not(.active):not(:disabled) {
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
    }

    .hidden { 
      display: none !important; 
    }
    
    .error { 
      color: #e53e3e; 
      font-size: 0.9rem; 
      margin-top: 8px;
      padding: 12px 16px;
      background: rgba(239, 68, 68, 0.1);
      border-radius: 8px;
      border-left: 4px solid #e53e3e;
    }
    
    .success { 
      color: #38a169; 
      font-size: 0.9rem; 
      margin-top: 8px;
      padding: 12px 16px;
      background: rgba(56, 161, 105, 0.1);
      border-radius: 8px;
      border-left: 4px solid #38a169;
    }
    
    .empty-state { 
      text-align: center; 
      color: rgba(255, 255, 255, 0.7); 
      padding: 40px 20px; 
      font-size: 1.1rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      backdrop-filter: blur(10px);
    }

    .stats-bar {
      display: flex;
      justify-content: space-around;
      align-items: center;
      background: rgba(255, 255, 255, 0.1);
      padding: 12px 16px;
      border-radius: 12px;
      margin-bottom: 16px;
      backdrop-filter: blur(10px);
      gap: 16px;
    }

    .stat-item {
      text-align: center;
      flex: 1;
    }

    .stat-number {
      display: block;
      font-size: 1.5rem;
      font-weight: 700;
      color: #ffffff;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .stat-label {
      display: block;
      font-size: 0.75rem;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 2px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .auth-switch {
      text-align: center;
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
      color: #718096;
      font-size: 0.95rem;
    }

    .auth-link {
      color: #667eea;
      text-decoration: none;
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .auth-link:hover {
      color: #5a67d8;
      text-decoration: underline;
    }

    .compact-card {
      padding: 16px !important;
    }

    .compact-card h2 {
      margin-bottom: 12px !important;
      font-size: 1.2rem !important;
    }

    .compact-card form {
      gap: 10px !important;
    }

    .compact-card input, .compact-card textarea {
      padding: 10px 14px !important;
      font-size: 0.9rem !important;
      border-radius: 8px !important;
    }

    .compact-card textarea {
      min-height: 50px !important;
    }

    .compact-card button {
      padding: 10px 16px !important;
      font-size: 0.9rem !important;
      border-radius: 8px !important;
    }

    .task-container {
      flex: 1;
      overflow-y: auto;
      max-height: 300px;
      padding-right: 4px;
    }

    .task-container::-webkit-scrollbar {
      width: 6px;
    }

    .task-container::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
    }

    .task-container::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 3px;
    }

    .task-container::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.5);
    }

    @media (max-width: 480px) {
      .container {
        padding-top: 20px;
      }
      
      h1 {
        font-size: 2rem;
      }
      
      .card {
        padding: 24px 20px;
      }
      
      .app-header { 
        flex-direction: column; 
        align-items: flex-start; 
        text-align: center;
      }
      
      .task-item { 
        flex-wrap: wrap; 
        padding: 16px 20px;
      }
      
      .filter-bar {
        justify-content: center;
      }
    }

    /* Loading animation */
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: #ffffff;
      animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Smooth transitions */
    * {
      transition: all 0.3s ease;
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
      <div class="auth-switch">
        <span>Don't have an account? </span>
        <a href="#" onclick="showTab('register')" class="auth-link">Register</a>
      </div>
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
      <div class="auth-switch">
        <span>Already have an account? </span>
        <a href="#" onclick="showTab('login')" class="auth-link">Login</a>
      </div>
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

    <!-- Task Statistics - Top Priority -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-number" id="total-count">0</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-item">
        <span class="stat-number" id="pending-count">0</span>
        <span class="stat-label">Pending</span>
      </div>
      <div class="stat-item">
        <span class="stat-number" id="completed-count">0</span>
        <span class="stat-label">Completed</span>
      </div>
    </div>

    <!-- Create Task -->
    <div class="card compact-card">
      <h2>New Task</h2>
      <form id="create-task-form">
        <input type="text" id="task-title" required placeholder="Task title" />
        <textarea id="task-desc" placeholder="Task description (optional)…" rows="2"></textarea>
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

    <!-- Task List Container -->
    <div class="task-container">
      <div id="task-list"></div>
      <div id="pagination" class="pagination"></div>
    </div>
  </div>

    <script>
  const API_BASE = "";
  let token = localStorage.getItem("tm_token") || null;
  let currentUser = localStorage.getItem("tm_user") || null;
  let currentFilter = "all";
  let currentPage = 1;
  const PAGE_SIZE = 10;

  document.addEventListener("DOMContentLoaded", () => {
    if (token){
      showApp();
    }

    document.getElementById("login-form").addEventListener("submit", handleLogin);
    document.getElementById("register-form").addEventListener("submit", handleRegister);
    document.getElementById("create-task-form").addEventListener("submit", handleCreateTask);
  });


  function showTab(tab){
    const isLogin = tab==="login";

    document.getElementById("login-tab").classList.toggle("hidden", !isLogin);
    document.getElementById("register-tab").classList.toggle("hidden", isLogin);

    document.getElementById("tab-login-btn").classList.toggle("active", isLogin);
    document.getElementById("tab-register-btn").classList.toggle("active", !isLogin);
  }


  async function handleRegister(e){
  e.preventDefault();

  clearMsg("register-error");
  clearMsg("register-success");

  const username=document.getElementById("reg-username").value.trim();
  const email=document.getElementById("reg-email").value.trim();
  const password=document.getElementById("reg-password").value;

  const resp=await apiFetch("/register","POST",{
  username,
  email,
  password
  });

  if(resp.ok){

  showMsg("register-success","Account created successfully!");

  document.getElementById("register-form").reset();

  setTimeout(()=>{
  showTab("login");
  document.getElementById("login-username").value=username;
  },2000);

  }
  else{
  showMsg("register-error",extractError(await resp.json()));
  }
  }



  async function handleLogin(e){

  e.preventDefault();

  clearMsg("login-error");

  const username=document.getElementById("login-username").value.trim();
  const password=document.getElementById("login-password").value;

  const resp=await apiFetch("/login","POST",{
  username,
  password
  });

  if(resp.ok){

  const data=await resp.json();

  token=data.access_token;
  currentUser=username;

  localStorage.setItem("tm_token",token);
  localStorage.setItem("tm_user",username);

  showApp();

  }
  else{
  showMsg("login-error",extractError(await resp.json()));
  }

  }



  function logout(){

  token=null;
  currentUser=null;

  localStorage.removeItem("tm_token");
  localStorage.removeItem("tm_user");

  document.getElementById("app-section").classList.add("hidden");
  document.getElementById("auth-section").classList.remove("hidden");

  }



  async function showApp(){

  document.getElementById("auth-section").classList.add("hidden");
  document.getElementById("app-section").classList.remove("hidden");

  document.getElementById("welcome-msg").textContent="Hi, "+currentUser;

  currentPage=1;

  await loadTasks();

  await updateTaskStats();

  }



  async function loadTasks(){

  let url="/tasks?page="+currentPage+"&page_size="+PAGE_SIZE;

  if(currentFilter!="all"){
  url+="&completed="+currentFilter;
  }

  const resp=await apiFetch(url,"GET");

  if(resp.status===401){
  logout();
  return;
  }

  const data=await resp.json();

  renderTasks(data.tasks);

  renderPagination(data.total_pages);

  }




  function renderTasks(tasks){

  const list=document.getElementById("task-list");

  if(!tasks.length){
  list.innerHTML='<p class="empty-state">No tasks here yet.</p>';
  return;
  }

  list.innerHTML=tasks.map(t=>`

  <div class="task-item ${t.completed ? "completed":""}">

  <div class="task-check ${t.completed ? "checked":""}"
  onclick="toggleComplete(${t.id},${t.completed})"></div>

  <div class="task-body">

  <div class="task-title">
  ${escHtml(t.title)}
  </div>

  ${t.description ?
  `<div class="task-desc">${escHtml(t.description)}</div>`
  :""}

  <div class="task-meta">
  ${new Date(t.created_at).toLocaleString()}
  </div>

  </div>

  <div class="task-actions">
  <button class="btn-delete"
  onclick="deleteTask(${t.id})">
  Delete
  </button>
  </div>

  </div>

  `).join("");

  }




    async function updateTaskStats() {
      try {
        // Use the SAME API call that loads tasks - we know this works
        const resp = await apiFetch("/tasks?page=1&page_size=100", "GET");
        
        if (resp.ok) {
          const data = await resp.json();
          const tasks = data.tasks || [];
          
          // Count directly from the tasks we got
          const total = tasks.length;
          const completed = tasks.filter(t => t.completed === true).length;
          const pending = total - completed;
          
          // FORCE update the DOM
          document.getElementById("total-count").innerHTML = total;
          document.getElementById("pending-count").innerHTML = pending;
          document.getElementById("completed-count").innerHTML = completed;
        }
      } catch (err) {
        // If anything fails, just set to 0
        document.getElementById("total-count").innerHTML = "0";
        document.getElementById("pending-count").innerHTML = "0";
        document.getElementById("completed-count").innerHTML = "0";
      }
    }




  function renderPagination(totalPages){

  const pg=
  document.getElementById("pagination");

  if(totalPages<=1){
  pg.innerHTML="";
  return;
  }

  let html=
  `<button class="page-btn"
  onclick="goPage(${currentPage-1})"
  ${currentPage===1?"disabled":""}>
  Prev
  </button>`;


  for(let i=1;i<=totalPages;i++){

  html+=
  `<button class="page-btn ${i===currentPage?"active":""}"
  onclick="goPage(${i})">
  ${i}
  </button>`;

  }

  html+=
  `<button class="page-btn"
  onclick="goPage(${currentPage+1})"
  ${currentPage===totalPages?"disabled":""}>
  Next
  </button>`;

  pg.innerHTML=html;

  }



  function goPage(page){

  currentPage=page;

  loadTasks();

  }



  function setFilter(filter,btn){

  currentFilter=filter;

  currentPage=1;

  document.querySelectorAll(".filter-btn").forEach(
  b=>b.classList.remove("active")
  );

  btn.classList.add("active");

  loadTasks();

  }



  async function handleCreateTask(e){

  e.preventDefault();

  clearMsg("create-error");

  const title=
  document.getElementById("task-title").value.trim();

  const description=
  document.getElementById("task-desc").value.trim()||null;


  const resp=
  await apiFetch("/tasks","POST",{
  title,
  description
  });


  if(resp.ok){

  document.getElementById("create-task-form").reset();

  await loadTasks();

  await updateTaskStats();

  }
  else{

  showMsg("create-error",
  extractError(await resp.json())
  );

  }

  }



  async function toggleComplete(id,currentState){

  const resp=
  await apiFetch(
  "/tasks/"+id,
  "PUT",
  {
  completed:!currentState
  }
  );

  if(resp.ok){

  await loadTasks();

  await updateTaskStats();

  }

  }




  async function deleteTask(id){

  if(!confirm("Delete this task?")){
  return;
  }

  const resp=
  await apiFetch(
  "/tasks/"+id,
  "DELETE"
  );

  if(resp.ok || resp.status===204){

  await loadTasks();

  await updateTaskStats();

  }

  }




  async function apiFetch(path,method="GET",body=null){

  const headers={
  "Content-Type":"application/json"
  };

  if(token){
  headers["Authorization"]="Bearer "+token;
  }

  const opts={
  method,
  headers
  };

  if(body && method!=="GET"){
  opts.body=
  JSON.stringify(body);
  }

  return fetch(
  API_BASE+path,
  opts
  );

  }



  function extractError(err){

  if(typeof err.detail==="string"){
  return err.detail;
  }

  if(Array.isArray(err.detail)){
  return err.detail.map(
  e=>e.msg
  ).join(", ");
  }

  return "Unexpected error";

  }



  function showMsg(id,msg){

  const el=
  document.getElementById(id);

  el.textContent=msg;

  el.classList.remove("hidden");

  }



  function clearMsg(id){

  const el=
  document.getElementById(id);

  el.textContent="";

  el.classList.add("hidden");

  }



  function escHtml(str){
  return str
  .replace(/&/g,"&amp;")
  .replace(/</g,"&lt;")
  .replace(/>/g,"&gt;")
  .replace(/"/g,"&quot;");
  }

  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
