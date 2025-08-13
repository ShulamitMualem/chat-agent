# Gemini Agent with MCP Tools

זהו agent חכם שמשתמש ב-Gemini AI כדי לעבוד עם MCP (Model Context Protocol) tools. ה-agent יכול לקבל שאלות מהמשתמש, להחליט איזה tools להשתמש בהם, ולהחזיר תשובות מדויקות.

## תכונות עיקריות

1. **זיהוי אוטומטי של צורך ב-tools** - ה-agent מנתח את השאלה ומחליט האם צריך להשתמש ב-tool
2. **הפעלת tools עם פרמטרים נכונים** - ה-agent מפעיל את ה-tools עם הפרמטרים המתאימים
3. **עיבוד תוצאות** - ה-agent מעבד את התוצאות ומחזיר תשובה ברורה למשתמש
4. **תמיכה ב-MCP Protocol** - עובד עם כל MCP server שמספק tools

## התקנה

1. התקן את התלויות:
```bash
pip install google-generativeai python-dotenv mcp
```

2. צור קובץ `.env` עם המפתחות הנדרשים:
```env
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=your_google_api_key_here
AI_SERVICE=gemini
```

## שימוש

### הרצת ה-agent הראשי:
```bash
python main.py
```

### בדיקת ה-agent:
```bash
python test_gemini_agent.py
```

## איך זה עובד

### 1. זיהוי צורך ב-tool
כאשר המשתמש שואל שאלה, ה-agent:
- מנתח את השאלה
- בודק איזה tools זמינים
- מחליט האם צריך להשתמש ב-tool

### 2. הפעלת tool
אם ה-agent מחליט להשתמש ב-tool:
- הוא מפעיל את ה-tool עם הפרמטרים הנכונים
- מקבל את התוצאה
- מעבד את התוצאה לתשובה ברורה

### 3. דוגמאות לשימוש

**שאלה פשוטה:**
```
User: "Hello, how are you?"
Agent: "Hello! I'm doing well, thank you for asking. How can I help you today?"
```

**שאלה שדורשת tool:**
```
User: "What's in the deposition document?"
Agent: TOOL_CALL: {"tool_name": "read_doc_contents", "parameters": {"doc_id": "deposition.md"}}
```

**תשובה עם תוצאות tool:**
```
I used the read_doc_contents tool to help answer your question. Here's what I found:

This deposition covers the testimony of Angela Smith, P.E.

Based on this information, here's my answer to your question:
The deposition document contains the testimony of Angela Smith, who is a Professional Engineer (P.E.).
```

## Tools זמינים

כרגע ה-MCP server מספק את ה-tools הבאים:

1. **read_doc_contents** - קורא תוכן של מסמך
   - פרמטרים: `doc_id` (מזהה המסמך)

2. **edit_document** - עורך מסמך
   - פרמטרים: `doc_id`, `old_str`, `new_str`

## מסמכים זמינים

- `deposition.md` - עדות של Angela Smith, P.E.
- `report.pdf` - דוח על מצב מגדל קירור של 20 מטר
- `financials.docx` - נתונים פיננסיים של הפרויקט
- `outlook.pdf` - תחזית ביצועים עתידיים
- `plan.md` - תוכנית יישום הפרויקט
- `spec.txt` - מפרטים טכניים

## הרחבה

כדי להוסיף tools חדשים:

1. הוסף את ה-tool ל-`mcp_server.py`
2. ה-agent יזהה אותו אוטומטית
3. ה-agent יוכל להשתמש בו לפי הצורך

## פתרון בעיות

### שגיאות נפוצות:

1. **API Key לא מוגדר** - ודא שה-`GOOGLE_API_KEY` מוגדר ב-.env
2. **Model לא מוגדר** - ודא שה-`GEMINI_MODEL` מוגדר נכון
3. **MCP Server לא זמין** - ודא שה-MCP server רץ

### Debug:
הפעל עם משתנה סביבה `DEBUG=1` כדי לראות הודעות debug מפורטות.

## מבנה הקוד

- `core/gemini.py` - הקלאס הראשי של Gemini Agent
- `mcp_server.py` - MCP Server עם tools
- `mcp_client.py` - MCP Client לתקשורת
- `cli_chat.py` - ממשק שורת פקודה
- `test_gemini_agent.py` - קובץ בדיקה
