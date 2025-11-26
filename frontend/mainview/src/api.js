// frontend/mainview/src/api.js
const API = "http://localhost:5000";

export async function registerUser(username, password) {
  return fetch(`${API}/register`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ username, password })
  }).then(r => r.json());
}

export async function createProject(username, projectName, repoUrl, templateId="") {
  return fetch(`${API}/create-project`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username,
      projectName,
      repoUrl,
      templateId
    })
  }).then(r => r.json());
}

export async function pingProject(username, projectName) {
  return fetch(`${API}/ping-project`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ username, projectName })
  }).then(r => r.json());
}
