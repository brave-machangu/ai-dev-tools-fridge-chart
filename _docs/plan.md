# Project Scope: Family Chore & Reward Manager

## 1. Project Overview
A web-based application designed to help families manage household chores through a point-based reward system. The application minimizes screen time for children by utilizing a "parent-only" digital interface combined with automatically generated, printable physical charts for the kids.

## 2. Target Audience
*   **Primary Users:** Parents (managing the system via mobile or desktop browser).
*   **Secondary Audience:** Children (interacting with the physical printouts and receiving rewards).

## 3. Technology Stack
*   **Backend Framework:** Django (Python)
*   **Database:** SQLite (development) / PostgreSQL (production) via Django ORM
*   **Frontend:** Django Templates (HTML/CSS) with minimal JavaScript
*   **PDF Generation:** WeasyPrint or ReportLab (for the printable charts)

## 4. Core Mechanics
*   **The Reward System (Custom Points Store):** Children earn points for completing chores. Parents define custom rewards (e.g., "1 Hour Screen Time" = 50 pts, "Pizza Night" = 200 pts) that kids can "purchase" with their earned points.
*   **Verification (Parent Approval):** Chores are not automatically marked as completed. A parent must review the work and explicitly click "Approve" in the app before points are credited to the child's ledger.
*   **End-of-Week Logic (Clean Slate):** Unfinished chores do not roll over to the next week, and there are no negative point penalties. The week resets cleanly every Monday to maintain a positive, motivating environment.

## 5. Chore Distribution Models
*   **Auto-Rotating Routines:** Daily or weekly recurring chores (e.g., washing dishes, taking out the trash) automatically rotate between the children each week to ensure fairness.
*   **Bonus Bounties:** A digital "bounty board" where parents can post one-off, high-effort tasks (e.g., washing the car, raking leaves) with higher point values. Kids can claim these voluntarily.

## 6. User Interface & Visibility
*   **Parent-Only Access:** Children do not have login credentials or interact with the app.
*   **The Fridge Chart:** The system's primary output is a clean, weekly PDF schedule containing the chore rotations, current point balances, and available bounties. Parents print this on Sunday night and put it on the fridge.
*   **Low-Noise Notifications:** The app avoids daily push notifications. It relies on a simple two-day cadence:
    *   *Friday Afternoon:* Reminder to review and approve the week's completed chores.
    *   *Sunday Evening:* Reminder to generate and print the upcoming week's chart.

## 7. High-Level Data Entities (Django Models Preview)
*   **Family:** Groups parents and children together.
*   **Profile:** Differentiates between 'Parent' (admin access) and 'Child' (point ledger).
*   **Chore:** Defines the task, base point value, and type (Routine vs. Bounty).
*   **ChoreAssignment:** Links a specific chore to a child for a specific week/date.
*   **Reward:** Defines the custom prizes and their point costs.
*   **LedgerEntry:** Tracks points earned and spent for auditing.