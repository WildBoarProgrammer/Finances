# 🏦 Setup Database PostgreSQL per Finances App

Questa guida ti aiuterà a configurare il database PostgreSQL per l'applicazione Finances.

## 📋 Prerequisiti

1. **PostgreSQL installato** (versione 12 o superiore)
2. **Python 3.8+**
3. **pip** per l'installazione delle dipendenze

## 🚀 Setup Rapido

### 1. Installazione PostgreSQL

**Windows:**

```powershell
# Scarica da https://www.postgresql.org/download/windows/
# Oppure con chocolatey:
choco install postgresql
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**

```bash
brew install postgresql
```

### 2. Creazione Database

Accedi a PostgreSQL e crea il database:

```sql
-- Accedi come utente postgres
psql -U postgres

-- Crea il database
CREATE DATABASE finances_db;

-- Crea un utente dedicato (opzionale ma consigliato)
CREATE USER finances_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finances_db TO finances_user;

-- Esci
\q
```

### 3. Configurazione Applicazione

1. **Clona/aggiorna le dipendenze:**

```powershell
pip install -r requirements.txt
```

2. **Configura il file `.env`:**

```env
# Sostituisci con i tuoi valori
DATABASE_URL=postgresql://finances_user:your_secure_password@localhost:5432/finances_db
```

3. **Inizializza il database:**

```powershell
python init_database.py
```

4. **Avvia l'applicazione:**

```powershell
reflex run
```

## 🔧 Configurazione Avanzata

### Variabili d'Ambiente (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Esempi per diversi setup:
# Local: postgresql://finances_user:password123@localhost:5432/finances_db
# Remote: postgresql://user:pass@remote-server.com:5432/finances_db
# Docker: postgresql://postgres:password@db:5432/finances_db
```

### Schema Database

Il database utilizza lo schema definito in `Schema.sql` con le seguenti tabelle:

- **Users**: Gestione utenti e permessi
- **Category**: Categorie per transazioni (Entrata/Uscita)
- **Account**: Account finanziari (Conto corrente, Risparmi, etc.)
- **Transactions**: Transazioni singole
- **Recurring_Transactions**: Transazioni ricorrenti

### Tipi ENUM

- **CatType**: `'Entrata'` | `'Uscita'`
- **TranStatus**: `'Singolo'` | `'Ricorrente'`
- **RecurrenceType**: `'Ogni mese'` | `'Ogni anno'`

## 🐳 Setup con Docker (Opzionale)

Se preferisci usare Docker per PostgreSQL:

```yaml
# docker-compose.yml
version: "3.8"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: finances_db
      POSTGRES_USER: finances_user
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Avvia con:

```powershell
docker-compose up -d
```

## 📊 Dati di Esempio

Lo script `init_database.py` crea automaticamente:

- 2 utenti (admin e normale)
- 11 categorie (entrate e uscite)
- 5 account (checking, savings, credit card, 401k, emergency fund)
- ~25 transazioni degli ultimi 60 giorni
- 4 transazioni ricorrenti

## 🔍 Troubleshooting

### Errore di Connessione

```
psycopg2.OperationalError: could not connect to server
```

**Soluzioni:**

- Verifica che PostgreSQL sia in esecuzione
- Controlla host, porta, username e password nel `.env`
- Verifica che il database esista

### Errore Permessi

```
permission denied for database
```

**Soluzioni:**

- Assicurati che l'utente abbia i permessi sul database
- Usa `GRANT ALL PRIVILEGES` come mostrato sopra

### Tabelle Non Create

```
relation "Users" does not exist
```

**Soluzioni:**

- Esegui `python init_database.py`
- Verifica che non ci siano errori nella creazione delle tabelle

## 🔄 Modalità Fallback

L'app può funzionare anche senza database utilizzando dati simulati:

1. Nella UI, clicca "Usa dati simulati" se il database non è connesso
2. Oppure modifica `use_database = False` in `account_state.py`

## 🛠️ Comandi Utili

```powershell
# Backup database
pg_dump -U finances_user finances_db > backup.sql

# Restore database
psql -U finances_user finances_db < backup.sql

# Reset database (cancella tutti i dati)
python -c "from app.models.database import engine; engine.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')"
python init_database.py

# Test connessione
python -c "from app.models.database import engine; print('✅ Connessione OK' if engine.connect() else '❌ Errore')"
```

## 📞 Supporto

Se riscontri problemi:

1. Verifica i log dell'applicazione
2. Controlla che PostgreSQL sia in esecuzione: `systemctl status postgresql` (Linux) o Task Manager (Windows)
3. Testa la connessione manualmente: `psql -U finances_user -d finances_db -h localhost`

---

🎉 **Buon utilizzo dell'app Finances!**
