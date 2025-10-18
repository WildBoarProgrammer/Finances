#!/usr/bin/env python3
"""
Script per aggiungere un account di test al database.
"""

import sys
import os
import random

# Aggiungi il percorso dell'app al path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.database_service import DatabaseService
    from app.models.database import engine
    from sqlalchemy import text
    
    print("🏦 Aggiunta Account di Test")
    print("=" * 30)
    
    # Test connessione
    print("📡 Test connessione database...")
    with engine.connect():
        print("✅ Connessione riuscita!")
    
    # Crea l'account di test
    with DatabaseService() as db_service:
        print("➕ Creazione account di test...")
        
        # Valori randomici per i campi
        need_admin = random.choice([True, False])
        initial_balance = round(random.uniform(100.0, 50000.0), 2)
        in_tot = random.choice([True, False])
        
        # Crea l'account
        test_account = db_service.create_account(
            name="test_account",
            goal="test_goal", 
            initial_balance=initial_balance,
            need_admin=need_admin,
            in_tot=in_tot
        )
        
        print(f"✅ Account creato con successo!")
        print(f"   ID: {test_account.ID}")
        print(f"   Nome: {test_account.name}")
        print(f"   Goal: {test_account.goal}")
        print(f"   Saldo iniziale: €{test_account.initial_balance:.2f}")
        print(f"   Richiede admin: {test_account.need_admin}")
        print(f"   Incluso nel totale: {test_account.in_tot}")
        
        # Verifica il saldo calcolato
        current_balance = db_service.calculate_account_balance(test_account.ID)
        print(f"   Saldo corrente: €{current_balance:.2f}")
        
        # Mostra tutti gli account
        print("\n📋 Tutti gli account nel database:")
        all_accounts = db_service.get_all_accounts()
        for account in all_accounts:
            balance = db_service.calculate_account_balance(account.ID)
            print(f"   • {account.name} (ID: {account.ID}) - €{balance:.2f}")
    
    print("\n🎉 Account di test aggiunto con successo!")
    print("💡 Ricarica l'app Reflex per vedere il nuovo account nel dashboard.")
    
except Exception as e:
    print(f"❌ Errore: {str(e)}")
    print("\n🔧 Verifica:")
    print("1. PostgreSQL è in esecuzione")
    print("2. Il database 'finances_db' esiste e contiene le tabelle")
    print("3. Le credenziali nel .env sono corrette")