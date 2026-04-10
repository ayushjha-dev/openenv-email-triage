"""
FastAPI Server for Email Triage Environment.

Endpoints:
- POST /reset - Reset environment with a task
- POST /step - Execute an action
- GET /state - Get current state
- GET /tasks - List available tasks
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import logging

from .models import (
    Action, StepRequest, ResetRequest, StepResponse, ResetResponse,
    State, Observation
)
from .environment import EmailTriageEnv
from .tasks import get_task, list_tasks, TASKS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="openenv-email-triage",
    description="OpenEnv Email Triage Environment - AI email triage for OpenEnv hackathon",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = EmailTriageEnv()


# ============================================================================
# LANDING PAGE - Command Center Aesthetic with Custom SVG Icons
# ============================================================================

LANDING_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Triage | OpenEnv Environment</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #09090b;
            --bg-secondary: #0f0f12;
            --bg-card: #131316;
            --bg-card-hover: #1a1a1f;
            --border-subtle: rgba(255,255,255,0.06);
            --border-medium: rgba(255,255,255,0.1);
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --text-muted: #52525b;
            --accent-primary: #06b6d4;
            --accent-glow: rgba(6,182,212,0.25);
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --font-sans: 'DM Sans', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        
        html { scroll-behavior: smooth; }
        
        body {
            font-family: var(--font-sans);
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Noise texture overlay */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            opacity: 0.03;
            pointer-events: none;
            z-index: 1000;
        }
        
        /* Gradient orbs */
        .bg-glow {
            position: fixed;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.15;
            pointer-events: none;
            z-index: -1;
        }
        .bg-glow-1 { width: 600px; height: 600px; background: var(--accent-primary); top: -200px; right: -100px; }
        .bg-glow-2 { width: 400px; height: 400px; background: #8b5cf6; bottom: 100px; left: -100px; }
        
        .container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
        }
        
        @media (max-width: 768px) {
            .container { padding: 0 1.25rem; }
        }
        
        @media (max-width: 480px) {
            .container { padding: 0 1rem; }
        }
        
        /* ===== HEADER ===== */
        header {
            padding: 4rem 0 3rem;
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .header-content {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logo-icon {
            width: 56px;
            height: 56px;
            min-width: 56px;
            background: linear-gradient(135deg, var(--accent-primary), #8b5cf6);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 30px var(--accent-glow), 0 4px 20px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }
        
        .logo-icon::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%);
            pointer-events: none;
        }
        
        .logo-icon svg { width: 32px; height: 32px; }
        
        .title-group h1 {
            font-size: 1.75rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text-primary);
        }
        
        .title-group p {
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }
        
        .status-badges {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 0.9rem;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text-secondary);
            white-space: nowrap;
        }
        
        .badge-live {
            background: rgba(16,185,129,0.1);
            border-color: rgba(16,185,129,0.3);
            color: var(--accent-green);
        }
        
        .badge-live::before {
            content: '';
            width: 6px;
            height: 6px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        @media (max-width: 768px) {
            header { padding: 2.5rem 0 2rem; }
            .header-content { gap: 1.25rem; }
            .logo-icon { width: 48px; height: 48px; min-width: 48px; border-radius: 12px; }
            .logo-icon svg { width: 26px; height: 26px; }
            .title-group h1 { font-size: 1.5rem; }
            .title-group p { font-size: 0.875rem; }
            .status-badges { gap: 0.5rem; }
            .badge { padding: 0.4rem 0.7rem; font-size: 0.75rem; }
        }
        
        @media (max-width: 480px) {
            header { padding: 2rem 0 1.5rem; }
            .header-content { flex-direction: column; gap: 1rem; }
            .logo-section { gap: 0.75rem; }
            .logo-icon { width: 44px; height: 44px; min-width: 44px; }
            .logo-icon svg { width: 22px; height: 22px; }
            .title-group h1 { font-size: 1.25rem; }
            .title-group p { font-size: 0.8rem; }
            .status-badges { width: 100%; justify-content: flex-start; }
        }
        
        /* ===== STATS BAR ===== */
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: var(--border-subtle);
            border-radius: 16px;
            overflow: hidden;
            margin: 3rem 0;
        }
        
        .stat-item {
            background: var(--bg-card);
            padding: 1.75rem 1.5rem;
            text-align: center;
            transition: background 0.2s;
        }
        
        .stat-item:hover { background: var(--bg-card-hover); }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-top: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .stats-bar { grid-template-columns: repeat(2, 1fr); }
            .stat-value { font-size: 2rem; }
            .stat-item { padding: 1.25rem 1rem; }
        }
        
        @media (max-width: 480px) {
            .stats-bar { grid-template-columns: 1fr 1fr; gap: 1px; margin: 2rem 0; }
            .stat-value { font-size: 1.75rem; }
            .stat-item { padding: 1rem 0.75rem; }
            .stat-label { font-size: 0.7rem; }
        }
        
        /* ===== SECTIONS ===== */
        section { margin: 4rem 0; }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }
        
        .section-header svg {
            width: 20px;
            height: 20px;
            min-width: 20px;
            color: var(--accent-primary);
        }
        
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        @media (max-width: 768px) {
            section { margin: 3rem 0; }
            .section-header { margin-bottom: 1.25rem; }
        }
        
        @media (max-width: 480px) {
            section { margin: 2.5rem 0; }
            .section-title { font-size: 1rem; }
        }
        
        /* ===== TASK CARDS ===== */
        .task-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }
        
        @media (max-width: 1024px) {
            .task-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 640px) {
            .task-grid { grid-template-columns: 1fr; gap: 0.875rem; }
        }
        
        .task-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        
        .task-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--card-accent), transparent);
            opacity: 0;
            transition: opacity 0.25s;
        }
        
        .task-card:hover {
            border-color: var(--border-medium);
            transform: translateY(-2px);
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
        }
        
        .task-card:hover::before { opacity: 1; }
        
        .task-card.easy { --card-accent: var(--accent-green); }
        .task-card.medium { --card-accent: var(--accent-amber); }
        .task-card.hard { --card-accent: var(--accent-rose); }
        
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            gap: 0.5rem;
        }
        
        .task-number {
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        
        .difficulty-badge {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            color: var(--card-accent);
            background: color-mix(in srgb, var(--card-accent) 15%, transparent);
            white-space: nowrap;
        }
        
        .task-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }
        
        .task-desc {
            font-size: 0.875rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 1.25rem;
        }
        
        .task-meta {
            display: flex;
            gap: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-subtle);
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            white-space: nowrap;
        }
        
        .meta-item svg { width: 14px; height: 14px; min-width: 14px; }
        
        @media (max-width: 768px) {
            .task-card { padding: 1.25rem; border-radius: 14px; }
            .task-title { font-size: 1rem; }
            .task-desc { font-size: 0.8rem; margin-bottom: 1rem; }
        }
        
        @media (max-width: 480px) {
            .task-card { padding: 1rem; border-radius: 12px; }
            .task-header { margin-bottom: 0.75rem; }
            .task-title { font-size: 0.95rem; }
            .task-desc { font-size: 0.8rem; line-height: 1.4; margin-bottom: 0.875rem; }
            .task-meta { gap: 0.75rem; padding-top: 0.875rem; }
            .meta-item { font-size: 0.75rem; }
        }
        
        /* ===== ACTIONS GRID ===== */
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.75rem;
        }
        
        @media (max-width: 1024px) {
            .actions-grid { grid-template-columns: repeat(4, 1fr); }
        }
        
        @media (max-width: 640px) {
            .actions-grid { grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
        }
        
        @media (max-width: 400px) {
            .actions-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        .action-item {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.25rem 1rem;
            text-align: center;
            transition: all 0.2s;
        }
        
        .action-item:hover {
            border-color: var(--accent-primary);
            background: var(--bg-card-hover);
        }
        
        .action-icon {
            width: 40px;
            height: 40px;
            margin: 0 auto 0.75rem;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card-hover));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .action-icon svg {
            width: 20px;
            height: 20px;
            color: var(--accent-primary);
        }
        
        .action-name {
            font-size: 0.75rem;
            font-weight: 600;
            font-family: var(--font-mono);
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .action-desc {
            font-size: 0.7rem;
            color: var(--text-muted);
        }
        
        @media (max-width: 768px) {
            .action-item { padding: 1rem 0.75rem; border-radius: 10px; }
            .action-icon { width: 36px; height: 36px; margin-bottom: 0.5rem; border-radius: 8px; }
            .action-icon svg { width: 18px; height: 18px; }
            .action-name { font-size: 0.7rem; }
            .action-desc { font-size: 0.65rem; }
        }
        
        @media (max-width: 480px) {
            .action-item { padding: 0.875rem 0.5rem; }
            .action-icon { width: 32px; height: 32px; }
            .action-icon svg { width: 16px; height: 16px; }
        }
        
        /* ===== API ENDPOINTS ===== */
        .endpoints-list {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            overflow: hidden;
        }
        
        .endpoint-row {
            display: grid;
            grid-template-columns: 80px 140px 1fr;
            gap: 1rem;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-subtle);
            transition: background 0.15s;
            font-family: var(--font-mono);
            font-size: 0.85rem;
        }
        
        .endpoint-row:last-child { border-bottom: none; }
        .endpoint-row:hover { background: var(--bg-card-hover); }
        
        .method {
            font-weight: 600;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
        }
        
        .method-get { color: var(--accent-green); }
        .method-post { color: var(--accent-primary); }
        
        .endpoint-path { color: var(--text-primary); word-break: break-all; }
        .endpoint-desc { color: var(--text-muted); font-family: var(--font-sans); }
        
        @media (max-width: 768px) {
            .endpoints-list { border-radius: 14px; }
            .endpoint-row {
                grid-template-columns: 60px 100px 1fr;
                gap: 0.75rem;
                padding: 0.875rem 1.25rem;
                font-size: 0.8rem;
            }
            .method { font-size: 0.65rem; }
        }
        
        @media (max-width: 640px) {
            .endpoint-row {
                grid-template-columns: 1fr;
                gap: 0.4rem;
                padding: 1rem;
            }
            .endpoint-path { order: -1; font-weight: 500; }
            .method { font-size: 0.6rem; width: fit-content; }
            .endpoint-desc { font-size: 0.75rem; margin-top: 0.25rem; }
        }
        
        @media (max-width: 480px) {
            .endpoints-list { border-radius: 12px; }
            .endpoint-row { padding: 0.875rem; }
            .endpoint-path { font-size: 0.8rem; }
            .endpoint-desc { font-size: 0.7rem; }
        }
        
        /* ===== CTA SECTION ===== */
        .cta-section {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 4rem 0;
            flex-wrap: wrap;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.875rem 1.5rem;
            border-radius: 10px;
            font-size: 0.9rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s;
            white-space: nowrap;
        }
        
        .btn svg { width: 18px; height: 18px; min-width: 18px; }
        
        .btn-primary {
            background: var(--accent-primary);
            color: var(--bg-primary);
        }
        
        .btn-primary:hover {
            background: #0891b2;
            box-shadow: 0 0 30px var(--accent-glow);
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-medium);
        }
        
        .btn-secondary:hover {
            background: var(--bg-card-hover);
            border-color: var(--accent-primary);
        }
        
        @media (max-width: 768px) {
            .cta-section { margin: 3rem 0; gap: 0.75rem; }
            .btn { padding: 0.75rem 1.25rem; font-size: 0.85rem; }
            .btn svg { width: 16px; height: 16px; min-width: 16px; }
        }
        
        @media (max-width: 480px) {
            .cta-section { flex-direction: column; align-items: stretch; margin: 2.5rem 0; }
            .btn { justify-content: center; padding: 0.875rem 1rem; }
        }
        
        /* ===== INTERACTIVE DEMO ===== */
        .demo-container {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            overflow: hidden;
        }
        
        .demo-controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.25rem 1.5rem;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-subtle);
            flex-wrap: wrap;
        }
        
        .demo-task-select {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
        }
        
        .demo-task-select label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            white-space: nowrap;
        }
        
        .demo-task-select select {
            flex: 1;
            max-width: 400px;
            padding: 0.6rem 1rem;
            background: var(--bg-card);
            border: 1px solid var(--border-medium);
            border-radius: 8px;
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 0.85rem;
            cursor: pointer;
        }
        
        .demo-task-select select:focus {
            outline: none;
            border-color: var(--accent-primary);
        }
        
        .demo-status-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .demo-score, .demo-steps {
            text-align: center;
        }
        
        .score-label, .steps-label {
            display: block;
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .score-value, .steps-value {
            font-family: var(--font-mono);
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent-primary);
        }
        
        .demo-progress {
            flex: 1;
            max-width: 300px;
        }
        
        .demo-progress span {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .progress-bar {
            height: 6px;
            background: var(--bg-card);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-green));
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .demo-main {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 1px;
            background: var(--border-subtle);
        }
        
        .email-panel, .action-panel {
            background: var(--bg-card);
            padding: 1rem;
        }
        
        .panel-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-subtle);
            margin-bottom: 0.75rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        .panel-header svg {
            width: 16px;
            height: 16px;
            color: var(--accent-primary);
        }
        
        .email-list {
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .email-item {
            padding: 0.875rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.15s;
        }
        
        .email-item:hover {
            border-color: var(--border-medium);
            background: var(--bg-card-hover);
        }
        
        .email-item.selected {
            border-color: var(--accent-primary);
            background: rgba(6,182,212,0.08);
        }
        
        .email-item.processed {
            opacity: 0.5;
        }
        
        .email-item .email-from {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }
        
        .email-item .email-subject {
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .email-item .email-preview {
            font-size: 0.75rem;
            color: var(--text-secondary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .email-item .email-tags {
            display: flex;
            gap: 0.4rem;
            margin-top: 0.5rem;
            flex-wrap: wrap;
        }
        
        .email-tag {
            font-size: 0.65rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .email-tag.category {
            background: rgba(6,182,212,0.15);
            color: var(--accent-primary);
        }
        
        .email-tag.priority {
            background: rgba(245,158,11,0.15);
            color: var(--accent-amber);
        }
        
        .email-tag.priority-critical {
            background: rgba(244,63,94,0.15);
            color: var(--accent-rose);
        }
        
        .selected-email {
            padding: 1rem;
            background: var(--bg-secondary);
            border-radius: 10px;
            margin-bottom: 1rem;
            min-height: 80px;
        }
        
        .hint-text {
            color: var(--text-muted);
            font-size: 0.85rem;
            text-align: center;
            padding: 1rem;
        }
        
        .selected-email .email-detail-from {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        
        .selected-email .email-detail-subject {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0.25rem 0 0.5rem;
        }
        
        .selected-email .email-detail-body {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }
        
        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .action-group label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .btn-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        
        .action-btn {
            padding: 0.5rem 0.75rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }
        
        .action-btn:hover {
            background: var(--bg-card-hover);
            border-color: var(--accent-primary);
            color: var(--text-primary);
        }
        
        .action-btn.priority-critical:hover { border-color: var(--accent-rose); }
        .action-btn.priority-high:hover { border-color: var(--accent-amber); }
        
        .done-btn {
            width: 100%;
            margin-top: 1rem;
        }
        
        .demo-log {
            border-top: 1px solid var(--border-subtle);
            padding: 1rem 1.5rem;
            max-height: 150px;
            overflow: hidden;
        }
        
        .log-entries {
            max-height: 100px;
            overflow-y: auto;
            font-family: var(--font-mono);
            font-size: 0.75rem;
        }
        
        .log-entry {
            padding: 0.3rem 0;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-subtle);
        }
        
        .log-entry:last-child { border-bottom: none; }
        
        .log-entry .log-action { color: var(--accent-primary); }
        .log-entry .log-reward.positive { color: var(--accent-green); }
        .log-entry .log-reward.negative { color: var(--accent-rose); }
        
        .demo-result {
            padding: 3rem;
            text-align: center;
        }
        
        .result-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .result-icon.success {
            background: rgba(16,185,129,0.15);
            color: var(--accent-green);
        }
        
        .result-icon svg {
            width: 40px;
            height: 40px;
        }
        
        .result-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
        
        .result-score {
            margin-bottom: 2rem;
        }
        
        .result-score .score-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .result-score .score-value {
            font-family: var(--font-mono);
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .result-stats {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-bottom: 2rem;
        }
        
        .result-stats .stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        
        .result-stats .stat-value {
            font-family: var(--font-mono);
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        /* Demo Responsive Styles */
        @media (max-width: 900px) {
            .demo-main { grid-template-columns: 1fr; }
            .action-panel { border-top: 1px solid var(--border-subtle); }
        }
        
        @media (max-width: 768px) {
            .demo-container { border-radius: 12px; }
            .demo-controls { 
                flex-direction: column; 
                align-items: stretch;
                padding: 1rem;
                gap: 0.75rem;
            }
            .demo-controls .btn { width: 100%; justify-content: center; }
            .demo-task-select { 
                flex-direction: column; 
                align-items: stretch;
                gap: 0.5rem;
            }
            .demo-task-select select { max-width: none; }
            .demo-status-bar { 
                flex-wrap: wrap; 
                gap: 1rem;
                padding: 1rem;
            }
            .demo-score, .demo-steps { min-width: 60px; }
            .score-value, .steps-value { font-size: 1.25rem; }
            .demo-progress { 
                order: 3; 
                flex-basis: 100%; 
                max-width: none;
            }
            .email-panel, .action-panel { padding: 0.875rem; }
            .email-list { max-height: 280px; }
            .email-item { padding: 0.75rem; }
            .email-item .email-subject { font-size: 0.85rem; }
            .selected-email { padding: 0.875rem; min-height: 60px; }
            .action-group label { font-size: 0.7rem; margin-bottom: 0.4rem; }
            .btn-row { gap: 0.35rem; }
            .action-btn { padding: 0.45rem 0.6rem; font-size: 0.7rem; }
            .demo-log { padding: 0.875rem 1rem; }
            .log-entries { font-size: 0.7rem; }
        }
        
        @media (max-width: 480px) {
            .demo-container { border-radius: 10px; }
            .demo-controls { padding: 0.875rem; }
            .demo-task-select label { font-size: 0.8rem; }
            .demo-task-select select { 
                padding: 0.5rem 0.75rem;
                font-size: 0.8rem;
            }
            .demo-status-bar { padding: 0.875rem; gap: 0.75rem; }
            .score-value, .steps-value { font-size: 1.1rem; }
            .score-label, .steps-label { font-size: 0.65rem; }
            .demo-progress span { font-size: 0.75rem; }
            .email-panel, .action-panel { padding: 0.75rem; }
            .panel-header { 
                font-size: 0.8rem; 
                padding-bottom: 0.5rem;
                margin-bottom: 0.5rem;
            }
            .panel-header svg { width: 14px; height: 14px; }
            .email-list { max-height: 220px; gap: 0.4rem; }
            .email-item { 
                padding: 0.625rem; 
                border-radius: 8px;
            }
            .email-item .email-from { font-size: 0.7rem; }
            .email-item .email-subject { font-size: 0.8rem; }
            .email-item .email-preview { font-size: 0.7rem; }
            .email-tag { font-size: 0.6rem; padding: 0.15rem 0.4rem; }
            .selected-email { 
                padding: 0.75rem; 
                border-radius: 8px;
                margin-bottom: 0.75rem;
            }
            .selected-email .email-detail-from { font-size: 0.7rem; }
            .selected-email .email-detail-subject { font-size: 0.9rem; }
            .selected-email .email-detail-body { font-size: 0.75rem; }
            .hint-text { font-size: 0.8rem; padding: 0.75rem; }
            .action-buttons { gap: 0.75rem; }
            .action-group label { font-size: 0.65rem; }
            .action-btn { 
                padding: 0.4rem 0.5rem; 
                font-size: 0.65rem;
                border-radius: 5px;
            }
            .done-btn { 
                margin-top: 0.75rem;
                padding: 0.75rem 1rem;
                font-size: 0.85rem;
            }
            .demo-log { 
                padding: 0.75rem; 
                max-height: 120px;
            }
            .log-entries { 
                max-height: 80px; 
                font-size: 0.65rem;
            }
            .log-entry { padding: 0.25rem 0; }
            .demo-result { padding: 1.5rem 1rem; }
            .result-icon { width: 60px; height: 60px; margin-bottom: 1rem; }
            .result-icon svg { width: 30px; height: 30px; }
            .result-title { font-size: 1.25rem; margin-bottom: 1rem; }
            .result-score { margin-bottom: 1.5rem; }
            .result-score .score-value { font-size: 2rem; }
            .result-stats { gap: 1.5rem; margin-bottom: 1.5rem; }
            .result-stats .stat-value { font-size: 1rem; }
        }
        
        /* ===== FOOTER ===== */
        footer {
            border-top: 1px solid var(--border-subtle);
            padding: 2rem 0;
            margin-top: 4rem;
            text-align: center;
        }
        
        .footer-text {
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        
        .footer-text a {
            color: var(--accent-primary);
            text-decoration: none;
        }
        
        .footer-text a:hover { text-decoration: underline; }
        
        @media (max-width: 768px) {
            footer { padding: 1.5rem 0; margin-top: 3rem; }
            .footer-text { font-size: 0.8rem; }
        }
        
        @media (max-width: 480px) {
            footer { padding: 1.25rem 0; margin-top: 2.5rem; }
            .footer-text { font-size: 0.75rem; line-height: 1.5; }
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate { animation: fadeInUp 0.5s ease-out forwards; }
        .delay-1 { animation-delay: 0.1s; opacity: 0; }
        .delay-2 { animation-delay: 0.2s; opacity: 0; }
        .delay-3 { animation-delay: 0.3s; opacity: 0; }
        .delay-4 { animation-delay: 0.4s; opacity: 0; }
    </style>
</head>
<body>
    <div class="bg-glow bg-glow-1"></div>
    <div class="bg-glow bg-glow-2"></div>
    
    <div class="container">
        <!-- HEADER -->
        <header class="animate">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-icon">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <!-- Envelope base with gradient effect -->
                            <rect x="2" y="5" width="20" height="14" rx="2" fill="url(#logoGrad)" opacity="0.3"/>
                            <rect x="2" y="5" width="20" height="14" rx="2" stroke="white" stroke-width="1.5"/>
                            <!-- Flap with AI-style circuit lines -->
                            <path d="M2 7l10 6 10-6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                            <!-- Neural network dots -->
                            <circle cx="12" cy="11" r="1.5" fill="white"/>
                            <circle cx="8" cy="13" r="1" fill="white" opacity="0.7"/>
                            <circle cx="16" cy="13" r="1" fill="white" opacity="0.7"/>
                            <circle cx="6" cy="15" r="0.75" fill="white" opacity="0.5"/>
                            <circle cx="18" cy="15" r="0.75" fill="white" opacity="0.5"/>
                            <!-- Connection lines -->
                            <path d="M12 11 L8 13 M12 11 L16 13 M8 13 L6 15 M16 13 L18 15" stroke="white" stroke-width="0.75" opacity="0.6"/>
                            <defs>
                                <linearGradient id="logoGrad" x1="2" y1="5" x2="22" y2="19">
                                    <stop offset="0%" stop-color="#06b6d4"/>
                                    <stop offset="100%" stop-color="#8b5cf6"/>
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <div class="title-group">
                        <h1>Email Triage Environment</h1>
                        <p>AI-powered email classification & prioritization</p>
                    </div>
                </div>
                <div class="status-badges">
                    <span class="badge badge-live">Running</span>
                    <span class="badge">OpenEnv</span>
                    <span class="badge">v1.0.0</span>
                </div>
            </div>
        </header>
        
        <!-- STATS BAR -->
        <div class="stats-bar animate delay-1">
            <div class="stat-item">
                <div class="stat-value">3</div>
                <div class="stat-label">Tasks</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">7</div>
                <div class="stat-label">Actions</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">30</div>
                <div class="stat-label">Emails</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">0-1</div>
                <div class="stat-label">Score Range</div>
            </div>
        </div>
        
        <!-- TASKS -->
        <section class="animate delay-2">
            <div class="section-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M8 12h8"/>
                    <path d="M12 8v8"/>
                </svg>
                <h2 class="section-title">Available Tasks</h2>
            </div>
            <div class="task-grid">
                <div class="task-card easy">
                    <div class="task-header">
                        <span class="task-number">01</span>
                        <span class="difficulty-badge">Easy</span>
                    </div>
                    <h3 class="task-title">Basic Classification</h3>
                    <p class="task-desc">Classify emails into categories: work, personal, spam, newsletter, urgent</p>
                    <div class="task-meta">
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                            5 emails
                        </span>
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                            50 steps
                        </span>
                    </div>
                </div>
                <div class="task-card medium">
                    <div class="task-header">
                        <span class="task-number">02</span>
                        <span class="difficulty-badge">Medium</span>
                    </div>
                    <h3 class="task-title">Classification + Priority</h3>
                    <p class="task-desc">Classify emails and assign priority levels: critical, high, medium, low</p>
                    <div class="task-meta">
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                            10 emails
                        </span>
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                            100 steps
                        </span>
                    </div>
                </div>
                <div class="task-card hard">
                    <div class="task-header">
                        <span class="task-number">03</span>
                        <span class="difficulty-badge">Hard</span>
                    </div>
                    <h3 class="task-title">Full Email Triage</h3>
                    <p class="task-desc">Handle complex emails with escalation, archiving, and deferral decisions</p>
                    <div class="task-meta">
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                            15 emails
                        </span>
                        <span class="meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                            150 steps
                        </span>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- INTERACTIVE DEMO -->
        <section class="animate delay-3" id="demo-section">
            <div class="section-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                <h2 class="section-title">Try It Live</h2>
                <span class="badge badge-live" style="margin-left: auto;">Interactive</span>
            </div>
            
            <div class="demo-container">
                <div class="demo-controls">
                    <div class="demo-task-select">
                        <label for="task-select">Select Task:</label>
                        <select id="task-select">
                            <option value="task1">Task 1 - Basic Classification (5 emails)</option>
                            <option value="task2">Task 2 - Classification + Priority (10 emails)</option>
                            <option value="task3">Task 3 - Full Triage (15 emails)</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" id="start-btn" onclick="startDemo()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                        Start Task
                    </button>
                </div>
                
                <div class="demo-workspace" id="demo-workspace" style="display: none;">
                    <div class="demo-status-bar">
                        <div class="demo-score">
                            <span class="score-label">Reward</span>
                            <span class="score-value" id="current-reward">0.00</span>
                        </div>
                        <div class="demo-progress">
                            <span id="progress-text">0 / 0 emails</span>
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="demo-steps">
                            <span class="steps-label">Steps</span>
                            <span class="steps-value" id="step-count">0</span>
                        </div>
                    </div>
                    
                    <div class="demo-main">
                        <div class="email-panel">
                            <div class="panel-header">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                                <span>Inbox</span>
                            </div>
                            <div class="email-list" id="email-list">
                                <!-- Emails will be populated here -->
                            </div>
                        </div>
                        
                        <div class="action-panel">
                            <div class="panel-header">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                                <span>Actions</span>
                            </div>
                            <div class="selected-email" id="selected-email">
                                <p class="hint-text">Select an email to perform actions</p>
                            </div>
                            <div class="action-buttons" id="action-buttons" style="display: none;">
                                <div class="action-group">
                                    <label>Category:</label>
                                    <div class="btn-row">
                                        <button class="action-btn" onclick="classifyEmail('work')">Work</button>
                                        <button class="action-btn" onclick="classifyEmail('personal')">Personal</button>
                                        <button class="action-btn" onclick="classifyEmail('spam')">Spam</button>
                                        <button class="action-btn" onclick="classifyEmail('newsletter')">Newsletter</button>
                                        <button class="action-btn" onclick="classifyEmail('urgent')">Urgent</button>
                                    </div>
                                </div>
                                <div class="action-group">
                                    <label>Priority:</label>
                                    <div class="btn-row">
                                        <button class="action-btn priority-critical" onclick="prioritizeEmail('critical')">Critical</button>
                                        <button class="action-btn priority-high" onclick="prioritizeEmail('high')">High</button>
                                        <button class="action-btn priority-medium" onclick="prioritizeEmail('medium')">Medium</button>
                                        <button class="action-btn priority-low" onclick="prioritizeEmail('low')">Low</button>
                                    </div>
                                </div>
                                <div class="action-group">
                                    <label>Triage:</label>
                                    <div class="btn-row">
                                        <button class="action-btn triage-btn" onclick="triageEmail('ESCALATE')">Escalate</button>
                                        <button class="action-btn triage-btn" onclick="triageEmail('ARCHIVE')">Archive</button>
                                        <button class="action-btn triage-btn" onclick="triageEmail('DEFER')">Defer</button>
                                    </div>
                                </div>
                            </div>
                            <button class="btn btn-primary done-btn" id="done-btn" onclick="finishTask()" style="display: none;">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                                Complete Task
                            </button>
                        </div>
                    </div>
                    
                    <div class="demo-log">
                        <div class="panel-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                            <span>Activity Log</span>
                        </div>
                        <div class="log-entries" id="log-entries"></div>
                    </div>
                </div>
                
                <div class="demo-result" id="demo-result" style="display: none;">
                    <div class="result-icon success" id="result-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    </div>
                    <h3 class="result-title" id="result-title">Task Complete!</h3>
                    <div class="result-score">
                        <span class="score-label">Final Score</span>
                        <span class="score-value" id="final-score">0.00</span>
                    </div>
                    <div class="result-stats">
                        <div class="stat">
                            <span class="stat-label">Steps</span>
                            <span class="stat-value" id="final-steps">0</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Reward</span>
                            <span class="stat-value" id="final-reward">0.00</span>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="resetDemo()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
                        Try Again
                    </button>
                </div>
            </div>
        </section>
        
        <!-- ACTIONS -->
        <section class="animate delay-3">
            <div class="section-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                <h2 class="section-title">Available Actions</h2>
            </div>
            <div class="actions-grid">
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                    </div>
                    <div class="action-name">CLASSIFY</div>
                    <div class="action-desc">Assign category</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    </div>
                    <div class="action-name">PRIORITIZE</div>
                    <div class="action-desc">Set urgency</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    </div>
                    <div class="action-name">REPLY_PLAN</div>
                    <div class="action-desc">Draft response</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    </div>
                    <div class="action-name">ESCALATE</div>
                    <div class="action-desc">Forward up</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/></svg>
                    </div>
                    <div class="action-name">ARCHIVE</div>
                    <div class="action-desc">Store away</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    </div>
                    <div class="action-name">DEFER</div>
                    <div class="action-desc">Handle later</div>
                </div>
                <div class="action-item">
                    <div class="action-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <div class="action-name">DONE</div>
                    <div class="action-desc">Complete task</div>
                </div>
            </div>
        </section>
        
        <!-- API ENDPOINTS -->
        <section class="animate delay-4">
            <div class="section-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 20V10"/>
                    <path d="M12 20V4"/>
                    <path d="M6 20v-6"/>
                </svg>
                <h2 class="section-title">API Endpoints</h2>
            </div>
            <div class="endpoints-list">
                <div class="endpoint-row">
                    <span class="method method-get">GET</span>
                    <span class="endpoint-path">/health</span>
                    <span class="endpoint-desc">Check if the service is running</span>
                </div>
                <div class="endpoint-row">
                    <span class="method method-get">GET</span>
                    <span class="endpoint-path">/tasks</span>
                    <span class="endpoint-desc">List all available tasks with metadata</span>
                </div>
                <div class="endpoint-row">
                    <span class="method method-post">POST</span>
                    <span class="endpoint-path">/reset</span>
                    <span class="endpoint-desc">Reset environment and load a task</span>
                </div>
                <div class="endpoint-row">
                    <span class="method method-post">POST</span>
                    <span class="endpoint-path">/step</span>
                    <span class="endpoint-desc">Execute an action and get observation</span>
                </div>
                <div class="endpoint-row">
                    <span class="method method-get">GET</span>
                    <span class="endpoint-path">/state</span>
                    <span class="endpoint-desc">Get current environment state</span>
                </div>
                <div class="endpoint-row">
                    <span class="method method-get">GET</span>
                    <span class="endpoint-path">/docs</span>
                    <span class="endpoint-desc">Interactive Swagger documentation</span>
                </div>
            </div>
        </section>
        
        <!-- CTA -->
        <div class="cta-section">
            <a href="/docs" class="btn btn-primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                Interactive API Docs
            </a>
            <a href="/api" class="btn btn-secondary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                View JSON API
            </a>
        </div>
        
        <!-- FOOTER -->
        <footer>
            <p class="footer-text">
                Built for <strong>OpenEnv Hackathon</strong> &middot; 
                <a href="https://huggingface.co/spaces/ayushjha85/openenv-email-triage">View on Hugging Face</a>
            </p>
        </footer>
    </div>
    
    <script>
        // ===== Interactive Demo State =====
        let demoState = {
            emails: [],
            selectedEmail: null,
            currentReward: 0,
            stepCount: 0,
            processedCount: 0,
            totalCount: 0
        };
        
        async function startDemo() {
            const taskSelect = document.getElementById('task-select');
            const taskId = taskSelect.value;
            
            try {
                const response = await fetch('/reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_id: taskId })
                });
                
                if (!response.ok) throw new Error('Failed to reset environment');
                
                const data = await response.json();
                
                demoState.emails = data.observation.emails;
                demoState.currentReward = 0;
                demoState.stepCount = 0;
                demoState.processedCount = data.observation.processed_count;
                demoState.totalCount = data.observation.total_count;
                demoState.selectedEmail = null;
                
                document.getElementById('demo-workspace').style.display = 'block';
                document.getElementById('demo-result').style.display = 'none';
                document.getElementById('done-btn').style.display = 'block';
                
                updateUI();
                addLog('Environment reset', 'Started ' + taskId);
            } catch (error) {
                console.error('Error:', error);
                addLog('Error', error.message);
            }
        }
        
        function updateUI() {
            // Update stats
            document.getElementById('current-reward').textContent = demoState.currentReward.toFixed(2);
            document.getElementById('step-count').textContent = demoState.stepCount;
            document.getElementById('progress-text').textContent = 
                `${demoState.processedCount} / ${demoState.totalCount} emails`;
            
            const progress = demoState.totalCount > 0 
                ? (demoState.processedCount / demoState.totalCount) * 100 
                : 0;
            document.getElementById('progress-fill').style.width = progress + '%';
            
            // Render email list
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '';
            
            demoState.emails.forEach(email => {
                const div = document.createElement('div');
                div.className = 'email-item' + 
                    (email.is_processed ? ' processed' : '') +
                    (demoState.selectedEmail === email.id ? ' selected' : '');
                
                let tagsHtml = '';
                if (email.predicted_category) {
                    tagsHtml += `<span class="email-tag category">${email.predicted_category}</span>`;
                }
                if (email.predicted_priority) {
                    const priorityClass = email.predicted_priority === 'critical' ? 'priority-critical' : 'priority';
                    tagsHtml += `<span class="email-tag ${priorityClass}">${email.predicted_priority}</span>`;
                }
                if (email.is_escalated) tagsHtml += '<span class="email-tag" style="background:rgba(244,63,94,0.15);color:var(--accent-rose)">ESCALATED</span>';
                if (email.is_archived) tagsHtml += '<span class="email-tag" style="background:rgba(82,82,91,0.3);color:var(--text-muted)">ARCHIVED</span>';
                if (email.is_deferred) tagsHtml += '<span class="email-tag" style="background:rgba(245,158,11,0.15);color:var(--accent-amber)">DEFERRED</span>';
                
                div.innerHTML = `
                    <div class="email-from">${email.sender}</div>
                    <div class="email-subject">${email.subject}</div>
                    <div class="email-preview">${email.body.substring(0, 100)}...</div>
                    ${tagsHtml ? '<div class="email-tags">' + tagsHtml + '</div>' : ''}
                `;
                
                div.onclick = () => selectEmail(email.id);
                emailList.appendChild(div);
            });
            
            // Update selected email panel
            updateSelectedEmail();
        }
        
        function selectEmail(emailId) {
            demoState.selectedEmail = emailId;
            updateUI();
        }
        
        function updateSelectedEmail() {
            const container = document.getElementById('selected-email');
            const actionButtons = document.getElementById('action-buttons');
            
            if (!demoState.selectedEmail) {
                container.innerHTML = '<p class="hint-text">Select an email to perform actions</p>';
                actionButtons.style.display = 'none';
                return;
            }
            
            const email = demoState.emails.find(e => e.id === demoState.selectedEmail);
            if (!email) return;
            
            container.innerHTML = `
                <div class="email-detail-from">From: ${email.sender}</div>
                <div class="email-detail-subject">${email.subject}</div>
                <div class="email-detail-body">${email.body}</div>
            `;
            
            actionButtons.style.display = 'flex';
        }
        
        async function executeAction(action) {
            try {
                const response = await fetch('/step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action })
                });
                
                if (!response.ok) throw new Error('Action failed');
                
                const data = await response.json();
                
                demoState.emails = data.observation.emails;
                demoState.currentReward += data.reward;
                demoState.stepCount++;
                demoState.processedCount = data.observation.processed_count;
                
                const rewardClass = data.reward >= 0 ? 'positive' : 'negative';
                addLog(action.action_type, 
                    `${action.email_id || ''} → <span class="log-reward ${rewardClass}">${data.reward >= 0 ? '+' : ''}${data.reward.toFixed(2)}</span>`);
                
                if (data.done) {
                    showResult(data.info.final_score);
                } else {
                    updateUI();
                }
            } catch (error) {
                console.error('Error:', error);
                addLog('Error', error.message);
            }
        }
        
        function classifyEmail(category) {
            if (!demoState.selectedEmail) return;
            executeAction({
                action_type: 'CLASSIFY',
                email_id: demoState.selectedEmail,
                category: category
            });
        }
        
        function prioritizeEmail(priority) {
            if (!demoState.selectedEmail) return;
            executeAction({
                action_type: 'PRIORITIZE',
                email_id: demoState.selectedEmail,
                priority: priority
            });
        }
        
        function triageEmail(actionType) {
            if (!demoState.selectedEmail) return;
            executeAction({
                action_type: actionType,
                email_id: demoState.selectedEmail
            });
        }
        
        function finishTask() {
            executeAction({ action_type: 'DONE' });
        }
        
        function showResult(finalScore) {
            document.getElementById('demo-workspace').style.display = 'none';
            document.getElementById('demo-result').style.display = 'block';
            
            document.getElementById('final-score').textContent = finalScore.toFixed(2);
            document.getElementById('final-steps').textContent = demoState.stepCount;
            document.getElementById('final-reward').textContent = demoState.currentReward.toFixed(2);
        }
        
        function resetDemo() {
            document.getElementById('demo-workspace').style.display = 'none';
            document.getElementById('demo-result').style.display = 'none';
            document.getElementById('log-entries').innerHTML = '';
            demoState = {
                emails: [],
                selectedEmail: null,
                currentReward: 0,
                stepCount: 0,
                processedCount: 0,
                totalCount: 0
            };
        }
        
        function addLog(action, detail) {
            const logEntries = document.getElementById('log-entries');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="log-action">[${action}]</span> ${detail}`;
            logEntries.insertBefore(entry, logEntries.firstChild);
        }
    </script>
</body>
</html>
'''


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with beautiful landing page."""
    return LANDING_PAGE_HTML


