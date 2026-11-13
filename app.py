import json
import streamlit as st
from google import genai
from pydantic import BaseModel
import database as db

db.init_db()

st.set_page_config(page_title="Smart Task Manager", page_icon="✅")
st.title("✅ Smart AI Task Manager")

class TaskItem(BaseModel):
    title: str
    priority: str

class TaskList(BaseModel):
    tasks: list[TaskItem]

with st.sidebar:
    st.header("✨ AI Task Generator")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    goal_input = st.text_area("Paste a messy note or big goal:", placeholder="e.g., Prepare for next week's hackathon")
    
    if st.button("Generate Subtasks"):
        if not api_key:
            st.error("Please enter an API key first.")
        elif goal_input:
            with st.spinner("Breaking down your goal..."):
                client = genai.Client(api_key=api_key)
                prompt = f"Break this goal into 3 to 5 clear, actionable tasks with priority (High, Medium, or Low): {goal_input}"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": TaskList,
                    },
                )
                result = json.loads(response.text)
                for item in result["tasks"]:
                    db.add_task(item["title"], item["priority"])
                st.success("Tasks added!")
                st.rerun()

st.subheader("Add a Task Manually")
col1, col2, col3 = st.columns([3, 1.5, 1])
with col1:
    new_title = st.text_input("Task description", label_visibility="collapsed", placeholder="Enter a new task...")
with col2:
    new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], label_visibility="collapsed")
with col3:
    if st.button("Add", use_container_width=True) and new_title:
        db.add_task(new_title, new_priority)
        st.rerun()

st.divider()

st.subheader("Your Tasks")
tasks = db.get_tasks()

if not tasks:
    st.info("No tasks yet. Add one above or open the top-left arrow (>) for the AI generator!")
else:
    for task_id, title, priority, completed in tasks:
        c1, c2, c3, c4 = st.columns([0.5, 4, 1.5, 1])
        with c1:
            is_checked = st.checkbox("", value=bool(completed), key=f"check_{task_id}")
            if is_checked != bool(completed):
                db.toggle_task(task_id, completed)
                st.rerun()
        with c2:
            if completed:
                st.markdown(f"~~{title}~~")
            else:
                st.markdown(f"**{title}**")
        with c3:
            badge_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
            st.write(f"{badge_color} {priority}")
        with c4:
            if st.button("🗑️", key=f"del_{task_id}"):
                db.delete_task(task_id)
                st.rerun()
