# Încărcare proiect pe GitHub

## 1. Creează repository-ul pe GitHub

1. Mergi la [github.com/new](https://github.com/new).
2. **Repository name:** `doisense` (sau alt nume).
3. Lasă **empty** (fără README, fără .gitignore).
4. Apasă **Create repository**.

## 2. Conectează și urcă din proiect

Înlocuiește `USERNAME` cu username-ul tău GitHub (sau organizația).

```bash
cd /opt/projects/doisense

# Adaugă remote (folosește URL-ul afișat de GitHub după ce creezi repo-ul)
git remote add origin https://github.com/USERNAME/doisense.git

# Prima încărcare
git push -u origin main
```

Dacă folosești SSH:

```bash
git remote add origin git@github.com:USERNAME/doisense.git
git push -u origin main
```

După asta, proiectul va fi pe GitHub și poți face ulterior `git push` / `git pull` normal.
