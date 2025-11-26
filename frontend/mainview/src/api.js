// frontend/mainview/src/api.js
const API = "http://localhost:5000";

export async function registerUser(username, password) {
  return fetch(`${API}/register`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  }).then(r => r.json());
}

export async function loginUser(username, password) {
  return fetch(`${API}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  }).then(r => r.json());
}

// ⛔ YA NO enviamos username en el body (el backend no lo usa)
export async function createProject(projectName, repoUrl, templateId="") {
  return fetch(`${API}/create-project`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": localStorage.getItem("token") || "" // token = username
    },
    body: JSON.stringify({
      projectName,
      repoUrl,
      templateId
    })
  }).then(r => r.json());
}

export async function pingProject(projectName) {
  return fetch(`${API}/ping-project`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": localStorage.getItem("token") || ""
    },
    body: JSON.stringify({ projectName })
  }).then(r => r.json());
}
