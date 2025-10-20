#!/usr/bin/env python3
"""
Script per fare reset completo dell'app Reflex.
"""

import os
import shutil
import subprocess

print("🔄 Reset Completo App Reflex")
print("=" * 30)

# Rimuovi cartelle cache
cache_folders = ['.web', '.states', '__pycache__', 'app/__pycache__']

for folder in cache_folders:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"✅ Rimossa cartella cache: {folder}")
        except Exception as e:
            print(f"⚠️ Errore rimozione {folder}: {e}")

# Rimuovi file cache Python
for root, dirs, files in os.walk('.'):
    for d in dirs[:]:
        if d == '__pycache__':
            try:
                shutil.rmtree(os.path.join(root, d))
                dirs.remove(d)
                print(f"✅ Rimossa cache: {os.path.join(root, d)}")
            except:
                pass

print("\n🔄 Ricostruzione completa...")
try:
    subprocess.run(['reflex', 'init'], check=True)
    print("✅ App reinizializzata!")
except Exception as e:
    print(f"⚠️ Errore reinizializzazione: {e}")

print("\n🚀 Ora esegui: reflex run")