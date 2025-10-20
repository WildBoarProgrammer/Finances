#!/usr/bin/env python3
"""
Script per creare lo schema database da Schema.sql.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.models.database import engine
    from sqlalchemy import text
    
    print("🏗️ Setup Schema Database")
    print("=" * 30)
    
    # Leggi il file Schema.sql
    schema_file = os.path.join(os.path.dirname(__file__), 'Schema.sql')
    
    if not os.path.exists(schema_file):
        print("❌ File Schema.sql non trovato!")
        sys.exit(1)
    
    print("📄 Lettura Schema.sql...")
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print("🔗 Connessione al database...")
    with engine.connect() as conn:
        print("✅ Connesso!")
        
        # Dividi lo schema in statements separati
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"\n⚙️ Esecuzione {len(statements)} statements SQL...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    conn.execute(text(statement))
                    # Identifica il tipo di statement per il logging
                    stmt_type = "Unknown"
                    if statement.upper().startswith('CREATE TYPE'):
                        stmt_type = "ENUM Type"
                    elif statement.upper().startswith('CREATE TABLE'):
                        table_name = statement.split('"')[1] if '"' in statement else "Unknown"
                        stmt_type = f"Table {table_name}"
                    elif statement.upper().startswith('COMMENT ON'):
                        stmt_type = "Comment"
                    elif statement.upper().startswith('ALTER TABLE'):
                        stmt_type = "Foreign Key"
                    
                    print(f"   ✅ {i:2d}. {stmt_type}")
                    
                except Exception as e:
                    # Identifica il tipo di statement per il logging degli errori
                    stmt_type = "Unknown"
                    if statement.upper().startswith('CREATE TYPE'):
                        stmt_type = "ENUM Type"
                    elif statement.upper().startswith('CREATE TABLE'):
                        table_name = statement.split('"')[1] if '"' in statement else "Unknown"
                        stmt_type = f"Table {table_name}"
                    elif statement.upper().startswith('COMMENT ON'):
                        stmt_type = "Comment"
                    elif statement.upper().startswith('ALTER TABLE'):
                        stmt_type = "Foreign Key"
                    
                    # Molti errori sono normali (tabelle già esistenti, etc.)
                    if "already exists" in str(e):
                        print(f"   ⚠️ {i:2d}. {stmt_type} (già esistente)")
                    else:
                        print(f"   ❌ {i:2d}. {stmt_type} - Errore: {e}")
        
        # Commit delle modifiche
        conn.commit()
        print("\n💾 Schema applicato con successo!")
        
        # Verifica finale
        print("\n🔍 Verifica finale...")
        result = conn.execute(text("""
            SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
            FROM pg_type t 
            LEFT JOIN pg_enum e ON t.oid = e.enumtypid
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
            WHERE t.typname IN ('CatType', 'TranStatus', 'RecurrenceType')
            GROUP BY t.typname
            ORDER BY t.typname;
        """))
        
        enums = result.fetchall()
        if enums:
            print("✅ ENUM Types creati:")
            for enum_name, enum_values in enums:
                print(f"   • {enum_name}: {enum_values}")
        else:
            print("❌ ENUM Types non trovati!")
        
        # Verifica tabelle
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('Users', 'Category', 'Account', 'Transactions', 'Recurring_Transactions')
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        print(f"\n✅ Tabelle create: {', '.join(tables) if tables else 'Nessuna'}")

except Exception as e:
    print(f"❌ Errore: {str(e)}")
    print("\n🔧 Verifica:")
    print("1. PostgreSQL è in esecuzione")
    print("2. Il database 'finances_db' esiste")
    print("3. L'utente ha permessi di scrittura sul database")