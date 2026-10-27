# 🏛️ LexAI Legal — ИИ-аналитик юридических документов на риски и противоречия

[![GitHub Project](https://img.shields.io/badge/GitHub%20Projects-LexAI%20Board%20%233-blue?style=for-the-badge&logo=github)](https://github.com/users/Ktofin/projects/3)
[![Scrum Sprints](https://img.shields.io/badge/Scrum-4%20Sprints%20%7C%2068%20SP-green?style=for-the-badge)](https://github.com/Ktofin/LexAI/milestones)
[![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%2014%20%7C%20PostgreSQL-orange?style=for-the-badge)](https://github.com/Ktofin/LexAI)
[![Design System](https://img.shields.io/badge/Design%20System-Warm%20Linen%20%26%20Terracotta-E06738?style=for-the-badge)](design-system/lexai-legal/MASTER.md)

> **Курсовой проект:** «Управление жизненным циклом программного обеспечения»  
> **Студент:** К.А. Фёдоров (группа 1-41м)  
> **Преподаватель:** доцент, канд. техн. наук А.М. Садыков  
> **ИГЭУ, Кафедра ПОКС, 2026**

---

## 📌 О проекте

**LexAI Legal** — интеллектуальный сервис автоматизированного юридического аудита и пре-скоринга договоров компании. Система выявляет скрытые финансовые риски, внутренние правовые коллизии между разделами, классифицирует типы договоров, извлекает ключевые сущности, находит риски и позволяет формировать отчёты с подсветкой и экспортом в PDF.

Проект разработан в строгом соответствии с картой историй пользователя (**User Story Mapping**, сервис Miro), где четко выделены активности: **Управление аккаунтом**, **Загрузка документов**, **Анализ документов**, **Просмотр результатов** и **Настройка параметров и безопасность**.

---

## 🚀 Быстрые ссылки

* 📋 **[Интерактивная доска проекта в GitHub Projects #3](https://github.com/users/Ktofin/projects/3)**
* 🎯 **[Бэклог задач и спецификации User Stories (Issues #20–#36)](https://github.com/Ktofin/LexAI/issues)**
* 🏁 **[Спринты разработки (Milestones: 28.10.2026 – 22.12.2026)](https://github.com/Ktofin/LexAI/milestones)**
* 🎨 **[Документация дизайн-системы (Tokens & Components)](design-system/lexai-legal/MASTER.md)**
* 🖌️ **[Файл прототипа интерфейса (FigCraft)](Legal_AI_Analyst.figcraft)**

---

## 🗓️ Спринты разработки (Scrum, старт: 28.10.2026)

| Спринт | Сроки | Состав задач (User Stories) | Оценка | Статус |
|---|---|---|---|---|
| **Спринт 1** | **28.10.2026 – 10.11.2026** | `E-0`, `US-1.1`, `US-1.2`, `US-2.1`, `US-2.2`, `US-2.3` | **18 SP** | В работе (Done: E-0, US-1.1, US-1.2) |
| **Спринт 2** | **11.11.2026 – 24.11.2026** | `US-3.1`, `US-3.2`, `US-3.3`, `US-3.4` | **17 SP** | Запланирован |
| **Спринт 3** | **25.11.2026 – 08.12.2026** | `US-4.1`, `US-4.2`, `US-4.3`, `US-4.4` | **16 SP** | Запланирован |
| **Спринт 4** | **09.12.2026 – 22.12.2026** | `US-5.1`, `US-5.2`, `US-5.3` | **17 SP** | Запланирован |
| **ИТОГО** | **8 недель (4 спринта)** | **17 задач / User Stories MVP** | **68 SP** | **100% покрытие MVP** |

---

## 🎯 Бэклог MVP (17 User Stories по Карте Историй Miro)

| № | Issue | Код | Наименование User Story | Активность (Miro) | Спринт | SP |
|---|---|---|---|---|---|---|
| 1 | [#20](https://github.com/Ktofin/LexAI/issues/20) | `E-0` | Создание технической основы и окружения разработки | Инфраструктура | Спринт 1 | 5 SP |
| 2 | [#21](https://github.com/Ktofin/LexAI/issues/21) | `US-1.1` | Вход и регистрация в системе | Управление аккаунтом | Спринт 1 | 3 SP |
| 3 | [#22](https://github.com/Ktofin/LexAI/issues/22) | `US-1.2` | Базовый профиль пользователя (имя, email) | Управление профилем | Спринт 1 | 2 SP |
| 4 | [#23](https://github.com/Ktofin/LexAI/issues/23) | `US-2.1` | Ручная загрузка файлов PDF и DOCX | Загрузка документов | Спринт 1 | 3 SP |
| 5 | [#24](https://github.com/Ktofin/LexAI/issues/24) | `US-2.2` | Базовое извлечение текста из документов PDF и DOCX | Загрузка документов | Спринт 1 | 3 SP |
| 6 | [#25](https://github.com/Ktofin/LexAI/issues/25) | `US-2.3` | Гостевой режим для быстрого теста без регистрации | Загрузка документов | Спринт 1 | 2 SP |
| 7 | [#26](https://github.com/Ktofin/LexAI/issues/26) | `US-3.1` | Автоматическая классификация типа договора | Анализ документов | Спринт 2 | 3 SP |
| 8 | [#27](https://github.com/Ktofin/LexAI/issues/27) | `US-3.2` | Извлечение ключевых сущностей договора | Анализ документов | Спринт 2 | 5 SP |
| 9 | [#28](https://github.com/Ktofin/LexAI/issues/28) | `US-3.3` | ИИ-анализ юридических рисков договора | Анализ документов | Спринт 2 | 5 SP |
| 10 | [#29](https://github.com/Ktofin/LexAI/issues/29) | `US-3.4` | Поиск противоречий и коллизий между разделами | Анализ документов | Спринт 2 | 4 SP |
| 11 | [#30](https://github.com/Ktofin/LexAI/issues/30) | `US-4.1` | Простой отчёт с найденными рисками в браузере | Просмотр результатов | Спринт 3 | 5 SP |
| 12 | [#31](https://github.com/Ktofin/LexAI/issues/31) | `US-4.2` | Просмотр результатов на экране с подсветкой рисков | Просмотр результатов | Спринт 3 | 5 SP |
| 13 | [#32](https://github.com/Ktofin/LexAI/issues/32) | `US-4.3` | Экспорт отчёта в PDF | Просмотр результатов | Спринт 3 | 3 SP |
| 14 | [#33](https://github.com/Ktofin/LexAI/issues/33) | `US-4.4` | Возможность поделиться отчётом с коллегой | Просмотр результатов | Спринт 3 | 3 SP |
| 15 | [#34](https://github.com/Ktofin/LexAI/issues/34) | `US-5.1` | Настройка параметров анализа документа | Настройка параметров | Спринт 4 | 5 SP |
| 16 | [#35](https://github.com/Ktofin/LexAI/issues/35) | `US-5.2` | Управление настройками безопасности и сессиями | Безопасность | Спринт 4 | 4 SP |
| 17 | [#36](https://github.com/Ktofin/LexAI/issues/36) | `US-5.3` | Сквозное интеграционное тестирование и приёмка MVP | Релиз и приёмка | Спринт 4 | 8 SP |

---

## 🎨 Дизайн-система проекта

Интерфейс спроектирован по канонам корпоративного UX/UI и стандартов доступности **WCAG 2.1 AAA**:
* **Светлая тема (Warm Linen & Terracotta):**
  * Фон: `#FAF9F5` (Warm Linen Canvas), карточки: `#FFFFFF` / `#F5F3ED`
  * Акцентный цвет: `#D97757` (Terracotta Accent), текст: `#141413`
* **Тёмная тема (Deep Obsidian):**
  * Фон: `#141413` (Deep Obsidian Canvas), карточки: `#1F1E1B`
  * Бордеры: `#2D2B26`, акцент: `#E06738`
* **Мобильная адаптация:** адаптивная сетка под дисплеи смартфонов 390×844 px.

---

## 🛠️ Стек технологий

* **Frontend:** Next.js 14 (React, TypeScript), Tailwind CSS, Headless UI, PDF.js
* **Backend:** Python 3.12, FastAPI (REST API, SSE-стриминг), Pydantic v2, python-docx
* **AI / NLP:** LangChain, BGE-M3 Embeddings, pgvector, открытые юридические модели
* **Database & Storage:** PostgreSQL 16 (metadata, audit log), MinIO S3 (PDF/DOCX хранилище)
* **DevOps & QA:** Docker, Docker Compose, Pytest (покрытие > 85%), GitHub Actions CI/CD

---

## 🏃 Запуск макета в FigCraft

1. Запустите FigCraft daemon на локальном порту 9897.
2. Откройте файл проекта:
   ```bash
   open Legal_AI_Analyst.figcraft
   ```
3. Все экраны (светлая тема, тёмная тема и мобильная версия) доступны для интерактивного тестирования.
