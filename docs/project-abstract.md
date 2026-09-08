# Project Abstract

## Title
SmartHire AI: Real-Time AI-Powered Requirement Analysis and Candidate Ranking Platform

## Introduction
Recruitment teams often spend significant time reading resumes, comparing requirements, and coordinating interviews. SmartHire AI provides a local, explainable workflow for those tasks.

## Problem Statement
Manual screening is slow, inconsistent, and difficult to audit when many candidates apply to several roles.

## Existing System
Traditional workflows depend on spreadsheets, manual resume review, and disconnected communication tools. They provide limited explainability and aggregate analytics.

## Proposed System
SmartHire AI parses job descriptions and resumes, extracts skills, calculates explainable multi-factor matches, ranks candidates, schedules interviews, and presents real-time analytics.

## Objectives
Reduce repetitive screening work, preserve recruiter control, expose score evidence, protect candidate data, and provide measurable recruitment operations.

## Methodology
Flask routes and RBAC protect workflows. SQLAlchemy stores normalized data. Local regex/NLP utilities extract fields and skills. TF-IDF/cosine similarity provides semantic relevance. Weighted scoring produces persisted, explainable results.

## Features
Authentication, job and candidate management, resume parsing, JD analysis, matching, ranking, shortlisting, interviews, notifications, Socket.IO updates, analytics, Copilot, hiring insights, audit records, and CSV reporting.

## Technology Stack
Python, Flask, SQLAlchemy, MySQL, Flask-SocketIO, JavaScript, Chart.js, PyMuPDF, python-docx, scikit-learn, HTML, and CSS.

## Expected Results
Recruiters receive faster, reviewable candidate comparisons and current funnel/interview metrics without paid external services.

## Conclusion and Future Scope
The platform demonstrates an explainable local recruitment assistant. Future work may add multilingual parsing, validated learning datasets, calendar integrations, and enterprise deployment controls.
