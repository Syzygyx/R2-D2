% SITH — Shadow Integration & Translation Hub  
% A Raspberry Pi–based Modernization of R2-D2 Control Systems  
% **Prepared by: Syzygyx, Inc.**

---

# Table of Contents
1. [Executive Summary](#executive-summary)  
2. [Goals & Success Criteria](#goals--success-criteria)  
3. [Technical Approach (SITH)](#technical-approach-sith)  
4. [Hardware Architecture & Pi HAT Strategy](#hardware-architecture--pi-hat-strategy)  
5. [Phased Plan, Deliverables & Budget](#phased-plan-deliverables--budget)  
    - [Phase I & II — 1-Month Sprint](#phase-i--ii--1-month-sprint)  
    - [Phase III — Physical Build](#phase-iii--physical-build)  
    - [Phase IV — Curriculum Development](#phase-iv--curriculum-development)  
6. [Timeline Overview](#timeline-overview)  
7. [Budget Summary](#budget-summary)  
8. [Risk Management & Safety](#risk-management--safety)  
9. [Acceptance Criteria](#acceptance-criteria)  
10. [Repository & Maintainability](#repository--maintainability)  
11. [Next Steps](#next-steps)

---

# Executive Summary

**SITH (Shadow Integration & Translation Hub)** is a lean, open-source project to port legacy **Shadow/MarcDuino** R2-D2 control to a modern **Raspberry Pi** stack using **Python**, optional **ROS 2** simulation, and on-device **TensorFlow Lite** vision. It preserves classic behaviors (drive, dome, servos, lights, sounds, sequences) while adding modern capabilities (simulation, AI, curriculum integration).

- **Phases I & II** (software + AI/sim) completed in **1 month**, **$5,000 total**.  
- **Phase III** (physical build) uses a **club hardware budget** (~$800–$1,200 for a Budget R2).  
- **Phase IV** develops educational curricula, aligned with a **Master's in AI (MS AI)** program, but usable by high school and club students.

Deliverables emphasize maintainability (clear wiring, YAML sequences), safety (override, e-stop, fuses), and longevity (open license, clear repo, simulation-first development).

---

# Goals & Success Criteria

### Primary Goals
1. **Shadow parity on Raspberry Pi**: Run legacy-style commands with <100 ms loop latency.  
2. **Student-friendly stack**: HAL, YAML sequences, clean Python.  
3. **On-device AI**: Face/person detection that drives dome tracking; manual override always wins.  
4. **Simulation support**: Run code in Gazebo with minimal changes.

### Success Criteria
- Drive, dome, 12–16 servos, LEDs, and sounds controlled from the Pi.  
- Run 3+ named sequences end-to-end.  
- Autonomous dome face-tracking with safe manual override.  
- Gazebo simulation demonstrating same control logic.

---

# Technical Approach (SITH)

SITH provides a **thin, testable software layer** independent of hardware:

- **HAL Interfaces** (`motors`, `dome`, `servos`, `leds`, `sound`)  
  - `RealBackend`: Sabertooth (UART), PCA9685 (I²C), GPIO, NeoPixels, audio  
  - `LoggerBackend` / `SimBackend`: Logs or publishes to ROS topics, no hardware needed
- **MarcDuino/Shadow Emulator**: PTY serial device parsing ASCII commands → HAL calls
- **Sequence Engine**: YAML-defined timed actions (servo moves, sounds, lights)
- **AI Module**: TFLite face/person detection → dome "suggestations"
- **Control Modes**: Manual > Assisted > Autonomous
- **Simulation**: Gazebo + ROS 2 URDF (diff-drive, dome joint, hero servos)

> **Key advantage:** ~95% of development can happen **without physical hardware**, using the emulator and Gazebo.

---

# Hardware Architecture & Pi HAT Strategy

To reduce wiring and improve reliability for students, SITH uses a **stacked Pi HAT approach**:

| Layer | Component | Purpose |
|-------|-----------|---------|
| Top | NeoPixel Bonnet *(optional)* | Dedicated DMA channel for WS2812/NeoPixel logic LEDs |
| Mid | PCA9685 Servo HAT | 16-ch hardware PWM for dome panels, utility arms, periscopes |
| Lower | PiJuice HAT | 5 V regulation, UPS, power events, brownout protection |
| Base | Raspberry Pi 4/5 | Runs SITH, TFLite, and optional ROS 2 |

**External Modules**  
- **Sabertooth 2×12** motor driver via UART for foot motors  
- Optional **SyRen 10** for dome rotation  
- 12 V battery, fused distribution, 5 V buck if PiJuice not used

**Why HATs**  
- Fewer wires, more reliability  
- Hardware-timed PWM → smooth servos  
- Easier student assembly & debugging  
- Scalable (add PCA9685 boards for more servos)

---

# Phased Plan, Deliverables & Budget

## Phase I & II — 1-Month Sprint  
**Budget:** $5,000 total • **Duration:** 4 weeks

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| **1 — Foundation** | 🧠 Core architecture | Repo scaffold, HAL, PTY emulator, parser skeleton, unit tests |
| **2 — Core Features** | ⚙️ Functional parity | Full parser, YAML sequence engine, PCA9685 & Sabertooth stubs, TFLite scaffold |
| **3 — Integration & Simulation** | 🧪 End-to-end behavior | Teleop + sequences in LoggerBackend & Gazebo, dome face-tracking, manual override |
| **4 — Demo & Docs** | 🚀 Delivery | Phase I functionality in sim, Phase II AI demo (face-tracking + override), Gazebo demo, wiring diagrams, developer docs |

---

## Phase III — Physical Build  
**Budget:** $800–$1,200 (separate) • **Duration:** 3–5 weeks

- **Budget R2 path**: PVC/printed frame, scooter motors, Sabertooth 2×12, 12–16 servos on PCA9685, Pi 4 + PiJuice + LED bonnet  
- Install, wire, calibrate; add safety (e-stop, fuses, labels)  
- Acceptance demo: teleop, 3+ sequences, dome face-tracking with override

*(Optional Hero/Aluminum build: $2,500–$4,000+; 8–12+ weeks.)*

---

## Phase IV — Curriculum Development

**Objective**: Turn SITH into a **teaching platform**, aligned with **MS in AI** curriculum but usable at multiple levels.

| Module | Focus | Skills |
|--------|-------|-------|
| 1 | System Overview | Systems thinking, diagrams |
| 2 | GPIO & Servos | Embedded control |
| 3 | Protocol Parsing | State machines, legacy translation |
| 4 | AI Vision | Edge ML, performance |
| 5 | ROS 2 Simulation | Digital twins |
| 6 | Hybrid Control | Mode switching, safety |
| 7 | Capstone | Integration, teamwork |

**Deliverables**
- Lesson plans, slides, Jupyter notebooks, assessments  
- Instructor notes, capstone templates  
- `/curriculum/` in repo + optional GitHub Pages site

---

# Timeline Overview

| Month | Milestone |
|-------|-----------|
| 1 | Phase I & II sprint (software + AI/sim) |
| 2–3 | Phase III physical build |
| 4+ | Phase IV curriculum development, pilot workshops |

---

# Budget Summary

| Phase | Description | Cost |
|-------|-------------|------|
| I & II | Software + AI/sim sprint | **$5,000** |
| III | Club hardware (Budget R2) | $800–$1,200 (separate) |
| IV | Curriculum authoring (optional) | $1,000–$1,500 |

**Licensing:** Code under MIT / Apache 2.0; Curriculum under CC-BY. Public GitHub repo ensures longevity.

---

# Risk Management & Safety

- **Power**: PiJuice or good buck regulators; stagger servo motion.  
- **Control Safety**: watchdog, e-stop, instant manual override.  
- **Schedule**: Emulator + sim first; hardware integration last.  
- **Student turnover**: clear docs, curriculum, contribution guide.

---

# Acceptance Criteria

- **Phase I & II**: Teleop + sequences in sim; dome face-tracking with override; Gazebo demo.  
- **Phase III**: Rolling chassis, stable power, 3+ sequences, face-tracking with override.  
- **Phase IV**: Published curriculum; one pilot session.

---

# Repository & Maintainabilitysith/
sith_core/          # Parser, HAL, sequence engine
sith_backends/
real/             # Sabertooth, PCA9685, GPIO, LEDs, sound
sim/              # LoggerBackend, ROS 2 bridge
sith_emulator/      # PTY serial emulator
sith_sequences/     # YAML routines
simulation/         # URDF, controllers, launch files
curriculum/         # Lessons, slides, notebooks
docs/               # Wiring diagrams, setup, safety
tests/              # Pytest- CI: parser & sequence tests + headless sim log checks.  
- Style: PEP-8, short CONTRIBUTING.md.

---

# Next Steps

1. ✅ Approve Phases I & II at $5,000 (1-month sprint).  
2. ✅ Confirm hardware purchasing plan for Phase III (Budget R2 path).  
3. 🧭 Assign faculty/mentor liaison for weekly 30-min check-ins.  
4. 🦾 Decide ROS 2 integration scope now (recommended "yes").  
5. 🚀 Kickoff repo scaffold + emulator Week 1.

---

**SITH is a bridge between legacy control and modern AI robotics**—inspiring for students, practical for builders, and sustainable for years to come.