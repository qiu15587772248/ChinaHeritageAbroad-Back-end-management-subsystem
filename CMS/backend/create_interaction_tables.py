import pymysql
import traceback

print("="*60)
print("用户互动相关表 (评论、收藏) 创建脚本")
print("="*60)

# 数据库连接参数 (与 create_mobile_users.py 中的一致)
DB_CONFIG = {
    'host': '39.105.26.212',
    'port': 3306,
    'user': 'museumdb',
    'password': '123456',
    'database': 'museumdb',
    'charset': 'utf8mb4'
}

# 创建 comments 表的 SQL 语句
CREATE_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `artifact_id` int(11) NOT NULL,
  `comment` TEXT NOT NULL,
  `comment_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `passed` BOOL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_COMMENTS_INDEX_USER_ARTIFACT = "CREATE INDEX IF NOT EXISTS idx_comments_user_artifact ON `comments` (`user_id`, `artifact_id`);"
CREATE_COMMENTS_INDEX_ARTIFACT = "CREATE INDEX IF NOT EXISTS idx_comments_artifact ON `comments` (`artifact_id`);"

# 创建 loves 表的 SQL 语句
CREATE_LOVES_TABLE = """
CREATE TABLE IF NOT EXISTS `loves` (
  `user_id` int(11) NOT NULL,
  `artifact_id` int(11) NOT NULL,
  `love_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`artifact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_LOVES_INDEX_ARTIFACT = "CREATE INDEX IF NOT EXISTS idx_loves_artifact ON `loves` (`artifact_id`);"

TABLES_TO_CREATE = [
    {
        "name": "comments",
        "create_sql": CREATE_COMMENTS_TABLE,
        "indices": [
            {"name": "idx_comments_user_artifact", "sql": CREATE_COMMENTS_INDEX_USER_ARTIFACT, "fallback_sql": "CREATE INDEX idx_comments_user_artifact ON `comments` (`user_id`, `artifact_id`);"},
            {"name": "idx_comments_artifact", "sql": CREATE_COMMENTS_INDEX_ARTIFACT, "fallback_sql": "CREATE INDEX idx_comments_artifact ON `comments` (`artifact_id`);"}
        ]
    },
    {
        "name": "loves",
        "create_sql": CREATE_LOVES_TABLE,
        "indices": [
            {"name": "idx_loves_artifact", "sql": CREATE_LOVES_INDEX_ARTIFACT, "fallback_sql": "CREATE INDEX idx_loves_artifact ON `loves` (`artifact_id`);"}
        ]
    }
]

def execute_sql_with_fallback(cursor, sql_if_not_exists, sql_no_check, index_name):
    try:
        print(f"    正在创建索引 {index_name} (IF NOT EXISTS)...")
        cursor.execute(sql_if_not_exists)
        print(f"    ✓ 索引 {index_name} 创建成功 (或已存在)!")
    except Exception as e:
        print(f"    ! 索引 {index_name} 使用 IF NOT EXISTS 创建失败: {e}")
        print(f"      尝试不带 IF NOT EXISTS 重新创建索引 {index_name}...")
        try:
            cursor.execute(sql_no_check)
            print(f"    ✓ 索引 {index_name} 创建成功!")
        except Exception as e_fallback:
            if "Duplicate key name" in str(e_fallback) or "already exists" in str(e_fallback).lower():
                print(f"    ! 索引 {index_name} 已存在，跳过创建")
            else:
                print(f"    × 创建索引 {index_name} 时出错: {e_fallback}")

try:
    print(f"正在连接到MySQL服务器...")
    print(f"主机: {DB_CONFIG['host']}")
    # ... (可以添加更多连接信息打印)
    
    conn = pymysql.connect(**DB_CONFIG)
    print("✓ 数据库连接成功!")
    cursor = conn.cursor()

    for table_info in TABLES_TO_CREATE:
        table_name = table_info["name"]
        print("\n" + "-"*20 + f" 处理表: {table_name} " + "-"*20)

        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if cursor.fetchone():
            print(f"! 表 '{table_name}' 已存在")
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            print(f"\n表 '{table_name}' 的现有结构:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            
            recreate = input(f"\n是否删除现有表 '{table_name}' 并重新创建? (y/n): ")
            if recreate.lower() == 'y':
                print(f"\n正在删除现有表 '{table_name}'...")
                cursor.execute(f"DROP TABLE `{table_name}`")
                print(f"✓ 现有表 '{table_name}' 已删除")
            else:
                print(f"\n保留现有表 '{table_name}'，跳过创建和索引操作。")
                continue # 跳到下一个表
        
        # 创建表
        print(f"\n正在创建表 '{table_name}'...")
        cursor.execute(table_info["create_sql"])
        print(f"✓ 表 '{table_name}' 创建成功!")
        
        # 创建索引
        if table_info["indices"]:
            print(f"\n  正在为表 '{table_name}' 创建索引...")
            for index_info in table_info["indices"]:
                execute_sql_with_fallback(cursor, index_info["sql"], index_info["fallback_sql"], index_info["name"])

        # 验证表创建
        print(f"\n验证表 '{table_name}' 创建...")
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        print(f"\n表 '{table_name}' 的结构:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        print(f"\n✓ 表 '{table_name}' 创建和验证完成!")

    conn.commit()
    
except Exception as e:
    print(f"\n× 操作失败: {e}")
    traceback.print_exc()
finally:
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
        print("\n数据库连接已关闭")

print("\n" + "="*60)
print("脚本结束")
print("="*60) 