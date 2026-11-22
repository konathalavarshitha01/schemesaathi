# SchemeSaathi

An AI agent that helps people in Andhra Pradesh and Telangana find government schemes they are eligible for, in Telugu, Hindi or English, by text or voice.

Built for IDEA//FORGE (NxtWave Academy AI & Agents Hackathon).
Track 1: Civic Pulse, Digital Governance and Public Information.
Problem: Multilingual Policy, Rights and Scheme Explainer, with an automation demo inspired by the Public Service Execution Agent.

## Problem
Many students and low-income families miss scholarships and welfare benefits. Information is scattered across websites, rules are hard to read, and deadlines are easy to miss.

## What it does
1. Understands the user's situation from a typed or spoken message (age, income, category, occupation, gender, state).
2. Asks follow-up questions only for missing details.
3. Matches the user against a schemes database and explains why they qualify.
4. Shows the document checklist and where to get each document.
5. Generates a pre-filled application summary PDF.
6. Saves deadline reminders.
7. Automation agent: opens a browser, fills a practice portal form by itself, submits it and returns a receipt.

## Agents
| Agent | Job |
|---|---|
| Profile Agent | Extracts details from Telugu, Hindi and English text |
| Scheme Finder | Rule-based eligibility matching (no hallucinated eligibility) |
| Document Agent | Document checklist per scheme |
| Form Agent | Pre-filled PDF |
| Reminder Agent | Deadline reminders |
| Automation Agent | Playwright fills and submits a demo portal form |

## Tech stack
React + Vite, FastAPI, ReportLab, Playwright, Web Speech API.

## Run locally
Backend:

    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    pip install playwright
    playwright install chromium
    python -m uvicorn main:app --reload --port 8001

Frontend:

    cd frontend
    npm install
    npm run dev

## Safety and limits
- Scheme data lives in backend/data/schemes.json. Income limits change, so every card tells users to verify on the official website.
- The automation agent only fills a practice portal. It never submits to real government sites.
- The PDF is a draft summary, not an official form.

## Impact
Target: a user finds eligible schemes and becomes application-ready in under 2 minutes. User test results: (add your numbers here).

