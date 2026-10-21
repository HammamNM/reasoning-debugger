import json
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. تجهيز قاعدة بيانات وهمية محلياً
db_path = "benchmarks/samples/public_real_trace/test.db"
conn = sqlite3.connect(db_path)
conn.execute("DROP TABLE IF EXISTS users;")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);")
conn.commit()
conn.close()

# 2. إعداد LangChain
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# إنشاء الوكيل مع تفعيل return_intermediate_steps لتسجيل الـ Trace
agent_executor = create_sql_agent(llm, db=db, agent_type="tool-calling", verbose=True, return_intermediate_steps=True)

print("Running LangChain Agent...")
try:
    # نسأل سؤالاً خادعاً لاختبار فشل الاستنتاج
    response = agent_executor.invoke({"input": "How many premium subscribers do we have?"})
    
    # 3. حفظ الـ Trace الخام
    steps = response.get("intermediate_steps", [])
    
    def trace_serializer(obj):
        if hasattr(obj, 'dict'): return obj.dict()
        if hasattr(obj, '__dict__'): return obj.__dict__
        return str(obj)
        
    trace_path = "benchmarks/samples/public_real_trace/langchain_raw_trace.json"
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(steps, f, default=trace_serializer, indent=2)
        
    print(f"\nSUCCESS! Raw trace saved to {trace_path}")
    print(f"Number of steps recorded: {len(steps)}")
    
except Exception as e:
    print(f"Execution Error: {e}")
