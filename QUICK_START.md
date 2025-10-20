# 🚀 Quick Start - Finances Dashboard

Guida rapida per avviare la dashboard finanziaria in modalità **Database Only**.

## 📋 Modifiche Implementate

✅ **Modalità Database Esclusiva**: L'app ora usa SOLO PostgreSQL  
✅ **Rimozione Dati Simulati**: Nessun fallback a dati fittizi  
✅ **Connessione Automatica**: Tentativo automatico di connessione all'avvio  
✅ **Script Account Specifico**: Creazione account con parametri esatti

## 🔧 Setup Rapido

### 1. Verifica Database

```powershell
# Assicurati che PostgreSQL sia attivo
# Il database 'finances_db' deve esistere
```

### 2. Configura Connessione

```powershell
# Il file .env dovrebbe contenere:
# DATABASE_URL=postgresql://username:password@localhost:5432/finances_db
```

### 3. Setup Schema Database ⭐ **IMPORTANTE**

```powershell
# Prima di tutto, inizializza lo schema corretto
python setup_database_schema.py
```

### 4. Verifica Schema (opzionale)

```powershell
# Controlla che tutto sia corretto
python check_database_schema.py
```

### 5. Crea Account Specifico

```powershell
python create_specific_account.py
```

### 6. Avvia App

```powershell
reflex run
```

## 📊 Account Creato

Lo script `create_specific_account.py` crea un account con esattamente i parametri richiesti:

```
need_admin: 0 (False)
name: testname_0
goal: test_goal
initial_balance: 1000.00
in_tot: 1 (True)
```

## 🎯 Comportamento App

- **All'avvio**: Tentativo automatico di connessione PostgreSQL
- **Se connesso**: Mostra dati reali dal database
- **Se NON connesso**: Mostra messaggio di errore rosso
- **Refresh**: Ricarica dati esclusivamente dal database
- **Nessun fallback**: Zero dati simulati/fittizi

## 🔍 Troubleshooting

### ❌ Errore ENUM "CatType" non valida

**Problema**: Il database non ha gli ENUM types corretti  
**Soluzione**:

```powershell
python setup_database_schema.py
python create_specific_account.py
```

### Database non connesso

- Verifica che PostgreSQL sia in esecuzione
- Controlla credenziali in `.env`
- Verifica che il database `finances_db` esista

### Account non visibile

- Assicurati di aver eseguito `python create_specific_account.py`
- Clicca "Refresh all" nella dashboard
- Verifica che `in_tot` sia `True` per l'account

### Errori di permessi

- L'utente PostgreSQL deve avere permessi sul database
- Esegui: `GRANT ALL PRIVILEGES ON DATABASE finances_db TO tuo_username;`

## 🎉 Risultato Finale

La dashboard ora funziona **esclusivamente con PostgreSQL** e mostra:

- Account reali dal database
- Transazioni persistenti
- Calcoli saldi in tempo reale
- Grafici basati su dati reali

**Nessun dato simulato sarà mai mostrato!**
