# Project Synapse

**Project Synapse** is a career intelligence and mentoring tool that uses AI to provide users with personalized career recommendations, skill gap analysis, career path simulation, and mentor feedback.

-----

## What it does

  - **Onboarding** — You tell Synapse who you are: your current skills, resume, and career interests.
  - **Skill Enrichment** — Uses Gemini/Vertex AI models to enrich your skills profile.
  - **Recommendations** — Suggests career roles that are in demand, compatible with your skills, and have a high salary potential.
  - **Gap Analysis** — Compares your current skills against what's needed for your dream role (or company) and tells you which skills to develop.
  - **Simulation** — Generates a simulated career path or project brief for a chosen role based on your background.
  - **Mentor Feedback** — Offers personalized feedback on a submission (e.g., project, assignment) for a role you choose.

-----

## How to use

1.  **Onboard** Submit your skills, resume, or career goals. The system enriches this data to build a detailed profile.
2.  **Get Recommendations** Synapse suggests top roles (“aspirational”, “target”, “discovery”) with demand, salary, and skill-match scores.
3.  **Gap Analysis** Choose a dream role (and optionally a company). Synapse shows how close you are, what you're missing, and what to work on next.
4.  **Simulation** For a selected role, get a custom project brief or “career path simulation” to try out.
5.  **Mentor Feedback** Submit work (e.g., project, assignment) and receive actionable feedback from the Mentor Agent.

-----

## Why it’s helpful

  - Helps people make better career choices with data instead of guesswork.
  - Identifies skill gaps so learning is more focused.
  - Provides “what if” scenarios via simulation for better planning.
  - Gives direct feedback to improve, accelerating growth.
  - Saves time — everything is in one place.

-----

## Base Case Assumptions & Future Vision

**Base Case Assumptions:**
For the current version, the model considers a limited scope:

  - Only **15 job roles for computer science students** are currently included for recommendations and analysis. This is a foundational step that will be expanded.

**Vision: From Product to Platform**
Our mission is to evolve Synapse from a co-pilot into the definitive intelligence layer for the global skills economy. This will be achieved by:

  - **Creating a Self-Improving AI Flywheel:** Every micro-internship will generate proprietary data to fine-tune our models. This unique dataset—our ultimate moat—will create an ever-widening accuracy advantage and an unmatched map of the skills economy.
  - **Expanding Career Options:** We will use **agents or web scrapers** to collect real-time data from various sources to expand the number of job roles and provide the most up-to-date career information.
  - **Evolving to a "Skills Stock Market" with GNNs:** Our next architectural leap is a **Graph Neural Network (GNN)** to model the career landscape in real-time, allowing us to predict high-value skills and roles years before they become mainstream.
  - **Scaling as a "Career-as-a-Service" API:** We will license our core engine, enabling universities to embed our "Micro-Internship" generator into their curriculum and companies to use our "Gap Analysis" for intelligent talent sourcing and upskilling.
  - **Becoming the Indispensable Bridge to the AI Economy:** We will use generative experiences to prove the value of learning products like Google's Career Certificates, creating the most powerful and authentic gateway to the professional learning ecosystem.

-----

## Demo Video

[Watch Demo Video](https://drive.google.com/file/d/1iL-_EAE5aXNovKgEOcRaOL1oVkgFyfLD/view?usp=sharing)

-----

## Technical Setup (for developers)

  - **Backend**: Flask + AI agents + scoring engine
  - **Frontend**: React (Vite) consuming REST APIs
  - **Deployment**: Google Cloud Run / Firebase Hosting

### Backend APIs

  - `/onboard` — Create or update user profile
  - `/recommend` — Get role recommendations
  - `/gap_analysis` — Check skill gaps
  - `/simulate` — Generate role-specific simulation
  - `/mentor` — Get mentor feedback

-----

## Quick Start

### Prerequisites

  - Python 3.11+
  - Node.js 18+ (for frontend)
  - Google Gemini / Vertex AI API key

### Steps

1.  Clone the repo:

    ```bash
    git clone https://github.com/tanaysinha1607/Synapse
    cd synapse
    ```

2.  Set environment variables:

    ```bash
    export GEMINI_API_KEY=<your_api_key>
    ```

3.  Install backend dependencies:

    ```bash
    pip install -r requirement.txt
    ```

4.  Run backend:

    ```bash
    PYTHONPATH=src python src/main_api.py
    ```

5.  Start frontend:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

-----

## Hackathon Use Case

Project Synapse empowers learners and professionals to make smarter career decisions by combining AI-driven insights, role recommendations, skill gap analysis, and mentorship—all through an intuitive interface.