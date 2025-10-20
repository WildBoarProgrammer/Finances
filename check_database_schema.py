#!/usr/bin/env python3
"""
Script per verificare lo stato dello schema database.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.models.database import engine
    from sqlalchemy import text
    
    print("🔍 Verifica Schema Database")
    print("=" * 35)
    
    with engine.connect() as conn:
        print("✅ Connessione riuscita!")
        
        # Verifica tabelle esistenti
        print("\n📋 Tabelle nel database:")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        for table in tables:
            print(f"   • {table}")
        
        # Verifica tipi ENUM
        print("\n🔧 Tipi ENUM nel database:")
        result = conn.execute(text("""
            SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
            FROM pg_type t 
            LEFT JOIN pg_enum e ON t.oid = e.enumtypid
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
            WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
            AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
            AND n.nspname NOT IN ('information_schema', 'pg_catalog')
            AND t.typname IN ('CatType', 'TranStatus', 'RecurrenceType')
            GROUP BY t.typname
            ORDER BY t.typname;
        """))
        
        enums = result.fetchall()
        if enums:
            for enum_name, enum_values in enums:
                print(f"   • {enum_name}: {enum_values}")
        else:
            print("   ❌ Nessun ENUM trovato! Schema non inizializzato.")
        
        # Verifica struttura tabella Account
        print("\n🏛️ Struttura tabella Account:")
        try:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'Account' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            if columns:
                for col_name, data_type, nullable in columns:
                    print(f"   • {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
            else:
                print("   ❌ Tabella Account non trovata!")
        except Exception as e:
            print(f"   ❌ Errore nella verifica tabella Account: {e}")
        
        # Conta record in Account
        try:
            result = conn.execute(text('SELECT COUNT(*) FROM "Account"'))
            count = result.scalar()
            print(f"\n📊 Record nella tabella Account: {count}")
        except Exception as e:
            print(f"\n❌ Errore nel conteggio Account: {e}")

except Exception as e:
    print(f"❌ Errore connessione: {str(e)}")
    print("\n🔧 Il database potrebbe non essere inizializzato correttamente.")