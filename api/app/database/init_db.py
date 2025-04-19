from ..database import engine
from ..models.script import Script
from ..models.analysis import ScriptAnalysis

def init_db():
    """
    初始化数据库表
    如果表已存在，不会重新创建
    """
    # 创建所有模型对应的表
    Script.__table__.create(engine, checkfirst=True)
    ScriptAnalysis.__table__.create(engine, checkfirst=True)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully") 