@app.get("/api")
async def api_info() -> Dict[str, Any]:
    """API information endpoint (JSON)."""
    return {
        "name": "openenv-email-triage",
        "title": "OpenEnv Email Triage Environment",
        "version": "1.0.0",
        "description": "AI email triage environment for OpenEnv hackathon",
        "endpoints": {
            "POST /reset": "Reset environment with a task",
            "POST /step": "Execute an action",
            "GET /state": "Get current state",
            "GET /tasks": "List available tasks",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/tasks")
async def get_available_tasks() -> Dict[str, Any]:
    """List all available tasks."""
    return {
        "tasks": list_tasks(),
        "total": len(TASKS)
    }


@app.post("/reset", response_model=ResetResponse)
async def reset_environment(
    request: ResetRequest = Body(default_factory=ResetRequest)
) -> ResetResponse:
    """
    Reset the environment with a specified task.
    
    Args:
        request: Contains task_id to load
        
    Returns:
        Initial observation and task info
    """
    try:
        task = get_task(request.task_id)
        logger.info(f"Resetting environment with task: {task.task_id}")
        
        observation = env.reset(
            task_id=task.task_id,
            emails=task.emails,
            task_description=task.description,
            grader=task.grader,
            max_steps=task.max_steps
        )
        
        return ResetResponse(
            observation=observation,
            info={
                "task": task.to_dict(),
                "message": f"Environment reset with {task.name}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step", response_model=StepResponse)
async def execute_step(request: StepRequest) -> StepResponse:
    """
    Execute an action in the environment.
    
    Args:
        request: Contains the action to execute
        
    Returns:
        Observation, reward, done status, and additional info
    """
    try:
        logger.info(f"Executing action: {request.action.action_type}")
        
        observation, reward, done, info = env.step(request.action)
        
        return StepResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info
        )
    except Exception as e:
        logger.error(f"Error executing step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state", response_model=State)
async def get_state() -> State:
    """
    Get the current environment state.
    
    Returns:
        Current state including observation, reward, and done status
    """
    try:
        return env.state()
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
