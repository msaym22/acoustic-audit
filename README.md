# ⚡ High-Performance Student Record System

![Language](https://img.shields.io/badge/Language-C++17-blue.svg) ![Performance](https://img.shields.io/badge/Performance-O(n)_Search-brightgreen.svg) ![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg) ![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

A robust, dependency-free **C++ System Utility** engineered for efficient academic record management.
Unlike standard beginner projects, this system demonstrates **low-level memory management**, **custom file serialization**, and **weighted algorithmic grading** without relying on external SQL databases.

---

## 🚀 Technical Engineering Highlights

### 1. 💾 Custom Data Persistence Engine
* **Raw File I/O:** Implemented a custom parser (`Load_file.cpp`) to serialize/deserialize object data to a flat-file database (`Student.txt`).
* **ACID-Like Integrity:** Validates data types and constraints before committing transactions to disk, preventing data corruption during runtime.

### 2. 🧮 Weighted Grading Algorithm
* **Logic:** Implements a complex **Weighted Average Formula** rather than simple arithmetic means.
* **Precision:** Uses floating-point architecture to ensure GPA accuracy up to 2 decimal places.

### 3. ⚡ Algorithmic Optimization
* **Search Complexity:** Optimized **Linear Search (O(n))** for instant record retrieval via unique Roll IDs.
* **Sorting Strategy:** Maintains a sorted dataset using an optimized **Bubble Sort** algorithm, ensuring reports are always ranked by performance.

---

## 🛠️ Core Capabilities

| Feature | Technical Description |
| :--- | :--- |
| **Smart Insertion** | Creates records with strict type-checking and duplicate key prevention. |
| **Auto-Grading** | Automatically computes percentage and assigns Letter Grades (A+ to F). |
| **Topper Analysis** | A traversal algorithm that identifies the top 3 highest-performing students in O(n) time. |
| **Statistical Report** | Calculates class variance, averages, and outliers (Highest/Lowest scores). |

---

## ⚖️ The Grading Logic (Algorithm)

The system calculates final grades based on a specific academic weight distribution:

| Assessment Component | Criteria Considered | Weightage |
| :--- | :--- | :--- |
| **Quizzes** | Top 3 Quizzes | **15%** |
| **Assignments** | Top 3 Assignments | **15%** |
| **Mid-Term Exam** | Raw Score | **20%** |
| **Final Exam** | Raw Score | **50%** |

### 📊 Grade Thresholds
| Grade | Percentage |
| :--- | :--- |
| **A+** | > 95% |
| **A** | > 90% |
| **B** | > 80% |
| **C** | > 70% |
| **D** | > 50% |
| **F** | ≤ 50% |

---