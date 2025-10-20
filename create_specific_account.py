#!/usr/bin/env python3
"""
Script per creare l'account specifico richiesto.
"""

import sys
import os

# Aggiungi il percorso dell'app al path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.database_service import DatabaseService
    from app.models.database import engine
    from sqlalchemy import text
    
    print("🏦 Creazione Account Specifico")
    print("=" * 35)
    
    # Test connessione
    print("📡 Test connessione database...")
    with engine.connect():
        print("✅ Connessione riuscita!")
    
    # Verifica che gli ENUM esistano
    print("🔍 Verifica schema database...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pg_type 
            WHERE typname IN ('CatType', 'TranStatus', 'RecurrenceType')
        """))
        enum_count = result.scalar()
        
        if enum_count < 3:
            print(f"❌ Schema incompleto! Trovati solo {enum_count}/3 ENUM types.")
            print("💡 Esegui prima: python setup_database_schema.py")
            sys.exit(1)
        else:
            print("✅ Schema database verificato!")
    
    # Crea l'account con le caratteristiche specificate
    with DatabaseService() as db_service:
        print("➕ Creazione account con caratteristiche specificate...")
        
        # Verifica se esiste già un account con questo nome
        existing_accounts = db_service.get_all_accounts()
        for acc in existing_accounts:
            if acc.name == "testname_0":
                print(f"⚠️ Account '{acc.name}' già esistente (ID: {acc.ID})")
                choice = input("Vuoi eliminarlo e ricrearlo? (y/N): ").lower().strip()
                if choice == 'y':
                    with db_service.db as session:
                        session.delete(acc)
                        session.commit()
                    print("🗑️ Account esistente eliminato")
                else:
                    print("❌ Operazione annullata")
                    sys.exit(0)
                break
        
        # Crea l'account con i parametri specificati
        specific_account = db_service.create_account(
            name="testname_0",
            goal="test_goal", 
            initial_balance=1000.00,
            need_admin=False,  # 0 = False
            in_tot=True       # 1 = True
        )
        
        print(f"✅ Account creato con successo!")
        print(f"   ID: {specific_account.ID}")
        print(f"   Nome: {specific_account.name}")
        print(f"   Goal: {specific_account.goal}")
        print(f"   Saldo iniziale: €{specific_account.initial_balance:.2f}")
        print(f"   Richiede admin: {specific_account.need_admin}")
        print(f"   Incluso nel totale: {specific_account.in_tot}")
        
        # Verifica il saldo calcolato (potrebbe fallire se non ci sono transazioni)
        try:
            current_balance = db_service.calculate_account_balance(specific_account.ID)
            print(f"   Saldo corrente: €{current_balance:.2f}")
        except Exception as balance_error:
            print(f"   ⚠️ Calcolo saldo: {balance_error}")
            print(f"   📝 Saldo iniziale: €{specific_account.initial_balance:.2f}")
        
        # Mostra tutti gli account nel database
        print("\n📋 Tutti gli account nel database:")
        all_accounts = db_service.get_all_accounts()
        for account in all_accounts:
            try:
                balance = db_service.calculate_account_balance(account.ID)
                status = "✅" if account.name == "testname_0" else "•"
                print(f"   {status} {account.name} (ID: {account.ID}) - €{balance:.2f}")
            except:
                # Se il calcolo fallisce, mostra solo il saldo iniziale
                print(f"   • {account.name} (ID: {account.ID}) - €{account.initial_balance:.2f} (iniziale)")
    
    print("\n🎉 Account specifico creato con successo!")
    print("💡 Caratteristiche inserite:")
    print("   • need_admin: 0 (False)")
    print("   • name: testname_0")
    print("   • goal: test_goal")
    print("   • initial_balance: 1000.00")
    print("   • in_tot: 1 (True)")
    print("\n🚀 Avvia l'app con 'reflex run' per vedere il nuovo account nel dashboard.")
    
except Exception as e:
    print(f"❌ Errore: {str(e)}")
    
    # Diagnosi più specifica
    if "ENUM" in str(e) or "enumeration" in str(e):
        print("\n🔧 PROBLEMA SCHEMA DATABASE:")
        print("Il database non ha gli ENUM types corretti.")
        print("SOLUZIONE:")
        print("1. Esegui: python setup_database_schema.py")
        print("2. Poi riprova: python create_specific_account.py")
    else:
        print("\n🔧 Verifica:")
        print("1. PostgreSQL è in esecuzione")
        print("2. Il database 'finances_db' esiste e contiene le tabelle")
        print("3. Le credenziali nel .env sono corrette")
        print("4. Hai eseguito 'python setup_database_schema.py' per lo schema")