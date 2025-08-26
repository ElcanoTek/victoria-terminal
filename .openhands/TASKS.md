# Task List

1. ✅ Explore current victoria.py and tests to understand constraints
Reviewed functions, tests expect detect_terminal_capabilities and get_terminal_width. Verified non-interactive behavior and banner text requirements.
2. ✅ Design minimal, maintainable box/UI system (BoxStyle + helpers)
Added BoxStyle NamedTuple and UI helper with hr and box. Centralizes border logic.
3. ✅ Refactor section_header, prompt_update_victoria, and course_menu to use new helpers
Refactored section_header and course_menu. prompt_update_victoria now uses UI.box for options.
4. ✅ Simplify banner for minimalist elegance while preserving 'VICTORIA' and 'ADTECH'
Rewrote banner to use UI.box; removed heavy ASCII art; added status box.
5. ✅ Run provided tests to ensure compatibility
Ran pytest; 10 tests passed.
6. 🔄 Commit changes with clear message
Prepare to commit.

