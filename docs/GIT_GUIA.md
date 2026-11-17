# Flujo Git sugerido

```bash
git init
git branch -M main
git add .
git commit -m "chore: iniciar estructura del proyecto PARKIA"
git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

Trabajar por funcionalidades en ramas:
```bash
git checkout -b feature/registro-vehiculos
# desarrollar y probar
git add .
git commit -m "feat: agregar registro de vehiculos"
git checkout main
git merge feature/registro-vehiculos
git push
```

No subir `.venv`, bases de datos reales, contraseñas ni archivos `.env`.
