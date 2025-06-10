# from app import db # db 仅被 Heritage 模型使用，已被删除
# from datetime import datetime # datetime 仅被 Heritage 模型使用，已被删除

class MetClear:
    """元数据清洗表模型"""
    
    @staticmethod
    def get_all_items(conn):
        """获取所有元数据清洗表项目"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM met_clear")
            return cursor.fetchall()
    
    @staticmethod
    def get_item(conn, item_id):
        """获取特定元数据清洗表项目"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM met_clear WHERE id = %s", (item_id,))
            return cursor.fetchone()
    
    @staticmethod
    def create_item(conn, item_data):
        """创建新的元数据清洗表项目"""
        # 确保字段名被反引号包围以处理特殊字符或关键字
        columns = ", ".join([f"`{key}`" for key in item_data.keys()])
        placeholders = ", ".join(["%s"] * len(item_data))
        values = list(item_data.values())
        
        with conn.cursor() as cursor:
            sql = f"INSERT INTO `met_clear` ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        conn.commit()
        
        # 返回新创建的项目ID
        with conn.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            return cursor.fetchone()[0]
    
    @staticmethod
    def update_item(conn, item_id, item_data):
        """更新元数据清洗表项目"""
        # 确保字段名被反引号包围
        set_clause = ", ".join([f"`{key}` = %s" for key in item_data.keys()])
        values = list(item_data.values())
        values.append(item_id)
        
        with conn.cursor() as cursor:
            sql = f"UPDATE `met_clear` SET {set_clause} WHERE `id` = %s"
            cursor.execute(sql, values)
        conn.commit()
    
    @staticmethod
    def delete_item(conn, item_id):
        """删除元数据清洗表项目"""
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM `met_clear` WHERE `id` = %s", (item_id,))
        conn.commit()
    
    @staticmethod
    def search_items(conn, criteria):
        """根据条件搜索元数据清洗表项目"""
        # 注意：这个搜索实现比较基础，可能需要根据实际字段和需求进行优化
        # 例如，对于多个搜索词，可能需要更复杂的查询逻辑
        sql = "SELECT * FROM `met_clear` WHERE 1=1"
        values = []
        
        # 假设 criteria 是一个字典，如 {'title': 'search_term', 'artist': 'another_term'}
        # 并且我们希望在 met_clear 表中对应的字段中进行模糊匹配
        # 请根据 met_clear 表的实际可搜索字段进行调整
        # 例如，假设有 'title', 'artist', 'period', 'material' 等字段可以搜索
        
        searchable_fields = ['title', 'artist', 'period', 'material', 'dynasty', 'excavation_site', 'dimensions', 'description']

        for field, term in criteria.items():
            if field in searchable_fields and term:
                sql += f" AND `{field}` LIKE %s"
                values.append(f"%{term}%")
            # 如果有更复杂的搜索逻辑（例如，一个关键词搜索多个字段），需要在这里实现
            # elif field == 'keyword' and term: 
            #    keyword_conditions = []
            #    for s_field in ['title', 'artist', 'description']:
            #        keyword_conditions.append(f"`{s_field}` LIKE %s")
            #        values.append(f"%{term}%")
            #    if keyword_conditions:
            #        sql += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(values))
            return cursor.fetchall() 