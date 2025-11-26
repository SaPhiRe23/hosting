# backend/git_handler.py
import subprocess, shutil, os

def clone_repo(repo_url, target_dir):
    """
    Clona el repo en target_dir. Si ya existe, lo elimina y clona de nuevo.
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    # usamos git clone --depth 1 para rapidez
    cmd = ["git", "clone", "--depth", "1", repo_url, target_dir]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise Exception(proc.stderr.strip() or "git clone failed")
    return True
