// frontend/mainview/src/App.jsx
import React, { useState } from "react";
import templates from "./templatesData";
import { registerUser, createProject } from "./api";

export default function App(){
  const [user, setUser] = useState("");
  const [passw, setPassw] = useState("");
  const [projectName, setProjectName] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState(templates[0].id);
  const [repoUrl, setRepoUrl] = useState("");
  const [output, setOutput] = useState("");

  const chooseTemplate = (tpl) => {
    setSelectedTemplate(tpl.id);
    // prefill example repo url so user can copy/edit
    setRepoUrl(tpl.exampleRepo);
  }

  const handleCreate = async () => {
    setOutput("Creando... (puede tardar unos segundos mientras se construye la imagen)");
    try {
      await registerUser(user, passw); // ignora si ya existe
      const r = await createProject(user, projectName, repoUrl, selectedTemplate);
      setOutput(JSON.stringify(r, null, 2));
    } catch (e) {
      setOutput("Error: " + e.message);
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: "30px auto", fontFamily: "Arial" }}>
      <h1>Panel Hosting</h1>

      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <h2>Plantillas (elige una)</h2>
          {templates.map(t => (
            <div key={t.id} style={{ border: t.id === selectedTemplate ? "2px solid #0077ff" : "1px solid #ddd", padding: 8, marginBottom: 8 }}>
              <strong>{t.name}</strong>
              <p style={{ marginTop: 6 }}>{t.description}</p>
              <button onClick={() => chooseTemplate(t)}>Usar plantilla</button>
            </div>
          ))}
        </div>

        <div style={{ flex: 1 }}>
          <h2>Crear proyecto</h2>
          <input placeholder="Usuario" value={user} onChange={e=>setUser(e.target.value)} style={{ width: "100%", padding:8, marginBottom:8 }}/>
          <input placeholder="Contraseña" type="password" value={passw} onChange={e=>setPassw(e.target.value)} style={{ width: "100%", padding:8, marginBottom:8 }}/>
          <input placeholder="Nombre del proyecto" value={projectName} onChange={e=>setProjectName(e.target.value)} style={{ width: "100%", padding:8, marginBottom:8 }}/>
          <input placeholder="URL del repo (pega aquí la URL del template seleccionado)" value={repoUrl} onChange={e=>setRepoUrl(e.target.value)} style={{ width: "100%", padding:8, marginBottom:8 }}/>
          <div style={{ display:"flex", gap:8 }}>
            <button onClick={handleCreate}>Crear proyecto</button>
          </div>
          <h3>Salida</h3>
          <pre style={{ background: "#f4f4f4", padding: 8 }}>{output}</pre>
        </div>
      </div>
    </div>
  )
}
