#!/usr/bin/env python3
"""
Script di debug per verificare gli account nel database.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.database_service import DatabaseService
    from app.models.database import engine
    
    print("🔍 Debug Account Database")
    print("=" * 30)
    
    with engine.connect():
        print("✅ Connessione riuscita!")
    
    with DatabaseService() as db_service:
        print("\n📋 Tutti gli account nel database:")
        accounts = db_service.get_all_accounts()
        
        if not accounts:
            print("❌ Nessun account trovato nel database!")
        else:
            for account in accounts:
                try:
                    balance = db_service.calculate_account_balance(account.ID)
                    included = "✅" if account.in_tot else "❌"
                    admin = "🔒" if account.need_admin else "🔓"
                    
                    print(f"   • ID: {account.ID}")
                    print(f"     Nome: {account.name}")
                    print(f"     Goal: {account.goal}")
                    print(f"     Saldo iniziale: €{account.initial_balance:.2f}")
                    print(f"     Saldo corrente: €{balance:.2f}")
                    print(f"     Incluso nel totale: {included} ({account.in_tot})")
                    print(f"     Richiede admin: {admin} ({account.need_admin})")
                    print("     ---")
                    
                except Exception as e:
                    print(f"   ❌ Errore calcolo saldo per {account.name}: {e}")
        
        print(f"\n📊 Totale account: {len(accounts)}")
        
        # Account inclusi nel totale
        included_accounts = db_service.get_accounts_in_total()
        total_net_worth = 0.0
        
        print(f"\n💰 Account inclusi nel Net Worth:")
        for account in included_accounts:
            try:
                balance = db_service.calculate_account_balance(account.ID)
                total_net_worth += balance
                print(f"   • {account.name}: €{balance:.2f}")
            except Exception as e:
                print(f"   ❌ {account.name}: Errore calcolo")
        
        print(f"\n🎯 NET WORTH TOTALE: €{total_net_worth:.2f}")

except Exception as e:
    print(f"❌ Errore: {str(e)}")
    print("\n🔧 Verifica la connessione al database.")