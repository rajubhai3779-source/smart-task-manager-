import json
import urllib.request
import streamlit as st
import database as db

db.init_db()

st.set_page_config(page_title="Smart Task Manager", page_icon="✅")
st.title("✅ Smart AI Task Manager")

def generate_ai_tasks(api_key, goal):
    url = f"https://googleapis.com{api_key}"
    prompt = (
        f"Break this goal into 3 to 5 clear, actionable tasks with priority (High, Medium, or Low). "
        f"Return ONLY a valid JSON array of objects, each with 'title' and 'priority' keys. "
        f"Do not include markdown formatting. Goal: {goal}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

with st.sidebar:
    st.header("✨ AI Task Generator")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    goal_input = st.text_area("Paste a messy note or big goal:", placeholder="e.g., Prepare for next week's hackathon")
    
    if st.button("Generate Subtasks"):
        if not api_key:
            st.error("Please enter an API key first.")
        elif goal_input:
            with st.spinner("Breaking down your goal..."):
                try:
                    tasks_list = generate_ai_tasks(api_key, goal_input)
                    for item in tasks_list:
                        db.add_task(item["title"], item.get("priority", "Medium"))
                    st.success("Tasks added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating tasks: {e}")

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
            st.markdown(f"~~{title}~~" if completed else f"**{title}**")
        with c3:
            badge_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
            st.write(f"{badge_color} {priority}")
        with c4:
            if st.button("🗑️", key=f"del_{task_id}"):
                db.delete_task(task_id)
                st.rerun()
                
