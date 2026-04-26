# Claim Reflex AI 🚀

An AI-powered insurance claim validation and decision platform that automates claim assessment using OCR, rule validation, multi-agent reasoning, and premium reporting.

---

## 🌐 Live Demo
Frontend: Vercel  
Backend: Render  
Storage/Auth: Supabase

---

## 📌 Project Overview

Claim Reflex AI helps insurance teams instantly validate policy and claim documents, detect mismatches, and generate AI-backed approval/rejection decisions with confidence scoring.

Instead of manual verification, the system uses:

- OCR text extraction from uploaded PDFs
- Intelligent policy vs claim validation
- Multi-Agent AI Debate Engine
- Final approval/rejection reasoning
- Downloadable premium PDF reports
- Clean enterprise-grade UI

---

## ⚙️ Core Features

### 📄 Document Upload System
- Upload Policy PDF
- Upload Claim PDF
- Preview uploaded files before processing

### 🤖 AI Decision Engine
Uses 3-layer reasoning:

#### ✅ Approval Agent
Finds evidence supporting approval.

#### ❌ Rejection Agent
Finds issues / risks / mismatches.

#### ⚖️ Final Judge
Compares both sides and gives final verdict.

---

## 📊 Smart Validation Checks

- Policy Number Match
- Claim Number Presence
- Holder Name Fuzzy Match
- Policy Expiry Check
- Claim Amount Detection
- OCR Noise Handling
- Missing Fields Detection

---

## 🎯 Premium Frontend UI

- Animated processing states
- Smooth transitions
- Approval / rejection result cards
- Confidence progress bar
- Expandable AI Debate Chamber
- Recent analysis history
- Responsive mobile design

---

## 📥 Premium PDF Reports

Generated after every analysis:

### Includes:
- Final decision
- Confidence %
- Validation summary
- Approval Agent opinion
- Rejection Agent opinion
- Final Judge verdict
- Audit Trail

---

## 🧠 Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask / FastAPI

### AI
- OpenAI API

### Cloud
- Supabase
- Vercel
- Render

---

## 🚀 How It Works

1. Upload Policy PDF  
2. Upload Claim PDF  
3. Click Analyze Claim  
4. AI validates documents  
5. Debate engine reasons internally  
6. Final result shown instantly  
7. Download premium report

---

## 📁 Project Structure

```bash
frontend/
 ├── index.html
 ├── app.html

backend/
 ├── main.py
 ├── validator.py
 ├── ai_engine.py
