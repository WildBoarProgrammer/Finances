#!/usr/bin/env python3
"""
Script per eliminare l'account di test dal database.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.models.database import SessionLocal
    from app.models.db_models import Account
    
    print("🗑️ Eliminazione Account di Test")
    print("=" * 35)
    
    with SessionLocal() as session:
        # Trova l'account test_account
        test_account = session.query(Account).filter(Account.name == "test_account").first()
        
        if test_account:
            print(f"🔍 Trovato account: {test_account.name} (ID: {test_account.ID})")
            session.delete(test_account)
            session.commit()
            print("✅ Account eliminato con successo!")
        else:
            print("⚠️ Nessun account 'test_account' trovato nel database.")
    
except Exception as e:
    print(f"❌ Errore: {str(e)}")