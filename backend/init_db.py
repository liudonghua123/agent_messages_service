#!/usr/bin/env python3
"""
Initialize database with sample data
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal, Chat, engine, Base

def create_sample_data():
    """Create sample chat data for testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Chat).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} records. Adding more sample data...")
        
        print("Creating sample data...")
        
        users = ["alice", "bob", "charlie", "diana", "eve"]
        sessions = ["session_001", "session_002", "session_003", "session_004", "session_005"]
        
        questions = [
            "什么是人工智能？",
            "如何学习Python编程？",
            "请解释机器学习的基本概念",
            "Vue.js和React有什么区别？",
            "如何优化数据库查询性能？",
            "什么是微服务架构？",
            "如何进行单元测试？",
            "请介绍一下Docker的使用",
            "什么是RESTful API？",
            "如何保证系统安全性？"
        ]
        
        answers = [
            "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统...",
            "学习Python编程可以从基础语法开始，然后逐步学习数据结构、算法、面向对象编程等概念...",
            "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进...",
            "Vue.js和React都是流行的前端框架，但它们在设计理念和使用方式上有所不同...",
            "数据库查询性能优化可以通过多种方式实现，包括索引优化、查询语句优化、数据库结构优化等...",
            "微服务架构是一种将单一应用程序开发为一套小服务的方法，每个服务运行在自己的进程中...",
            "单元测试是软件开发中的重要实践，它涉及测试代码的最小可测试部分...",
            "Docker是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个轻量级、可移植的容器中...",
            "RESTful API是一种基于REST架构风格的Web API设计方法，它使用HTTP协议的标准方法...",
            "系统安全性可以通过多层防护来保证，包括身份认证、授权控制、数据加密、网络安全等措施..."
        ]
        
        # Create sample chats
        for i in range(50):
            chat = Chat(
                session=random.choice(sessions),
                question=random.choice(questions),
                answer=random.choice(answers),
                datetime=datetime.now() - timedelta(days=random.randint(0, 30), 
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59)),
                user=random.choice(users),
                fullfill=random.choice([True, False]),
                process_time=random.randint(500, 3000)
            )
            db.add(chat)
        
        db.commit()
        print(f"Successfully created {50} sample chat records!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create sample data
    create_sample_data()
    
    print("Database initialization completed!")