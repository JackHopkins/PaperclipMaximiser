import json
import math
import random
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

import psycopg2
import tenacity
from psycopg2.extras import DictCursor
from tenacity import wait_exponential, retry_if_exception_type
from datasetgen.mcts.program import Program


class DBClient:
    def __init__(self, max_conversation_length: int = 20, **db_config):
        self.db_config = db_config
        self.max_conversation_length = max_conversation_length
        # Don't store connection as instance variable
        # Instead create connection pool
        self.pool = []
        self.max_pool_size = 5

    @contextmanager
    def get_connection(self):
        """Context manager to handle database connections"""
        conn = None
        try:
            # Try to get connection from pool
            if self.pool:
                conn = self.pool.pop()
                try:
                    # Test if connection is still alive
                    conn.cursor().execute('SELECT 1')
                except (psycopg2.OperationalError, psycopg2.InterfaceError):
                    # If connection is dead, close it and create new one
                    conn.close()
                    conn = None

            # If no connection from pool, create new one
            if conn is None:
                conn = psycopg2.connect(**self.db_config)

            yield conn

            # If connection still good, return to pool
            try:
                conn.cursor().execute('SELECT 1')
                if len(self.pool) < self.max_pool_size:
                    self.pool.append(conn)
                else:
                    conn.close()
            except:
                conn.close()

        except Exception as e:
            if conn:
                conn.close()
            raise e

    @tenacity.retry(
        retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.DatabaseError)),
        wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_program(self, program: Program) -> Program:
        """Create a new program, now with connection management"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO programs (code, value, visits, parent_id, state_json, conversation_json, 
                                           completion_token_usage, prompt_token_usage, token_usage, response, 
                                           holdout_value, raw_reward, version, version_description, model, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, created_at
                    """, (program.code, program.value, 0, program.parent_id,
                          program.state.to_raw() if program.state else None,
                          json.dumps(program.conversation.dict()),
                          program.completion_token_usage,
                          program.prompt_token_usage,
                          program.token_usage,
                          program.response,
                          program.holdout_value,
                          program.raw_reward,
                          program.version,
                          program.version_description,
                          program.model,
                          json.dumps(program.meta)
                          ))

                    id, created_at = cur.fetchone()
                    conn.commit()
                    program.id = id
                    program.created_at = created_at
                    return program
        except Exception as e:
            print(f"Error creating program: {e}")
            raise e

    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_all_program_rewards(self, version: int = None) -> List[float]:
        """Get all program rewards with proper connection management"""
        query = """
            SELECT value 
            FROM programs 
            WHERE value IS NOT NULL
        """
        if version is not None:
            query += " AND version = %s"

        params = (version,) if version is not None else ()

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query.strip(), params)
                    results = cur.fetchall()
                    return [row[0] for row in results]
        except Exception as e:
            print(f"Error fetching program rewards: {e}")
            return []

    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def sample_parent(self, version=1) -> Optional[Program]:
        """Sample parent with proper connection management"""
        max_assistant_length = (self.max_conversation_length * 2) + 1

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        WITH recent AS (
                            SELECT id, value, conversation_json
                            FROM programs
                            WHERE version = %s 
                            AND value IS NOT NULL
                            AND jsonb_array_length(conversation_json->'messages') < %s
                            ORDER BY created_at DESC
                            LIMIT 300
                        )
                        SELECT id, value 
                        FROM recent
                        """, (version, max_assistant_length))

                    results = cur.fetchall()
                    if not results:
                        return None

                    # Calculate softmax weights
                    max_value = max(row['value'] for row in results)
                    weights = [
                        (row['id'],
                         math.exp(row['value'] - max_value))
                        for row in results
                    ]

                    # Normalize weights
                    total_weight = sum(w[1] for w in weights)
                    if total_weight == 0:
                        sampled_id = random.choice([w[0] for w in weights])
                    else:
                        normalized_weights = [(id, w / total_weight) for id, w in weights]
                        sampled_id = random.choices(
                            [id for id, _ in normalized_weights],
                            weights=[w for _, w in normalized_weights],
                            k=1
                        )[0]

                    # Fetch the selected program
                    cur.execute("""
                        SELECT * FROM programs WHERE id = %s
                        """, (sampled_id,))

                    row = cur.fetchone()
                    return Program.from_row(dict(row)) if row else None
        except Exception as e:
            print(f"Error sampling parent: {e}")
            raise e
    

    def get_programs(self, limit = None, version = None):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                sql_query = "SELECT value, code, conversation_json, response, meta, version, id, parent_id, holdout_value FROM programs"
                if version:
                    sql_query += f" WHERE version = {version}"
                if limit:
                    sql_query += f" LIMIT {limit}"
                cur.execute(sql_query)
                results = cur.fetchall()
                output_dicts = []
                for row in results:
                    output_dicts.append({
                        'reward': row[0] if row[0] is not None else 0,
                        'code': row[1],
                        'conversation': row[2],
                        'response': row[3] if row[3] is not None else "",
                        'meta': row[4],
                        'version': row[5],
                        "id": row[6],
                        "parent_id": row[7],
                        "holdout_value": row[8] if row[8] is not None else 0
                    })
                return output_dicts
        
    
    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_parent_visit_stats(self, version: int = None) -> Dict[str, float]:
        """Get visit statistics with proper connection management"""
        query = """
            SELECT 
                AVG(visits) as avg_visits,
                MIN(visits) as min_visits,
                MAX(visits) as max_visits,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY visits) as median_visits
            FROM programs 
            WHERE visits > 0
        """
        if version is not None:
            query += " AND version = %s"

        params = (version,) if version is not None else ()

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    result = cur.fetchone()
                    return {
                        'avg_visits': result[0],
                        'min_visits': result[1],
                        'max_visits': result[2],
                        'median_visits': result[3]
                    }
        except Exception as e:
            print(f"Error fetching visit statistics: {e}")
            return {}

    async def update_program(self, program_id: int, updates: Dict[str, Any]) -> Program:
        """Update program with proper connection management"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    set_clauses = [f"{k} = %s" for k in updates.keys()]
                    values = list(updates.values())

                    cur.execute(f"""
                        UPDATE programs
                        SET {', '.join(set_clauses)}
                        WHERE id = %s
                        RETURNING *
                    """, values + [program_id])

                    conn.commit()
                    row = cur.fetchone()
                    return Program.from_row(dict(zip([desc[0] for desc in cur.description], row)))
        except Exception as e:
            print(f"Error updating program: {e}")
            raise e
