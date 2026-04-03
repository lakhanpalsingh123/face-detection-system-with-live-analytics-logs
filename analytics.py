from db import get_db_connection

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT details) FROM logs WHERE action='detection'")
    unique = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(confidence) FROM logs WHERE confidence > 0")
    avg_conf = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "total": total,
        "unique": unique,
        "avg_confidence": round(avg_conf * 100, 2)
    }

def get_all_logs():
    from db import get_logs
    return get_logs()