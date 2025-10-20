# 🏦 Finances - Dashboard Gestione Finanziaria Personale

Un'applicazione web moderna per la gestione delle finanze personali, costruita con **Reflex** (framework Python full-stack) e **PostgreSQL**.

## 📋 Panoramica

L'app Finances è una dashboard completa per il monitoraggio e la gestione delle finanze personali che offre:

- **Visualizzazione del patrimonio netto** con grafici interattivi
- **Gestione multi-account** (conti correnti, risparmi, carte di credito, investimenti)
- **Tracking delle transazioni** con categorizzazione automatica
- **Transazioni ricorrenti** per entrate/uscite fisse
- **Analytics e reporting** con riassunti mensili e trend
- **Modalità dual**: dati reali da database PostgreSQL o dati simulati per demo

## 🏗️ Architettura

### Stack Tecnologico

- **Frontend**: Reflex (React.js generato automaticamente)
- **Backend**: Python con Reflex State Management
- **Database**: PostgreSQL con SQLAlchemy ORM
- **Styling**: Tailwind CSS
- **Charts**: Componenti nativi Reflex

### Struttura del Progetto

```
Finances/
├── app/
│   ├── app.py                 # App principale e routing
│   ├── components/           # Componenti UI modulari
│   │   ├── header.py         # Header con azioni principali
│   │   ├── sidebar.py        # Navigazione laterale
│   │   ├── net_worth_*.py    # Grafici patrimonio netto
│   │   ├── account_section.py # Sezioni account per categoria
│   │   └── summary_section.py # Riassunto assets/liabilities
│   ├── models/              # Modelli dati e database
│   │   ├── models.py        # TypedDict per type safety
│   │   ├── database.py      # Setup SQLAlchemy
│   │   └── db_models.py     # Modelli ORM SQLAlchemy
│   ├── services/           # Layer business logic
│   │   └── database_service.py # Operazioni CRUD database
│   └── states/             # State management Reflex
│       ├── account_state.py # State principale applicazione
│       └── data.py         # Dati simulati per modalità demo
├── init_database.py        # Script inizializzazione DB
├── test_connection.py      # Utility test connessione
├── Schema.sql             # Schema PostgreSQL
├── DATABASE_SETUP.md      # Guida setup database
└── requirements.txt       # Dipendenze Python
```

## 🎯 Funzionalità Principali

### 1. Dashboard Patrimonio Netto

- **Grafico interattivo** del patrimonio nel tempo (1 mese, 3 mesi, 6 mesi, 1 anno, tutto)
- **Metriche di performance** con variazioni assolute e percentuali
- **Calcolo automatico** basato su saldi account reali

### 2. Gestione Account Multi-Categoria

- **Cash**: Conti correnti e risparmi
- **Credit Cards**: Carte di credito con saldi negativi
- **Investments**: 401k, fondi pensione, investimenti
- **Altri tipi**: Configurabili via database

### 3. Sistema Transazioni Avanzato

- **Transazioni singole**: Entrate/uscite one-time
- **Transazioni ricorrenti**: Stipendi, affitti, bollette
- **Categorizzazione**: Sistema flessibile categorie personalizzabili
- **Multi-user**: Supporto utenti multipli con permessi

### 4. Analytics e Reporting

- **Riassunto Assets/Liabilities** con percentuali
- **Trend mensili** per account e categorie
- **Sparkline charts** per visualizzazione rapida trend
- **Calcoli automatici** saldi e patrimonio netto

## 🔧 Componenti e Interazioni

### State Management (`account_state.py`)

Il cuore dell'applicazione, gestisce:

- **Stato connessione database** (modalità live/simulata)
- **Dati account e transazioni** con reactive updates
- **Filtri grafici** e range temporali
- **Eventi utente** (refresh, toggle, navigazione)

### Database Service (`database_service.py`)

Layer di astrazione per operazioni database:

- **CRUD operations** per tutte le entità
- **Calcoli business logic** (saldi account, patrimonio netto)
- **Query analytics** (riassunti mensili, trend)
- **Context manager** per gestione sessioni SQLAlchemy

### Componenti UI Modulari

