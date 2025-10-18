# test_enum.py - Test per verificare gli ENUM
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import engine, SessionLocal
from app.models.db_models import Category, CatType
from sqlalchemy import text

def test_enum():
    print("🧪 Test ENUM PostgreSQL...")
    
    try:
        with SessionLocal() as session:
            # Test 1: Inserimento diretto
            print("1️⃣ Test inserimento categoria...")
            
            category = Category(
                name="Test Category",
                type=CatType.ENTRATA
            )
            
            session.add(category)
            session.commit()
            
            print(f"✅ Categoria creata con ID: {category.ID}")
            print(f"   Nome: {category.name}")
            print(f"   Tipo: {category.type} (valore: {category.type.value})")
            
            # Test 2: Lettura
            print("\n2️⃣ Test lettura categoria...")
            read_category = session.query(Category).filter(Category.name == "Test Category").first()
            
            if read_category:
                print(f"✅ Categoria letta: {read_category.name}, Tipo: {read_category.type}")
            
            # Cleanup
            session.delete(category)
            session.commit()
            print("🧹 Cleanup completato")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        
        # Verifica diretta con SQL
        print("\n🔍 Verifica diretta valori ENUM...")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (
                        SELECT oid 
                        FROM pg_type 
                        WHERE typname = 'CatType'
                    )
                    ORDER BY enumlabel;
                """))
                
                values = [row[0] for row in result.fetchall()]
                print(f"Valori ENUM CatType nel DB: {values}")
                
        except Exception as e2:
            print(f"❌ Errore nella verifica SQL: {e2}")

if __name__ == "__main__":
    test_enum()