# PawPal+ System Architecture

## System Diagram with RAG & Reliability Integration

```mermaid
flowchart TB
    subgraph INPUT["📥 INPUT LAYER"]
        direction TB
        A1[("👤 Owner<br/>Name, Available Time")]
        A2[("🐕 Pet<br/>Name, Species, Age")]
        A3[("📋 Task<br/>Type, Duration, Priority")]
    end

    subgraph CORE["🔄 CORE PROCESSING LAYER"]
        direction LR
        B1[("Scheduler<br/>Brain")]
        B2[("📚 RAG System")]
        B3[("✅ Reliability<br/>Validator")]
    end

    subgraph KNOWLEDGE["💾 KNOWLEDGE LAYER"]
        direction TB
        K1[("PetCare<br/>KnowledgeBase")]
        K1 --- K2[Dog Care Guidelines]
        K1 --- K3[Cat Care Guidelines]
        K1 --- K4[General Pet Tips]
    end

    subgraph TESTING["🧪 TESTING LAYER"]
        direction TB
        T1[("PlanTester<br/>Edge Cases")]
        T2[("Validation<br/>Checks")]
    end

    subgraph OUTPUT["📤 OUTPUT LAYER"]
        direction TB
        O1[("📅 DailyPlan<br/>Scheduled Tasks")]
        O2[("💡 AI Insights<br/>Pet Care Advice")]
        O3[("✅ Reliability<br/>Report")]
    end

    INPUT --> CORE
    KNOWLEDGE --> B2
    B2 --> B1
    B1 --> B3
    B3 --> TESTING
    CORE --> OUTPUT
    
    B1 -.->|Retrieves Tasks| INPUT
    B2 -.->|Fetches Advice| KNOWLEDGE
    B3 -.->|Validates| TESTING

    style INPUT fill:#e1f5fe,stroke:#01579b
    style CORE fill:#e8f5e9,stroke:#2e7d32
    style KNOWLEDGE fill:#fff3e0,stroke:#e65100
    style TESTING fill:#fce4ec,stroke:#c2185b
    style OUTPUT fill:#f3e5f5,stroke:#7b1fa2
```

---

## Data Flow Description

### 📥 Input → Process → Output

| Stage | Component | Description |
|-------|-----------|-------------|
| **Input** | Owner, Pet, Task | User provides: name, available time, pet details, task list |
| **Process** | Scheduler | Retrieves all tasks, filters mandatory ones, ranks by priority |
| **Process** | RAG System | Retrieves relevant pet care advice from knowledge base |
| **Process** | Reliability Validator | Validates plan for feasibility, consistency, completeness |
| **Output** | DailyPlan | Scheduled tasks + AI insights + reliability report |

---

## Human & Testing Involvement

### 👤 Human Involvement (Checking AI Results)

1. **Owner Review**
   - User reviews generated schedule in Streamlit app
   - Can mark tasks as complete or skip them
   - Can adjust available time and regenerate

2. **Pet Care Decision**
   - AI provides advice but human makes final decisions
   - Can accept or ignore smart suggestions

### 🧪 Testing Involvement

1. **Automated Testing (PlanTester)**
   - Edge case testing: empty tasks, overflow, dependencies
   - Runs via `pytest tests/test_pawpal.py`

2. **Reliability Validation**
   - Time feasibility check: Does plan fit available time?
   - Consistency check: No duplicates, no zero-duration tasks
   - Completeness check: All mandatory tasks scheduled
   - Conflict check: No scheduling overlaps

3. **Manual Verification**
   - User can expand "AI Insights" section to verify advice
   - User can review "Reliability Check" metrics

---

## Component Details

### Core Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| **Scheduler** | Agent | Organizes tasks into daily plan using priority & time constraints |
| **RAG Integration** | Retriever | Fetches relevant pet care advice from knowledge base |
| **ReliabilityValidator** | Evaluator | Validates plan reliability across multiple dimensions |
| **PlanTester** | Tester | Runs automated edge case tests |

### Knowledge Base (RAG)

- **Dog Care Guidelines**: Walking, feeding, playtime, grooming
- **Cat Care Guidelines**: Feeding, litter box, enrichment, vet visits
- **General Pet Tips**: Hydration, rest, general health

### Validation Categories

1. **Feasibility**: Plan fits within available time
2. **Consistency**: No duplicates or invalid tasks
3. **Completeness**: All mandatory tasks included
4. **Conflicts**: No scheduling overlaps