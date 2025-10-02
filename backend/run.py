"""
应用启动脚本
"""

import os
import sys
import uvicorn

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings

if __name__ == "__main__":
    # 启动FastAPI应用
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        workers=1 if settings.reload else 4,
        access_log=True,
        use_colors=True
    )
