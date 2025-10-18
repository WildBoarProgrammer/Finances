# test_connection.py
import sys
import os

# Aggiungi il percorso dell'app
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.models.database import engine
    from sqlalchemy import text
    
    print("🔄 Test connessione database...")
    
    # Test connessione
    with engine.connect() as conn:
        # Usa text() per le query SQL raw in SQLAlchemy 2.0
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connessione riuscita!")
        print(f"📊 PostgreSQL Version: {version}")
        
        # Verifica tabelle esistenti
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        print(f"📋 Tabelle trovate: {', '.join(tables) if tables else 'Nessuna'}")
        
        # Verifica anche i tipi ENUM se ci sono tabelle
        if tables:
            result = conn.execute(text("""
                SELECT t.typname
                FROM pg_type t 
                LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
                WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
                AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
                AND n.nspname NOT IN ('information_schema', 'pg_catalog')
                AND t.typname IN ('CatType', 'TranStatus', 'RecurrenceType')
                ORDER BY t.typname;
            """))
            
            enums = [row[0] for row in result.fetchall()]
            print(f"🔧 Tipi ENUM trovati: {', '.join(enums) if enums else 'Nessuno'}")
        
except Exception as e:
    print(f"❌ Errore connessione: {str(e)}")
    print("\n🔧 Verifica:")
    print("1. PostgreSQL è in esecuzione")
    print("2. Il database 'finances_db' esiste") 
    print("3. Le credenziali nel .env sono corrette")
    print("4. Hai eseguito lo script SQL per creare lo schema?")