Ogni componente è altamente riutilizzabile e responsivo:

- **`header.py`**: Azioni principali (refresh, add account)
- **`sidebar.py`**: Navigazione principale dell'app
- **`net_worth_*.py`**: Grafici e summary patrimonio
- **`account_section.py`**: Cards espandibili per categorie account
- **`summary_section.py`**: Breakdown assets/liabilities

## 🚀 Setup e Installazione

### Prerequisiti

- Python 3.8+
- PostgreSQL 12+
- pip

### Setup Rapido

1. **Installa dipendenze**:

```bash
pip install -r requirements.txt
```

2. **Configura database** (vedi `DATABASE_SETUP.md` per dettagli):

```sql
CREATE DATABASE finances_db;
```

3. **Configura ambiente** (`.env`):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/finances_db
```

4. **Inizializza database**:

```bash
python init_database.py
```

5. **Avvia applicazione**:

```bash
reflex run
```

## 💡 Modalità Operative

### Modalità Database (Produzione)

- Connessione PostgreSQL reale
- Dati persistenti e sincronizzati
- Transazioni e saldi calcolati in real-time
- Multi-user support completo

### Modalità Simulata (Demo)

- Dati generati programmaticamente
- Fallback automatico se database non disponibile
- Perfect per testing e demo
- Dati realistici ma temporanei

## 🎨 Design Patterns

### Reactive State Management

```python
@rx.var
def account_categories(self) -> List[AccountCategory]:
    """Reactive property che switcha tra DB e dati simulati"""
    if self.use_database and self.db_connected:
        return self._get_accounts_from_database()
    return account_categories_data
```

### Context Manager Pattern

```python
with DatabaseService() as db_service:
    accounts = db_service.get_all_accounts()
    balance = db_service.calculate_account_balance(account_id)
```

### Type Safety con TypedDict

```python
class AccountDetail(TypedDict):
    id: str
    name: str
    balance: float
    # ... garantisce type checking completo
```

## 🔮 Potenziali Utilizzi

### Personal Finance Management

- Monitoraggio spese familiari
- Planning budgetario
- Tracking obiettivi risparmio
- Analisi trend spese

### Small Business Accounting

- Gestione cash flow
- Tracking entrate/uscite
- Reporting finanziario
- Budget planning

### Financial Planning & Analytics

- Analisi patrimonio nel tempo
- Proiezioni future
- Benchmark performance
- Decision support

### Educational & Demo

- Teaching financial literacy
- Prototipazione soluzioni fintech
- Portfolio development
- Proof of concept per investitori

## 🔄 Flusso Applicazione

1. **Startup**: Verifica connessione DB, fallback a dati simulati se necessario
2. **Dashboard Load**: Carica account, calcola patrimonio, genera grafici
3. **User Interaction**: Reactive updates su filtri, toggle, refresh
4. **Data Sync**: Automatic refresh da database o simulazione cambiamenti
5. **State Management**: Reflex gestisce automaticamente UI updates

## 📊 Performance & Scalabilità

- **Database connection pooling** via SQLAlchemy
- **Lazy loading** per grafici e dati complessi
- **Efficient queries** con ottimizzazioni PostgreSQL
- **Responsive design** con Tailwind CSS
- **Component-based architecture** per manutenibilità

L'architettura modulare e il design pattern service-layer permettono facilmente di scalare l'applicazione aggiungendo nuove funzionalità come budget planning, investment tracking, financial goals, notifiche, export/import dati, e integrazione con banking APIs.

---

## ⚠️ **Disclaimer**

Questa è un'applicazione **dimostrativa** per gestione finanziaria personale. Non utilizzare in produzione senza:

- Implementare autenticazione/autorizzazione robusta
- Configurare HTTPS e sicurezza database
- Validare e sanitizzare tutti gli input utente
- Implementare backup e disaster recovery

## 🔒 **Setup Sicurezza**

1. **Mai committare file `.env`** con credenziali reali
2. **Usa password sicure** per database production
3. **Configura firewall** per database server
4. **Implementa logging** per audit trail

---

**Built with ❤️ using Reflex - The full-stack Python framework**
