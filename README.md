The AI Placement Evaluator simulates real-world technical interview rounds by providing dynamically generated questions, real-time response analysis, and actionable career feedback.

Key Features:
Domain-Agnostic Engine: Dynamically adapts its evaluation criteria based on the selected domain (e.g., Data Science, Web Development, System Design, or General Aptitude).

Structured Feedback System: Forces LLM responses into strict output formats, rating candidates on technical accuracy, communication clarity, and problem-solving depth.

Secure API Workflow: Key-management handled via the UI sidebar using environment/session isolation to prevent credential leakage.

Persistent State Management: Built using Streamlit's session_state to maintain smooth conversation context and prevent state reset bugs during dynamic rerenders.

Tech Stack:
Language: Python 3.10+

Frontend / UI: Streamlit

LLM Orchestration: REST API Orchestration / Groq Cloud API / OpenAI API

Data Structure & Validation: Pydantic / JSON Schema
