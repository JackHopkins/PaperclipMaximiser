import json
import math
import random
from typing import Optional, Dict, Any, List

import psycopg2
import tenacity
from psycopg2.extras import DictCursor
from tenacity import wait_exponential, retry_if_exception_type

from datasetgen.mcts.evaluation_task import EvaluationTask
from datasetgen.mcts.program import Program


class DBClient:
    def __init__(self, **db_config):
        self.db_config = db_config
        self.conn = psycopg2.connect(**db_config)

    def _get_new_connection(self):
        """Create a new database connection"""
        return psycopg2.connect(**self.db_config)

    async def create_program(self, program: Program) -> Program:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO programs (code, value, visits, parent_id, state_json, conversation_json, completion_token_usage, prompt_token_usage, token_usage, response, holdout_value, raw_reward, version, version_description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                      program.version_description
                      ))

                id, created_at = cur.fetchone()
                self.conn.commit()
                program.id = id
                program.created_at = created_at
                return program
        except Exception as e:
            print(e)
            raise e


    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_all_program_rewards(self, version: int = None) -> List[float]:
        """Get all program rewards for a given version."""
        query = """
            SELECT value 
            FROM programs 
            WHERE value IS NOT NULL
        """

        if version is not None:
            query += f" AND version = {version}"


        try:
            with self.conn.cursor() as cur:
                cur.execute(query.strip())
                results = cur.fetchall()
                return [row[0] for row in results]
        except Exception as e:
            print(f"Error fetching program rewards: {e}")
            return []

    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def sample_parent(self, version=1) -> Optional[Program]:
        """
        Sample parent using a separate connection and transaction to avoid blocking.
        Each MCTS group can call this independently without serialization.
        """
        # Create a new connection for this sampling operation
        with self._get_new_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # First get recent programs
                cur.execute("""
                        WITH recent AS (
                            SELECT id, value
                            FROM programs
                            WHERE version = %s AND value IS NOT NULL
                            ORDER BY created_at DESC
                            LIMIT 100
                        )
                        SELECT id, value 
                        FROM recent
                    """, (version,))

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
                    # If all weights are 0, use uniform distribution
                    sampled_id = random.choice([w[0] for w in weights])
                else:
                    # Sample using normalized weights
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

    @tenacity.retry(retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
                    wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_parent_visit_stats(self, version: int = None) -> Dict[str, float]:
        """Get statistics about parent visit counts"""
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
            query += f" AND version = {version}"

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
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
        with self.conn.cursor() as cur:
            set_clauses = [f"{k} = %s" for k in updates.keys()]
            values = list(updates.values())

            cur.execute(f"""
                UPDATE programs
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
            """, values + [program_id])

            self.conn.commit()
            row = cur.fetchone()
            return Program.from_row(dict(zip([desc[0] for desc in cur.description], row)))

    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> EvaluationTask:
        with self.conn.cursor() as cur:
            set_clauses = [f"{k} = %s" for k in updates.keys()]
            values = list(updates.values())

            cur.execute(f"""
                UPDATE evaluation_queue
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
            """, values + [task_id])

            self.conn.commit()
            return EvaluationTask.parse_obj(cur.fetchone())