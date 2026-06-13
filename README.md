# 🛡️ JB Compliance Backend

금융 문서의 규정 준수 여부를 AI로 검토하고, 규정 기반 질의응답 및 보고서 생성을 지원하는 FastAPI 기반 백엔드 서버입니다.

LangGraph 기반 Agent와 OpenAI GPT를 활용하여 금융 컴플라이언스 업무를 자동화합니다.

---

## ✨ 주요 기능

### 📄 AI 문서 검토

* 문서 업로드
* 규정 기반 AI 검토
* 위험 문장 하이라이트
* 수정 제안 생성
* 검토 결과 조회

### 📑 검토 보고서 생성

* PDF 보고서
* DOCX 보고서
* TXT 보고서

### 💬 AI 컴플라이언스 채팅

* FAQ 기반 질의응답
* 규정 검색
* 근거 문서 제공

### 🎓 교육 콘텐츠 생성

* 교육자료 생성
* 교육 안내 문구 생성
* 교육 포스터 생성

### 📅 일정 및 알림 관리

* 캘린더 일정 CRUD
* 알림 CRUD

---

## 🛠 Tech Stack

| Category            | Technology           |
| ------------------- | -------------------- |
| Framework           | FastAPI              |
| Language            | Python               |
| AI Framework        | LangGraph, LangChain |
| LLM                 | OpenAI GPT-5.5       |
| Vector Store        | FAISS                |
| Document Processing | PyMuPDF, python-docx |
| Report Generation   | ReportLab            |
| Validation          | Pydantic             |

---

## 🧠 AI Architecture

```text
User
 ↓
Frontend
 ↓
FastAPI
 ↓
LangGraph Agent
 ↓
OpenAI Embedding
 ↓
FAISS Search
 ↓
GPT-5.5
 ↓
Response
```

---

## 🚀 Getting Started

### Install

```bash
pip install -r requirements.txt
```

### Environment Variables

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5.5
```

### Run Server

```bash
uvicorn app.main:app --reload
```

---

## 📂 Project Structure

```text
app
├── agents
├── api
├── graphs
├── rag
├── services
├── models
├── core
└── main.py
```

---

## 🔌 Core APIs

### Default

```text
GET /
GET /health
```

### Authentication

```text
POST /api/v1/auth/login
POST /api/v1/auth/logout
```

### File Upload

```text
POST /api/v1/files/upload
GET  /api/v1/files
GET /api/v1/files/download/{file_name}
GET /api/v1/files/uploaded/{file_name}
```

### AI Review

```text
POST /api/v1/reviews/analyze
GET  /api/v1/reviews
GET  /api/v1/reviews/{review_id}
GET  /api/v1/reviews/{review_id}/highlights
GET  /api/v1/reviews/{review_id}/report
```

### AI Chat

```text
POST /api/v1/chat
```

### Languages

```text
GET  /api/v1/languages
PUT  /api/v1/languages/settings/language
```

### Alarms

```text
GET    /api/v1/alarms
POST   /api/v1/alarms
PATCH  /api/v1/alarms/{alarm_id}
DELETE /api/v1/alarms/{alarm_id}
```

### Calendar

```text
GET    /api/v1/calendar
POST   /api/v1/calendar
GET    /api/v1/calendar/{event_id}
PATCH  /api/v1/calendar/{event_id}
DELETE /api/v1/calendar/{event_id}
```

---

## 📢 Notes

* 업로드 파일은 `uploads/`에 저장됩니다.
* 결과 파일은 `outputs/`에 저장됩니다.
* 현재 일부 데이터는 In-Memory 방식으로 관리됩니다.
* 향후 PostgreSQL 및 AWS S3 기반으로 확장 예정입니다.
